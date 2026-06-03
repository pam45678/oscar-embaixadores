"""
Carga inicial — insere a LISTA OFICIAL do clube no banco Postgres (Neon),
todos com 0 pontos. Roda UMA vez, manualmente, depois de configurar a
DATABASE_URL. É idempotente: se já houver desbravadores no banco, não faz nada
(assim você nunca perde os pontos que já lançou).

Como rodar (no seu PC, com a DATABASE_URL do Neon no ambiente):
    DATABASE_URL="postgresql://..." python migrar_dados.py
"""
import db as database

# Lista oficial do clube — (nome completo, unidade). Todos começam com 0 pontos.
INTEGRANTES = [
    # SEDA AZUL (desbravadores)
    ("Luísa Cristina Silva Vieira", "Seda Azul"),
    ("Leandra Giovanna Machado Morganti", "Seda Azul"),
    ("Beatriz Fantini Antunes", "Seda Azul"),
    ("Lavínia da Cruz Braga", "Seda Azul"),
    ("Larissa Gabriela da Cruz Teixeira", "Seda Azul"),
    ("Emilly Alves Costa", "Seda Azul"),
    ("Júlia Carvalho Bianchini", "Seda Azul"),
    ("Emily Luma Ferreira de Lima", "Seda Azul"),
    ("Helena Vitória Rosa Cintra", "Seda Azul"),
    ("Sophia Rafaela Sales Casagrande", "Seda Azul"),
    # LOBO (desbravadores)
    ("Felipe Monteiro Castro", "Lobo"),
    ("Vinícius Lavezo Luengo", "Lobo"),
    ("Yuri Gabriel Mantovani", "Lobo"),
    ("Bernardo Henrique dos Santos Ruas", "Lobo"),
    ("Pedro Vieira da Silva", "Lobo"),
    ("Richard Pavan Cunha", "Lobo"),
    ("Davi Henrique Gomes da Silva", "Lobo"),
    # GUEPARDO (desbravadores)
    ("Mohammed Messias Batista", "Guepardo"),
    ("Lucas Luciano Silva Vieira", "Guepardo"),
    ("João Vitor Candido dos Santos", "Guepardo"),
    # GORILA (diretoria)
    ("Dário Fernando Silva Fagundes", "Gorila"),
    ("Victor Gabriel Gomes da Silva", "Gorila"),
    ("Felipe Tosi Gomes", "Gorila"),
    ("Márcio Candido da Costa", "Gorila"),
    ("Anderson Geroldo Cunha", "Gorila"),
    ("João Pedro Tosi Gomes", "Gorila"),
    ("Murilo Cesar Siqueira Barros", "Gorila"),
    ("Fabiano Rosendo da Silva", "Gorila"),
    ("Anderson Rodrigues Gomes", "Gorila"),
    # MONARCA (diretoria)
    ("Agata Mariano Miranda", "Monarca"),
    ("Camila Oliveira Gomes", "Monarca"),
    ("Pâmela Rodrigues", "Monarca"),
    ("Máira Samires da Rocha Fonseca", "Monarca"),
    ("Suelen Solani Tosi Gomes", "Monarca"),
    ("Erica Fernanda Mariano Miranda", "Monarca"),
    ("Eulene Carvalho Bianchini", "Monarca"),
]


def main():
    database.init_db()
    db = database.connect()

    ja_tem = db.execute(
        "SELECT COUNT(*) AS c FROM desbravadores"
    ).fetchone()["c"]
    if ja_tem and int(ja_tem) > 0:
        print(f"Carga ignorada: já existem {ja_tem} integrantes no banco.")
        db.close()
        return

    for nome, unidade in INTEGRANTES:
        db.execute(
            "INSERT INTO desbravadores (nome, unidade, pontuacao_total) "
            "VALUES (?, ?, 0)",
            (nome, unidade),
        )

    db.commit()
    db.close()
    print(f"Carga concluída: {len(INTEGRANTES)} integrantes inseridos (0 pontos).")


if __name__ == "__main__":
    main()
