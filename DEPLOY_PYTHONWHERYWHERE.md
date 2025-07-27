# 🚀 Deploy PUCRS Gamification System no PythonAnywhere

Este guia completo te ajudará a fazer o deploy do Sistema de Gamificação PUCRS no PythonAnywhere gratuitamente.

## 📋 Pré-requisitos

1. **Conta PythonAnywhere**: [Criar conta gratuita](https://www.pythonanywhere.com/registration/register/beginner/)
2. **Conta GitHub**: Para hospedar o código
3. **Base64 Images**: O sistema já está configurado para usar imagens em base64 (sem necessidade de storage externo)

## 🗄️ Configuração do Banco de Dados

### Opção 1: MongoDB Atlas (Recomendado - Gratuito)
1. Criar conta no [MongoDB Atlas](https://www.mongodb.com/atlas/database)
2. Criar cluster gratuito (512MB)
3. Configurar usuário e senha
4. Obter string de conexão

### Opção 2: PostgreSQL (PythonAnywhere nativo)
Se preferir PostgreSQL, você precisará adaptar o código para usar SQLAlchemy.

## 📁 Estrutura do Projeto para Deploy

```
projeto-pucrs/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── build/ (após npm run build)
│   ├── package.json
│   └── src/
└── wsgi.py (arquivo principal para PythonAnywhere)
```

## 🔧 Passos de Deploy

### 1. Preparar o Código

#### Backend - Atualizar requirements.txt:
```txt
fastapi==0.104.1
uvicorn==0.24.0
motor==3.3.2
python-dotenv==1.0.0
pydantic==2.5.0
bcrypt==4.1.2
PyJWT==2.8.0
python-multipart==0.0.6
```

#### Criar arquivo wsgi.py na raiz:
```python
import sys
import os
from pathlib import Path

# Adicionar o diretório do backend ao path
project_dir = Path(__file__).parent
backend_dir = project_dir / 'backend'
sys.path.insert(0, str(backend_dir))

# Configurar variáveis de ambiente
os.environ.setdefault('MONGO_URL', 'sua_string_de_conexao_mongodb_atlas')
os.environ.setdefault('DB_NAME', 'pucrs_gamification')

# Importar e configurar a aplicação
from server import app

# WSGI application
application = app
```

#### Configurar .env para produção:
```env
MONGO_URL="mongodb+srv://usuario:senha@cluster.mongodb.net/"
DB_NAME="pucrs_gamification"
SECRET_KEY="sua_chave_secreta_super_segura_2025"
```

### 2. Frontend - Build para Produção

```bash
cd frontend
npm run build
```

### 3. Upload para PythonAnywhere

#### Via GitHub (Recomendado):
1. **Criar repositório no GitHub**
2. **Push do código**
3. **No PythonAnywhere Bash Console:**
```bash
cd ~
git clone https://github.com/seu-usuario/pucrs-gamification.git
cd pucrs-gamification
```

#### Via Upload Direto:
1. Compactar projeto em .zip
2. Upload via PythonAnywhere Files
3. Extrair no diretório home

### 4. Configurar Web App no PythonAnywhere

1. **Dashboard PythonAnywhere** → **Web** → **Add a new web app**
2. **Choose Python version**: 3.10
3. **Framework**: Manual configuration
4. **Python version**: 3.10

### 5. Configurações do Web App

#### WSGI Configuration File:
```python
import sys
import os
from pathlib import Path

# Adicionar path do projeto
path = '/home/seuusuario/pucrs-gamification'
if path not in sys.path:
    sys.path.insert(0, path)

backend_path = f'{path}/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Configurar variáveis de ambiente
os.environ['MONGO_URL'] = 'sua_string_conexao_mongodb_atlas'
os.environ['DB_NAME'] = 'pucrs_gamification'

from server import app
application = app
```

#### Virtual Environment:
```bash
# No PythonAnywhere Bash Console
cd ~/pucrs-gamification
python3.10 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

#### Static Files Configuration:
- **URL**: `/static/`
- **Directory**: `/home/seuusuario/pucrs-gamification/frontend/build/static/`

### 6. Configurar Frontend

#### Opção 1: Servir via PythonAnywhere (Simples)
1. **Static Files** → **Add new static file**
2. **URL**: `/`
3. **Directory**: `/home/seuusuario/pucrs-gamification/frontend/build/`

#### Opção 2: Deploy separado (Netlify/Vercel)
1. Deploy do frontend no Netlify/Vercel
2. Atualizar CORS no backend para permitir o domínio frontend

### 7. Variáveis de Ambiente Frontend

Atualizar `/frontend/.env.production`:
```env
REACT_APP_BACKEND_URL=https://seuusuario.pythonanywhere.com
```

### 8. CORS Configuration

No `server.py`, atualizar CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "https://seuusuario.pythonanywhere.com",
        "http://localhost:3000",  # Para desenvolvimento
        "https://seu-frontend-url.netlify.app"  # Se frontend separado
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔄 Atualizações e Manutenção

### Atualizar via Git:
```bash
cd ~/pucrs-gamification
git pull origin main
# Reiniciar web app no dashboard
```

### Logs e Debug:
- **Error Log**: Disponível no dashboard Web
- **Server Log**: Via Bash Console

## 📊 Monitoramento

### Métricas Disponíveis:
- CPU usage
- Bandwidth
- Storage usage
- Database connections

### Backup:
- Backup automático do MongoDB Atlas
- Export de dados via admin panel

## 🔒 Segurança

### Configurações Importantes:
1. **JWT Secret**: Use uma chave forte e única
2. **MongoDB**: Configure IP whitelist e usuários específicos
3. **HTTPS**: Automático no PythonAnywhere
4. **Environment Variables**: Nunca commitar .env para Git

### Exemplo .env seguro:
```env
MONGO_URL="mongodb+srv://pucrs_user:SenhaForte123!@cluster-abc123.mongodb.net/"
DB_NAME="pucrs_prod"
SECRET_KEY="sua_chave_jwt_super_secura_256_bits_2025"
```

## 🎯 URLs Finais

### Aplicação:
- **Frontend + Backend**: `https://seuusuario.pythonanywhere.com`
- **API Docs**: `https://seuusuario.pythonanywhere.com/docs`

### Admin Padrão:
Criar via registro com role "admin" na primeira execução.

## 📞 Suporte

### Links Úteis:
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Troubleshooting Comum:
1. **Import Errors**: Verificar paths no WSGI
2. **Database Connection**: Testar string de conexão
3. **Static Files**: Verificar paths absolutos
4. **CORS Errors**: Atualizar allow_origins

---

🚀 **Sistema Pronto para Produção!**

O sistema PUCRS já está otimizado para deploy com:
- ✅ Gerenciamento de arquivos em base64
- ✅ JWT authentication seguro
- ✅ API RESTful documentada
- ✅ Frontend responsivo e profissional
- ✅ Sistema de gamificação completo