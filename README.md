# Mar.IA - Backend

Sistema RAG Agentic para fornecer informações seguras para a população trans brasileira.

## 📋 Sobre o Projeto

**Mar.IA** é um sistema de inteligência artificial que fornece informações educativas e orientações para a população trans brasileira, focando em três áreas principais:

1. **Riscos e Caminhos Seguros - Automedicação Hormonal**
2. **Retificação de Nome e Gênero em Documentos**
3. **Processo para Acesso a Cirurgias de Afirmação de Gênero via Planos de Saúde**

O projeto segue princípios de responsabilidade digital, incluindo disclaimers automáticos, validação de segurança de respostas e orientação para profissionais especializados.

## 🏗️ Arquitetura

- **Framework**: FastAPI com Python 3.13+
- **Banco de Dados**: PostgreSQL com pgvector para busca vetorial
- **Embeddings**: Sentence Transformers (intfloat/multilingual-e5-base)
- **LLM Integration**: Claude, Gemini e OpenAI via factory pattern
- **Dependency Injection**: Wireup (injeção assíncrona)
- **ORM**: SQLModel
- **Testes**: pytest

## 💻 Instalação

### Pré-requisitos

- Python 3.13+
- PostgreSQL com pgvector
- Poetry

### Configuração Local

1. **Clonar o repositório**
```bash
git clone <repository-url>
cd maria/backend
```

2. **Instalar dependências**
```bash
poetry install
```

3. **Configurar variáveis de ambiente**
```bash
cp .env.template .env
# Editar .env com suas configurações locais
```

4. **Configurar banco de dados**
```bash
# Criar banco PostgreSQL local
createdb maria_db

# Executar migrations (quando implementadas)
# poetry run alembic upgrade head
```

5. **Executar aplicação**
```bash
poetry run uvicorn src.backend.main:app --reload
```

## 🚀 Deploy para Produção

### Deploy Automático (Google Cloud Run)

Este projeto está configurado para deploy **totalmente automatizado** via GitHub Actions para Google Cloud Run, otimizado para o orçamento de $300 grátis.

### Configuração de Production

- **CPU**: 1 vCPU
- **Memory**: 2GB RAM (otimizado para ML models)
- **Scaling**: 0-10 instâncias (economia pay-per-use)
- **Region**: `us-central1`
- **Database**: PostgreSQL + pgvector via Cloud SQL

### Processo de Deploy

