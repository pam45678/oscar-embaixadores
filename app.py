import sqlite3
import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)

# ----------------------------------------------------------------------------
# CONFIGURAÇÃO
# ----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "embaixadores-sertaozinho-oscar-2026"

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clube.db")

# Senha do painel administrativo (hardcoded conforme solicitado)
ADMIN_PASSWORD = "1986"

# Informações do clube
CLUBE = {
    "nome": "Embaixadores de Sertãozinho",
    "associacao": "APO — Associação Paulista Oeste",
}

# Unidades que ENTRAM no ranking público (somente desbravadores)
UNIDADES_DESBRAVADORES = ["Lobo", "Guepardo", "Seda Azul"]


# ----------------------------------------------------------------------------
# BANCO DE DADOS (SQLite)
# ----------------------------------------------------------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS desbravadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            unidade TEXT NOT NULL,
            pontuacao_total INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_pontos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            desbravador_id INTEGER NOT NULL,
            pontos INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (desbravador_id) REFERENCES desbravadores (id)
        )
        """
    )
    conn.commit()
    conn.close()


# Cria as tabelas assim que o app é importado (gunicorn no Render, etc.)
init_db()


# ----------------------------------------------------------------------------
# AUTENTICAÇÃO SIMPLES
# ----------------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("admin"))
        return view(*args, **kwargs)
    return wrapped


# ----------------------------------------------------------------------------
# ROTA PÚBLICA — LEADERBOARD
# ----------------------------------------------------------------------------
@app.route("/")
def index():
    db = get_db()
    filtro = request.args.get("unidade", "Todas")

    placeholders = ",".join("?" for _ in UNIDADES_DESBRAVADORES)
    params = list(UNIDADES_DESBRAVADORES)
    query = (
        f"SELECT * FROM desbravadores WHERE unidade IN ({placeholders})"
    )

    if filtro != "Todas" and filtro in UNIDADES_DESBRAVADORES:
        query += " AND unidade = ?"
        params.append(filtro)

    query += " ORDER BY pontuacao_total DESC, nome ASC"
    desbravadores = db.execute(query, params).fetchall()

    # Estatísticas para os cards do topo
    total_part = db.execute(
        f"SELECT COUNT(*) c FROM desbravadores WHERE unidade IN ({placeholders})",
        UNIDADES_DESBRAVADORES,
    ).fetchone()["c"]
    total_pts = db.execute(
        f"SELECT COALESCE(SUM(pontuacao_total),0) s FROM desbravadores WHERE unidade IN ({placeholders})",
        UNIDADES_DESBRAVADORES,
    ).fetchone()["s"]

    return render_template(
        "index.html",
        clube=CLUBE,
        desbravadores=desbravadores,
        unidades=UNIDADES_DESBRAVADORES,
        filtro=filtro,
        total_part=total_part,
        total_pts=total_pts,
    )


# ----------------------------------------------------------------------------
# ROTA PRIVADA — PAINEL ADMIN
# ----------------------------------------------------------------------------
@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Login
    if request.method == "POST" and "senha" in request.form:
        if request.form.get("senha") == ADMIN_PASSWORD:
            session["logado"] = True
            return redirect(url_for("painel"))
        flash("Senha incorreta. Tente novamente.", "erro")
        return redirect(url_for("admin"))

    if session.get("logado"):
        return redirect(url_for("painel"))

    return render_template("login.html", clube=CLUBE)


@app.route("/admin/painel")
@login_required
def painel():
    db = get_db()
    placeholders = ",".join("?" for _ in UNIDADES_DESBRAVADORES)
    desbravadores = db.execute(
        f"SELECT * FROM desbravadores WHERE unidade IN ({placeholders}) "
        "ORDER BY nome ASC",
        UNIDADES_DESBRAVADORES,
    ).fetchall()

    historico = db.execute(
        """
        SELECT h.pontos, h.motivo, h.data, d.nome, d.unidade
        FROM historico_pontos h
        JOIN desbravadores d ON d.id = h.desbravador_id
        ORDER BY h.id DESC LIMIT 15
        """
    ).fetchall()

    return render_template(
        "admin.html",
        clube=CLUBE,
        desbravadores=desbravadores,
        unidades=UNIDADES_DESBRAVADORES,
        historico=historico,
    )


@app.route("/admin/cadastrar", methods=["POST"])
@login_required
def cadastrar():
    nome = request.form.get("nome", "").strip()
    unidade = request.form.get("unidade", "").strip()

    if not nome or unidade not in UNIDADES_DESBRAVADORES:
        flash("Preencha nome e selecione uma unidade válida.", "erro")
        return redirect(url_for("painel"))

    db = get_db()
    db.execute(
        "INSERT INTO desbravadores (nome, unidade, pontuacao_total) VALUES (?, ?, 0)",
        (nome, unidade),
    )
    db.commit()
    flash(f"Desbravador '{nome}' cadastrado na unidade {unidade}!", "ok")
    return redirect(url_for("painel"))


@app.route("/admin/lancar", methods=["POST"])
@login_required
def lancar():
    try:
        desbravador_id = int(request.form.get("desbravador_id"))
        pontos = int(request.form.get("pontos"))
    except (TypeError, ValueError):
        flash("Selecione um desbravador e informe pontos válidos.", "erro")
        return redirect(url_for("painel"))

    motivo = request.form.get("motivo", "").strip()
    if not motivo:
        flash("Informe o motivo da pontuação.", "erro")
        return redirect(url_for("painel"))

    db = get_db()
    desb = db.execute(
        "SELECT * FROM desbravadores WHERE id = ?", (desbravador_id,)
    ).fetchone()
    if not desb:
        flash("Desbravador não encontrado.", "erro")
        return redirect(url_for("painel"))

    # Soma automática na pontuação total + registro do histórico
    db.execute(
        "UPDATE desbravadores SET pontuacao_total = pontuacao_total + ? WHERE id = ?",
        (pontos, desbravador_id),
    )
    db.execute(
        "INSERT INTO historico_pontos (desbravador_id, pontos, motivo, data) "
        "VALUES (?, ?, ?, ?)",
        (desbravador_id, pontos, motivo, datetime.now().strftime("%d/%m/%Y %H:%M")),
    )
    db.commit()
    flash(f"{pontos:+d} pts lançados para {desb['nome']} ({motivo}).", "ok")
    return redirect(url_for("painel"))


@app.route("/admin/excluir/<int:desbravador_id>", methods=["POST"])
@login_required
def excluir(desbravador_id):
    db = get_db()
    desb = db.execute(
        "SELECT * FROM desbravadores WHERE id = ?", (desbravador_id,)
    ).fetchone()
    if not desb:
        flash("Desbravador não encontrado.", "erro")
        return redirect(url_for("painel"))

    nome = desb["nome"]
    db.execute("DELETE FROM historico_pontos WHERE desbravador_id = ?", (desbravador_id,))
    db.execute("DELETE FROM desbravadores WHERE id = ?", (desbravador_id,))
    db.commit()
    flash(f"Desbravador '{nome}' excluído.", "ok")
    return redirect(url_for("painel"))


@app.route("/admin/limpar-tudo", methods=["POST"])
@login_required
def limpar_tudo():
    # Só executa se a confirmação for digitada corretamente
    if request.form.get("confirmar", "").strip().upper() != "LIMPAR":
        flash("Para limpar tudo, digite LIMPAR na confirmação.", "erro")
        return redirect(url_for("painel"))
    db = get_db()
    db.execute("DELETE FROM historico_pontos")
    db.execute("DELETE FROM desbravadores")
    db.commit()
    flash("Todos os desbravadores e pontos foram removidos. Comece do zero!", "ok")
    return redirect(url_for("painel"))


@app.route("/admin/sair")
def sair():
    session.clear()
    return redirect(url_for("index"))


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
