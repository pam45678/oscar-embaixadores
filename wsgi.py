"""
Arquivo WSGI para o PythonAnywhere.
No painel Web do PythonAnywhere, aponte o "WSGI configuration file" para
importar a variável `application` deste arquivo (ou cole o conteúdo lá).

IMPORTANTE: troque 'SEUUSUARIO' pelo seu nome de usuário do PythonAnywhere.
"""
import sys
import os

# Caminho do projeto no PythonAnywhere (ajuste SEUUSUARIO)
project_home = "/home/Pamelarodri/oscar-desbravadores"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Garante que o banco seja criado na primeira execução
from app import app as application, init_db

with application.app_context():
    init_db()