1. **Configurar Secrets** (veja seção [🔐 Configuração de Secrets](#-configuração-de-secrets))
2. **Fazer push** para branch `main`
3. **Deploy automático** acontece em ~5 minutos

### Links Úteis (pós-deploy)

- **API**: `https://maria-api-xxxxx.a.run.app`
- **Documentation**: `/docs` (Swagger)
- **Health Check**: `/health`
- **Ready Check**: `/ready`

## 🔐 Configuração de Secrets

### Secrets Obrigatórios

Configure os seguintes secrets no seu repository GitHub:

#### Google Cloud
- **`GOOGLE_APPLICATION_CREDENTIALS`**: Service Account JSON
- **`GCLOUD_PROJECT`**: ID do projeto Google Cloud
- **`GCLOUD_REGION`**: Região do deploy (ex: `us-central1`)

#### Database
- **`DATABASE_URL`**: String de conexão PostgreSQL
  - Formato: `postgresql+asyncpg://usuario:senha@IP:5432/nome_db`

#### Application
- **`SECRET_KEY`**: Chave secreta para JWT (gerar com `openssl rand -base64 32`)
- **`DEFAULT_LLM_PROVIDER`**: Provedor LLM (`claude` ou `gemini`)

#### LLM Providers (pelo menos um)
- **`ANTHROPIC_API_KEY`**: API key do Claude (se usar Claude)
- **`GOOGLE_AI_API_KEY`**: API key do Gemini (se usar Gemini)
- **`OPENAI_API_KEY`**: API key do OpenAI (se usar OpenAI)

#### Opcional
- **`FRONT_USER_URL`**: URL do frontend para CORS
- **`MAILGUN_API_KEY`**, `MAILGUN_DOMAIN`**: Para envio de emails

### Comandos para Configurar Secrets via CLI

```bash
# Google Cloud
gh secret set GOOGLE_APPLICATION_CREDENTIALS < service-account.json
gh secret set GCLOUD_PROJECT "seu-projeto-id"
gh secret set GCLOUD_REGION "us-central1"

# Database
gh secret set DATABASE_URL "postgresql+asyncpg://user:pass@IP:5432/db_name"

# Application
gh secret set SECRET_KEY "$(openssl rand -base64 32)"
gh secret set DEFAULT_LLM_PROVIDER "gemini"

# LLM Provider (escolha um)
gh secret set GOOGLE_AI_API_KEY "AIzaSuaChaveAqui"
# ou
gh secret set ANTHROPIC_API_KEY "sk-ant-sua-chave"
```

## 🗄️ Configuração do Cloud SQL PostgreSQL

### Configurações Recomendadas da Instância

- **Database Engine**: PostgreSQL 14 (ou mais recente)
- **Instance Type**: `db-f1-micro` (otimizado para $300 grátis)
- **vCPUs**: 1 shared vCPU
- **Memory**: 0.6 GB RAM
- **Storage**: 10 GB SSD (free tier)
- **Automated Backups**: Ativado
- **SSL**: Ativado

### Comandos SQL Iniciais

Execute após criar a instância:

```sql
-- Habilitar extensão pgvector (essencial para embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar database e usuário
CREATE DATABASE maria_db;
CREATE USER maria_user WITH PASSWORD 'senha_forte_aqui';
GRANT ALL PRIVILEGES ON DATABASE maria_db TO maria_user;

-- Verificar extensão
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### String de Conexão

```
postgresql+asyncpg://maria_user:senha_forte_aqui@IP_PUBLICO:5432/maria_db
```

## 📊 Estrutura do Projeto

```
backend/
├── .github/workflows/
│   └── deploy-backend.yml    # GitHub Action CI/CD
├── src/backend/
│   ├── core/                   # Configurações centrais
│   │   ├── config.py           # Settings com fallbacks
│   │   ├── database.py         # Database connection
│   │   └── validators/        # Validadores
│   ├── modules/                # Módulos de negócio
│   │   ├── auth/              # Autenticação JWT
│   │   │   ├── auth_router.py
│   │   │   ├── auth_service.py
│   │   │   └── auth_repository.py
│   │   ├── document/          # Gestão de documentos
│   │   ├── chunk/             # Processamento de chunks
│   │   └── rag/               # Sistema RAG principal
│   │       ├── rag_router.py
│   │       ├── rag_service.py
│   │       └── rag_repository.py
│   ├── integrations/           # Integrações externas
│   │   ├── llm/              # Interfaces LLM
│   │   │   ├── protocol.py
│   │   │   ├── claude.py
│   │   │   ├── gemini.py
│   │   │   └── openai.py
│   │   └── embeddings/       # Providers de embeddings
│   └── services/               # Serviços de domínio
├── Dockerfile                 # Multi-stage build otimizado
├── .dockerignore              # Build otimizado
├── pyproject.toml            # Dependências Poetry
└── logs/                     # Logs da aplicação
```

## 🔧 Environment Variables com Fallbacks

**TODAS** as variáveis de configuração podem ser definidas via environment variables. Se não definidas, o sistema usa valores padrão (fallbacks) definidos no código.

### Variáveis Principais

| Variável | Fallback | Descrição |
|----------|----------|-----------|
| `CHUNK_SIZE` | `512` | Tamanho dos chunks para RAG |
| `CHUNK_OVERLAP` | `50` | Overlap entre chunks |
| `RAG_TOP_K_CHUNKS` | `5` | Número de chunks retornados |
| `EMBEDDING_MODEL` | `intfloat/multilingual-e5-base` | Modelo de embeddings |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Modelo Claude |
| `GEMINI_MODEL` | `gemini-1.5-pro` | Modelo Gemini |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Expiração do token (7 dias) |

## 🎯 Endpoints da API

### Health Checks
- `GET /health` - Health check básico
- `GET /ready` - Readiness check com validação de dependências

### RAG System
- `POST /rag/query` - Consulta RAG
- `POST /rag/query/stream` - Consulta RAG com streaming
- `GET /rag/embeddings/encode` - Teste de embeddings
- `GET /rag/health` - Health check do RAG

### Authentication
- `POST /auth/sign_up` - Registro de usuário
- `POST /auth/login` - Login
- `POST /auth/validate_invite` - Validar convite

### Documents
- `POST /document/upload` - Upload de documento
- `GET /document/list` - Listar documentos
- `DELETE /document/{id}` - Excluir documento

### Geral
- `GET /` - Informações da aplicação
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc

## 🔍 Sistema de Responsabilidade Digital

### Disclaimers Automáticos
- Detecção automática de tipo de consulta
- Disclaimers específicos por categoria
- Validação de segurança de respostas

### Limitações
- Não faz diagnósticos médicos
- Não prescreve medicamentos
- Não substitui aconselhamento profissional
- Sempre orienta para profissionais especializados

### Privacidade
- Conversas não são armazenadas no servidor
- Dados de usuário limitados ao essencial
- Anonimização automática de consultas

## 🛠️ Desenvolvimento

### Adicionando Dependências
```bash
poetry add <package-name>
```

### Executando Testes
```bash
poetry run pytest
```

### Logs
Os logs são estruturados com Loguru e salvos em `logs/maria.log`.

## 📈 Monitoramento e Troubleshooting

### Logs em Produção
```bash
# Verificar logs do Cloud Run
gcloud logs read "resource.type=cloud_run_revision" --follow

# Verificar status do serviço
gcloud run services describe maria-api --region=us-central1
```

### Health Checks
```bash
# Testar health check da API
curl https://maria-api-xxxxx.run.app/health

# Testar ready check
curl https://maria-api-xxxxx.run.app/ready
```

## 💰 Custos Estimados (Dentro $300 grátis)

- **Cloud Run**: ~$20-50/mês (pay-per-use)
- **Cloud SQL (db-f1-micro)**: ~$15/mês
- **Artifact Registry**: ~$5/mês
- **Total estimado**: ~$40-70/mês

## 🔄 Processo de CI/CD

### GitHub Actions Workflow
1. **Trigger**: Push para branch `main`
2. **Build**: Docker image multi-stage otimizado
3. **Push**: Image para Artifact Registry
4. **Deploy**: Atualização do Cloud Run service
5. **Health Check**: Validação automática

### Deploy Manual (se necessário)
```bash
# Build e push manual
docker build -t us-central1-docker.pkg.dev/PROJECT/maria-api:latest .
docker push us-central1-docker.pkg.dev/PROJECT/maria-api:latest

# Deploy manual
gcloud run deploy maria-api \
  --image us-central1-docker.pkg.dev/PROJECT/maria-api:latest \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --allow-unauthenticated
```

## 🐛 Estrutura de Módulos

Cada módulo segue o padrão:

```
modules/<nome>/
├── <nome>_router.py    # Endpoints FastAPI
├── <nome>_service.py   # Lógica de negócio
├── <name>_repository.py # Acesso a dados
├── <name>_dto.py       # Data transfer objects
└── <name>_enums.py     # Enumerações
```

## 🚀 Deploy para Produção

### Deploy Automático (Google Cloud Run)

Este projeto está configurado para deploy **totalmente automatizado** via GitHub Actions para Google Cloud Run, otimizado para o orçamento de $300 grátis.

### Configuração de Production

- **CPU**: 1 vCPU
- **Memory**: 2GB RAM (otimizado para ML models)
- **Scaling**: 0-10 instâncias (economia pay-per-use)
- **Region**: `us-central1`
- **Database**: PostgreSQL + pgvector via Cloud SQL

### Processo de Deploy

1. **Configurar Secrets** (veja seção [🔐 Configuração de Secrets](#-configuração-de-secrets))
2. **Fazer push** para branch `main`
3. **Deploy automático** acontece em ~5 minutos

### Links Úteis (pós-deploy)

- **API**: `https://maria-api-xxxxx.a.run.app`
- **Documentation**: `/docs` (Swagger)
- **Health Check**: `/health`
- **Ready Check**: `/ready`

## 🔐 Configuração de Secrets

### Secrets Obrigatórios

Configure os seguintes secrets no seu repository GitHub:

#### Google Cloud
- **`GOOGLE_APPLICATION_CREDENTIALS`**: Service Account JSON
- **`GCLOUD_PROJECT`**: ID do projeto Google Cloud
- **`GCLOUD_REGION`**: Região do deploy (ex: `us-central1`)

#### Database
- **`DATABASE_URL`**: String de conexão PostgreSQL
  - Formato: `postgresql+asyncpg://usuario:senha@IP:5432/nome_db`

#### Application
- **`SECRET_KEY`**: Chave secreta para JWT (gerar com `openssl rand -base64 32`)
- **`DEFAULT_LLM_PROVIDER`**: Provedor LLM (`claude` ou `gemini`)

#### LLM Providers (pelo menos um)
- **`ANTHROPIC_API_KEY`**: API key do Claude (se usar Claude)
- **`GOOGLE_AI_API_KEY`**: API key do Gemini (se usar Gemini)
- **`OPENAI_API_KEY`**: API key do OpenAI (se usar OpenAI)

#### Opcional
- **`FRONT_USER_URL`**: URL do frontend para CORS
- **`MAILGUN_API_KEY`**, `MAILGUN_DOMAIN`**: Para envio de emails

### Comandos para Configurar Secrets via CLI

```bash
# Google Cloud
gh secret set GOOGLE_APPLICATION_CREDENTIALS < service-account.json
gh secret set GCLOUD_PROJECT "seu-projeto-id"
gh secret set GCLOUD_REGION "us-central1"

# Database
gh secret set DATABASE_URL "postgresql+asyncpg://user:pass@IP:5432/db_name"

# Application
gh secret set SECRET_KEY "$(openssl rand -base64 32)"
gh secret set DEFAULT_LLM_PROVIDER "gemini"

# LLM Provider (escolha um)
gh secret set GOOGLE_AI_API_KEY "AIzaSuaChaveAqui"
# ou
gh secret set ANTHROPIC_API_KEY "sk-ant-sua-chave"
```

## 🗄️ Configuração do Cloud SQL PostgreSQL

### Configurações Recomendadas da Instância

- **Database Engine**: PostgreSQL 14 (ou mais recente)
- **Instance Type**: `db-f1-micro` (otimizado para $300 grátis)
- **vCPUs**: 1 shared vCPU
- **Memory**: 0.6 GB RAM
- **Storage**: 10 GB SSD (free tier)
- **Automated Backups**: Ativado
- **SSL**: Ativado

### Comandos SQL Iniciais

Execute após criar a instância:

```sql
-- Habilitar extensão pgvector (essencial para embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar database e usuário
CREATE DATABASE maria_db;
CREATE USER maria_user WITH PASSWORD 'senha_forte_aqui';
GRANT ALL PRIVILEGES ON DATABASE maria_db TO maria_user;

-- Verificar extensão
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### String de Conexão

```
postgresql+asyncpg://maria_user:senha_forte_aqui@IP_PUBLICO:5432/maria_db
```

## 📊 Estrutura do Projeto

```
backend/
├── .github/workflows/
│   └── deploy-backend.yml    # GitHub Action CI/CD
├── src/backend/
│   ├── core/                   # Configurações centrais
│   │   ├── config.py           # Settings com fallbacks
│   │   ├── database.py         # Database connection
│   │   └── validators/        # Validadores
│   ├── modules/                # Módulos de negócio
│   │   ├── auth/              # Autenticação JWT
│   │   │   ├── auth_router.py
│   │   │   ├── auth_service.py
│   │   │   └── auth_repository.py
│   │   ├── document/          # Gestão de documentos
│   │   ├── chunk/             # Processamento de chunks
│   │   └── rag/               # Sistema RAG principal
│   │       ├── rag_router.py
│   │       ├── rag_service.py
│   │       └── rag_repository.py
│   ├── integrations/           # Integrações externas
│   │   ├── llm/              # Interfaces LLM
│   │   │   ├── protocol.py
│   │   │   ├── claude.py
│   │   │   ├── gemini.py
│   │   │   └── openai.py
│   │   └── embeddings/       # Providers de embeddings
│   └── services/               # Serviços de domínio
├── Dockerfile                 # Multi-stage build otimizado
├── .dockerignore              # Build otimizado
├── pyproject.toml            # Dependências Poetry
└── logs/                     # Logs da aplicação
```

## 🔧 Environment Variables com Fallbacks

**TODAS** as variáveis de configuração podem ser definidas via environment variables. Se não definidas, o sistema usa valores padrão (fallbacks) definidos no código.

### Variáveis Principais

| Variável | Fallback | Descrição |
|----------|----------|-----------|
| `CHUNK_SIZE` | `512` | Tamanho dos chunks para RAG |
| `CHUNK_OVERLAP` | `50` | Overlap entre chunks |
| `RAG_TOP_K_CHUNKS` | `5` | Número de chunks retornados |
| `EMBEDDING_MODEL` | `intfloat/multilingual-e5-base` | Modelo de embeddings |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-20241022` | Modelo Claude |
| `GEMINI_MODEL` | `gemini-1.5-pro` | Modelo Gemini |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Expiração do token (7 dias) |

## 🎯 Endpoints da API

### Health Checks
- `GET /health` - Health check básico
- `GET /ready` - Readiness check com validação de dependências

### RAG System
- `POST /rag/query` - Consulta RAG
- `POST /rag/query/stream` - Consulta RAG com streaming
- `GET /rag/embeddings/encode` - Teste de embeddings
- `GET /rag/health` - Health check do RAG

### Authentication
- `POST /auth/sign_up` - Registro de usuário
- `POST /auth/login` - Login
- `POST /auth/validate_invite` - Validar convite

### Documents
- `POST /document/upload` - Upload de documento
- `GET /document/list` - Listar documentos
- `DELETE /document/{id}` - Excluir documento

### Geral
- `GET /` - Informações da aplicação
- `GET /docs` - Documentação Swagger
- `GET /redoc` - Documentação ReDoc

## 🔍 Sistema de Responsabilidade Digital

### Disclaimers Automáticos
- Detecção automática de tipo de consulta
- Disclaimers específicos por categoria
- Validação de segurança de respostas

### Limitações
- Não faz diagnósticos médicos
- Não prescreve medicamentos
- Não substitui aconselhamento profissional
- Sempre orienta para profissionais especializados

### Privacidade
- Conversas não são armazenadas no servidor
- Dados de usuário limitados ao essencial
- Anonimização automática de consultas

## 🛠️ Desenvolvimento

### Adicionando Dependências
```bash
poetry add <package-name>
```

### Executando Testes
```bash
poetry run pytest
```

### Logs
Os logs são estruturados com Loguru e salvos em `logs/maria.log`.

## 📈 Monitoramento e Troubleshooting

### Logs em Produção
```bash
# Verificar logs do Cloud Run
gcloud logs read "resource.type=cloud_run_revision" --follow

# Verificar status do serviço
gcloud run services describe maria-api --region=us-central1
```

### Health Checks
```bash
# Testar health check da API
curl https://maria-api-xxxxx.run.app/health

# Testar ready check
curl https://maria-api-xxxxx.run.app/ready
```

## 💰 Custos Estimados (Dentro $300 grátis)

- **Cloud Run**: ~$20-50/mês (pay-per-use)
- **Cloud SQL (db-f1-micro)**: ~$15/mês
- **Artifact Registry**: ~$5/mês
- **Total estimado**: ~$40-70/mês

## 🔄 Processo de CI/CD

### GitHub Actions Workflow
1. **Trigger**: Push para branch `main`
2. **Build**: Docker image multi-stage otimizado
3. **Push**: Image para Artifact Registry
4. **Deploy**: Atualização do Cloud Run service
5. **Health Check**: Validação automática

### Deploy Manual (se necessário)
```bash
# Build e push manual
docker build -t us-central1-docker.pkg.dev/PROJECT/maria-api:latest .
docker push us-central1-docker.pkg.dev/PROJECT/maria-api:latest

# Deploy manual
gcloud run deploy maria-api \
  --image us-central1-docker.pkg.dev/PROJECT/maria-api:latest \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --allow-unauthenticated
```

## 🐛 Estrutura de Módulos

Cada módulo segue o padrão:

```
modules/<nome>/
├── <nome>_router.py    # Endpoints FastAPI
├── <nome>_service.py   # Lógica de negócio
├── <name>_repository.py # Acesso a dados
├── <name>_dto.py       # Data transfer objects
└── <name>_enums.py     # Enumerações
```

## 📝 Licença

Projeto acadêmico - TCC.

---

**Este projeto prioriza segurança, responsabilidade digital e experiência do usuário para servir a população trans brasileira com informações confiáveis e seguras, respeitando os contextos específicos de vulnerabilidade e exclusão enfrentados por esta comunidade.**