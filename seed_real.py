"""
Seed REAL — roda UMA vez no deploy do Render.
- Zera desbravadores fictícios e o histórico de pontos.
- Insere a lista oficial de integrantes (todos com 0 pontos).
- Usa uma marca em 'meta' para nunca rodar duas vezes (idempotente).
"""
import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), "clube.db")

# (nome, unidade)
INTEGRANTES = [
    # SEDA AZUL
    ("Larissa", "Seda Azul"),
    ("Júlia", "Seda Azul"),
    ("Leandra", "Seda Azul"),
    ("Emily Luma", "Seda Azul"),
    ("Lavígnia", "Seda Azul"),
    ("Beatriz (Bia)", "Seda Azul"),
    ("Helena", "Seda Azul"),
    ("Emilly Alves", "Seda Azul"),
    ("Sophia", "Seda Azul"),
    # LOBO
    ("Felipe (Lipe)", "Lobo"),
    ("Bernardo", "Lobo"),
    ("Mohammed", "Lobo"),
    ("Yuri", "Lobo"),
    ("Pedro Richard", "Lobo"),
    ("Davi", "Lobo"),
    ("João Vitor", "Lobo"),
    # GUEPARDO
    ("Lucas", "Guepardo"),
    # MONARCA (diretoria)
    ("Pâmela", "Monarca"),
    ("Camila", "Monarca"),
    ("Ágata", "Monarca"),
    ("Érica", "Monarca"),
    # GORILA (diretoria)
    ("João Pedro", "Gorila"),
    ("Felipi", "Gorila"),
    ("Anderson Cunha", "Gorila"),
    ("Anderson Gomes", "Gorila"),
    ("Murilo", "Gorila"),
    ("Márcio", "Gorila"),
    ("Fabiano", "Gorila"),
]

MARK = "seed_real_v1"


def main():
    db = sqlite3.connect(DB)
    db.execute(
        "CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT)"
    )
    # Garante tabelas principais (caso rode antes do app)
    db.execute(
        """CREATE TABLE IF NOT EXISTS desbravadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            unidade TEXT NOT NULL,
            pontuacao_total INTEGER NOT NULL DEFAULT 0
        )"""
    )
    db.execute(
        """CREATE TABLE IF NOT EXISTS historico_pontos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            desbravador_id INTEGER,
            pontos INTEGER,
            motivo TEXT,
            data TEXT
        )"""
    )

    ja_rodou = db.execute(
        "SELECT 1 FROM meta WHERE chave = ?", (MARK,)
    ).fetchone()
    if ja_rodou:
        print("seed_real: já executado anteriormente. Nada a fazer.")
        db.close()
        return

    # Limpa fictícios e histórico
    db.execute("DELETE FROM historico_pontos")
    db.execute("DELETE FROM desbravadores")

    # Insere a lista oficial com 0 pontos
    db.executemany(
        "INSERT INTO desbravadores (nome, unidade, pontuacao_total) "
        "VALUES (?, ?, 0)",
        INTEGRANTES,
    )

    db.execute(
        "INSERT INTO meta (chave, valor) VALUES (?, '1')", (MARK,)
    )
    db.commit()
    print(f"seed_real: {len(INTEGRANTES)} integrantes inseridos (0 pontos).")
    db.close()


if __name__ == "__main__":
    main()
