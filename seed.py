"""Popula o banco com dados de exemplo. Rode: python seed.py"""
import sqlite3, os, random
from datetime import datetime
from app import DB_PATH, init_db

init_db()
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("DELETE FROM historico_pontos")
cur.execute("DELETE FROM desbravadores")

dados = [
    ("Ana Beatriz", "Lobo"), ("Lucas Andrade", "Lobo"), ("Pedro Henrique", "Lobo"),
    ("Mariana Costa", "Guepardo"), ("Gabriel Souza", "Guepardo"), ("Júlia Ferreira", "Guepardo"),
    ("Rafael Lima", "Seda Azul"), ("Larissa Rocha", "Seda Azul"), ("Enzo Martins", "Seda Azul"),
]
motivos = ["Presença", "Classe concluída", "Uniforme completo", "Especialidade", "Pontualidade", "Caça missionária"]

for nome, uni in dados:
    cur.execute("INSERT INTO desbravadores (nome, unidade, pontuacao_total) VALUES (?,?,0)", (nome, uni))
    did = cur.lastrowid
    total = 0
    for _ in range(random.randint(3, 7)):
        p = random.choice([5, 10, 15, 20, 25])
        total += p
        cur.execute(
            "INSERT INTO historico_pontos (desbravador_id, pontos, motivo, data) VALUES (?,?,?,?)",
            (did, p, random.choice(motivos), datetime.now().strftime("%d/%m/%Y %H:%M")),
        )
    cur.execute("UPDATE desbravadores SET pontuacao_total=? WHERE id=?", (total, did))

conn.commit()
conn.close()
print("Banco populado com dados de exemplo.")
