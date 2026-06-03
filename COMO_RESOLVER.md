# Como deixar os dados FIXOS (nunca mais sumir)

## O que estava acontecendo
Seu site guardava os dados num arquivo (`clube.db`) **dentro do servidor do Render**.
No plano gratuito, o disco do Render é apagado toda vez que o serviço dorme ou
reinicia. Além disso, o build rodava um "seed" que zerava os dados a cada deploy.
Por isso você refazia tudo o tempo todo.

## A solução
Agora os dados ficam num **banco Postgres externo e gratuito (Neon)**, que
**não apaga nada** e **não dorme**. Já adaptei todo o código. Só falta você:

1. Criar a conta no Neon (grátis, 2 min)
2. Colar a string de conexão no Render
3. Rodar a migração uma vez (pra trazer os dados que estavam no ar)

---

## PASSO 1 — Criar o banco no Neon (grátis)
1. Acesse https://neon.tech e crie conta (pode usar login do Google/GitHub)
2. Clique em **Create Project** (nome: `oscar-embaixadores`, região mais perto: US East)
3. Quando criar, aparece uma tela **Connection String**. Copie a que começa com:
   `postgresql://...neon.tech/neondb?sslmode=require`
   > Essa é a sua DATABASE_URL. Guarde, não compartilhe em público.

## PASSO 2 — Configurar no Render
1. Entre no painel do Render → seu serviço **oscar-embaixadores**
2. Menu **Environment** → **Add Environment Variable**
3. Key: `DATABASE_URL`  |  Value: cole a string do Neon
4. Salve. O Render vai reiniciar o serviço sozinho.

## PASSO 3 — Subir o código novo pro GitHub
No seu computador, dentro da pasta do projeto:
```
git add -A
git commit -m "Persistir dados no Postgres (Neon) e remover seed do build"
git push
```
O Render detecta o push e faz o deploy automático.

## PASSO 4 — Carregar a lista oficial do clube (rodar UMA vez)
Isso insere os 28 integrantes oficiais (Seda Azul, Lobo, Guepardo, Monarca,
Gorila), todos com 0 pontos. Os nomes de teste antigos foram descartados.
No seu PC (ou no Shell do Render, se tiver), com a DATABASE_URL configurada:
```
DATABASE_URL="postgresql://...neon.tech/neondb?sslmode=require" python migrar_dados.py
```
> Pode rodar sem medo: se já tiver dados no banco, ele NÃO duplica nada.
> Depois é só logar no /admin e ir lançando os pontos reais — eles ficam salvos pra sempre.

Pronto. A partir daí, tudo que você e a diretora lançarem fica salvo pra sempre.

---

## Detalhes técnicos (pra referência)
- `db.py` — camada nova: usa Postgres se existir `DATABASE_URL`, senão SQLite local (só pra teste no seu PC).
- `app.py` — agora usa `db.py`. Senhas viraram variáveis de ambiente (com os mesmos
  valores padrão: admin `1986`, diretoria `Embaixadores@10`). Se quiser trocar as senhas,
  é só adicionar `ADMIN_PASSWORD` e `DIRETORIA_PASSWORD` no Environment do Render.
- `render.yaml` — o build **não roda mais nenhum seed**. Só instala dependências.
- `seed.py`, `seed_real.py`, `wsgi.py` — removidos (eram a causa do reset).
- `migrar_dados.py` — script de migração única, idempotente.

## Dica de ouro (opcional)
O Render free "dorme" após 15 min sem acesso e demora ~30s pra acordar.
Os dados não somem mais, mas o site fica lento na 1ª visita. Se incomodar,
use um "ping" grátis (ex: UptimeRobot a cada 10 min) pra manter acordado.
