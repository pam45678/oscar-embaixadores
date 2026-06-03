"""
Camada de banco de dados.
- Em PRODUÇÃO (Render): usa Postgres se a variável de ambiente DATABASE_URL existir.
  Os dados ficam num banco externo (Neon) e NUNCA somem, mesmo que o Render
  reinicie ou durma.
- Em DESENVOLVIMENTO (sua máquina): se não houver DATABASE_URL, cai pra SQLite
  local (clube.db) — útil só pra testar.

Tudo no app usa as funções daqui, com "?" como placeholder. Quando estamos no
Postgres, traduzimos "?" pra "%s" automaticamente.
"""
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
USE_PG = bool(DATABASE_URL)

if USE_PG:
    import psycopg
    from psycopg.rows import dict_row
else:
    import sqlite3

# Caminho do SQLite local (fallback de desenvolvimento)
SQLITE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "clube.db"
)


def _translate(query):
    """Postgres usa %s como placeholder; nosso código usa ?."""
    if USE_PG:
        return query.replace("?", "%s")
    return query


class _Cursor:
    """Cursor unificado — mesma interface pra Postgres e SQLite."""

    def __init__(self, raw):
        self._raw = raw

    def execute(self, query, params=()):
        self._raw.execute(_translate(query), params)
        return self

    def fetchone(self):
        return self._raw.fetchone()

    def fetchall(self):
        return self._raw.fetchall()

    @property
    def lastrowid(self):
        return getattr(self._raw, "lastrowid", None)


class Connection:
    """Conexão unificada com .execute / .commit / .close."""

    def __init__(self):
        if USE_PG:
            self._conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        else:
            self._conn = sqlite3.connect(SQLITE_PATH)
            self._conn.row_factory = sqlite3.Row

    def execute(self, query, params=()):
        cur = self._conn.cursor()
        cur.execute(_translate(query), params)
        return _Cursor(cur)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def connect():
    return Connection()


# ---------------------------------------------------------------------------
# Tipos de coluna que mudam entre os dois bancos
# ---------------------------------------------------------------------------
if USE_PG:
    PK = "SERIAL PRIMARY KEY"
else:
    PK = "INTEGER PRIMARY KEY AUTOINCREMENT"


def init_db():
    """Cria as tabelas se ainda não existirem (idempotente)."""
    conn = connect()
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS desbravadores (
            id {PK},
            nome TEXT NOT NULL,
            unidade TEXT NOT NULL,
            pontuacao_total INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS historico_pontos (
            id {PK},
            desbravador_id INTEGER NOT NULL,
            pontos INTEGER NOT NULL,
            motivo TEXT NOT NULL,
            data TEXT NOT NULL
        )
        """
    )
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS recados (
            id {PK},
            tipo TEXT NOT NULL,
            texto TEXT NOT NULL,
            autor TEXT,
            data TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()
