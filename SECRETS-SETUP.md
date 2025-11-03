# Configuração de Secrets para Deploy do Mar.IA Backend

Este documento explica como configurar todos os secrets necessários no GitHub repository para o deploy automatizado para Google Cloud Run.

## 📋 Secrets Obrigatórios

### 1. Google Cloud Configuration
- **`GOOGLE_APPLICATION_CREDENTIALS`**: Service Account JSON
  - Como obter: Crie uma service account no Google Cloud Console
  - Permissions necessárias:
    - Cloud Run Admin
    - Cloud SQL Client
    - Artifact Registry Writer
    - Service Account User
  - Formato: JSON completo (conteúdo do arquivo)

- **`GCLOUD_PROJECT`**: ID do seu projeto Google Cloud
  - Exemplo: `maria-backend-prod`

- **`GCLOUD_REGION`**: Região do deploy
  - Padrão: `us-central1`
  - Outras opções: `us-east1`, `southamerica-east1`, etc.

### 2. Database Configuration
- **`DATABASE_URL`**: String de conexão com PostgreSQL Cloud SQL
  - Formato: `postgresql+asyncpg://usuario:senha@IP_DO_BANCO:5432/nome_db`
  - Importante: Use `asyncpg` para FastAPI
  - O banco deve ter a extensão `pgvector` instalada

### 3. Security Configuration
- **`SECRET_KEY`**: Chave secreta para JWT
  - Como gerar: `openssl rand -base64 32`
  - Importante: Use uma chave forte e única

### 4. LLM Providers (pelo menos um)

#### Claude (Anthropic)
- **`ANTHROPIC_API_KEY`**: API key do Claude
  - Como obter: https://console.anthropic.com/
  - Formato: `sk-ant-...`

#### Gemini (Google)
- **`GOOGLE_AI_API_KEY`**: API key do Gemini
  - Como obter: https://makersuite.google.com/app/apikey
  - Formato: `AIza...`

#### OpenAI (Opcional)
- **`OPENAI_API_KEY`**: API key do OpenAI
  - Como obter: https://platform.openai.com/api-keys
  - Formato: `sk-...`

### 5. Application Settings
- **`DEFAULT_LLM_PROVIDER`**: Provider padrão
  - Opções: `claude`, `gemini`, `openai`
  - Padrão: `gemini`

- **`FRONTEND_URL`**: URL do frontend para CORS
  - Exemplo: `https://seu-frontend.vercel.app`
  - Para desenvolvimento: `http://localhost:3000`

### 6. Email Configuration (Mailgun)
- **`MAILGUN_API_KEY`**: API key do Mailgun
- **`MAILGUN_DOMAIN`**: Domínio configurado no Mailgun
- **`MAILGUN_API_URL`**: URL da API (padrão: `https://api.mailgun.net`)
- **`MAILGUN_TEST_EMAIL`**: Email para testes

### 7. Environment Variables com Fallbacks

**TODAS** as variáveis de configuração podem ser definidas via environment variables. Se não definidas, o sistema usa valores padrão (fallbacks) definidos no código.

#### Variáveis Opcionais (têm fallbacks no código)

**RAG & Chunking Configuration:**
- **`CHUNK_SIZE`**: Tamanho dos chunks (fallback: `512`)
- **`CHUNK_OVERLAP`**: Overlap entre chunks (fallback: `50`)
- **`RAG_TOP_K_CHUNKS`**: Número de chunks para retornar (fallback: `5`)
- **`RAG_MAX_SEARCH_ATTEMPTS`**: Tentativas de busca (fallback: `2`)

**Embeddings Configuration:**
- **`EMBEDDING_MODEL`**: Modelo de embeddings (fallback: `intfloat/multilingual-e5-base`)
- **`EMBEDDING_DIMENSION`**: Dimensão dos embeddings (fallback: `768`)
- **`EMBEDDING_PROVIDER`**: Provider de embeddings (fallback: `local`)

**LLM Models Configuration:**
- **`CLAUDE_MODEL`**: Modelo Claude (fallback: `claude-3-5-sonnet-20241022`)
- **`CLAUDE_MAX_TOKENS`**: Max tokens Claude (fallback: `4096`)
- **`CLAUDE_TEMPERATURE`**: Temperature Claude (fallback: `0.7`)
- **`GEMINI_MODEL`**: Modelo Gemini (fallback: `gemini-1.5-pro`)
- **`GEMINI_MAX_TOKENS`**: Max tokens Gemini (fallback: `4096`)
- **`GEMINI_TEMPERATURE`**: Temperature Gemini (fallback: `0.7`)

**Security Configuration:**
- **`JWT_ALGORITHM`**: Algoritmo JWT (fallback: `HS256`)
- **`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`**: Expiração token (fallback: `10080`)
- **`INVITATION_CODE_EXPIRE_DAYS`**: Validade convite (fallback: `7`)

**Como Funciona:**
1. **Environment Variable Definida**: Usa o valor da environment variable
2. **Environment Variable Não Definida**: Usa o fallback do código
3. **Flexibilidade Total**: Configure apenas o que precisar customizar

**Exemplos:**
```bash
# Se não definir nada, usa todos os fallbacks
# Deploy funciona com valores padrão otimizados

# Se quiser customizar apenas chunk size:
CHUNK_SIZE=1024  # Demais variáveis usam fallbacks

# Se quiser customizar modelo LLM:
DEFAULT_LLM_PROVIDER=claude
CLAUDE_MODEL=claude-3-opus-20240229
```

## 🔧 Como Configurar os Secrets

### Variáveis do Workflow (não precisam de secrets)

O GitHub Action usa algumas variáveis definidas diretamente no workflow:

**Variáveis Fixas (definidas no início do workflow):**
- **`SERVICE_NAME`**: `maria-backend` - Nome do serviço no Cloud Run
- **`IMAGE_NAME`**: `maria-backend` - Nome da imagem Docker
- **`REGISTRY`**: `${GCLOUD_REGION}-docker.pkg.dev` - Registry do Google Cloud

**Variáveis de Ambiente (precisam de secrets):**
- **`PROJECT_ID`**: `${{ secrets.GCLOUD_PROJECT }}` - ID do seu projeto Google Cloud
- **`REGION`**: `${{ secrets.GCLOUD_REGION || 'us-central1' }}` - Região do deploy

**Como Funciona:**
```yaml
env:
  PROJECT_ID: ${{ secrets.GCLOUD_PROJECT }}  # ← Secret obrigatório
  REGION: ${{ secrets.GCLOUD_REGION || 'us-central1' }}  # ← Secret opcional
  SERVICE_NAME: maria-backend                  # ← Fixo no workflow
  IMAGE_NAME: maria-backend                    # ← Fixo no workflow
  REGISTRY: ${{ secrets.GCLOUD_REGION || 'us-central1' }}-docker.pkg.dev  # ← Baseado na região
```

**Se quiser customizar**: Edite o arquivo `.github/workflows/deploy-backend.yml` e altere os valores fixos.

### Via GitHub Web Interface
1. Vá para seu repository no GitHub
2. Settings → Secrets and variables → Actions
3. Clique em "New repository secret"
4. Adicione todos os secrets listados acima

### Via GitHub CLI
```bash
gh secret set GOOGLE_APPLICATION_CREDENTIALS < service-account.json
gh secret set GCLOUD_PROJECT "seu-projeto-id"
gh secret set GCLOUD_REGION "us-central1"
gh secret set DATABASE_URL "postgresql+asyncpg://..."
gh secret set SECRET_KEY "sua-chave-secreta"
# ... e assim por diante
```

## 🏗️ Pré-requisitos do Google Cloud

### 1. Service Account com Permissões
Crie uma service account com as seguintes roles:
- Cloud Run Admin (`roles/run.admin`)
- Cloud SQL Client (`roles/cloudsql.client`)
- Artifact Registry Writer (`roles/artifactregistry.writer`)
- Service Account User (`roles/iam.serviceAccountUser`)

### 2. Ativar APIs Necessárias
No Google Cloud Console, ative:
- Cloud Run API
- Cloud SQL Admin API
- Artifact Registry API
- Cloud Build API

### 3. Criar Artifact Registry
```bash
gcloud artifacts repositories create docker-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Mar.IA"
```

### 4. Cloud SQL PostgreSQL
- Crie instância PostgreSQL (db-f1-micro recomendado)
- Habilite extensão `pgvector`
- Crie database e usuário
- Configure IP público ou privado

## 🚀 Teste de Deploy

Depois de configurar todos os secrets:

1. Faça commit para a branch `main`
2. A GitHub Action será triggerada automaticamente
3. Monitore o progresso em Actions tab
4. Service URL será exibida no final do deploy

## 🔍 Troubleshooting

### Erros Comuns
- **Permission denied**: Verifique permissões da service account
- **Artifact Registry not found**: Crie repositório ou verifique região
- **Database connection failed**: Verifique DATABASE_URL e rede
- **Build failed**: Verifique Dockerfile e dependências

### Logs Úteis
```bash
# Verificar Cloud Run logs
gcloud logs read "resource.type=cloud_run_revision" --limit 50

# Verificar service status
gcloud run services describe maria-backend --region=us-central1
```

## 💡 Dicas

- Use secrets diferentes para desenvolvimento e produção
- Gere chaves fortes e únicas
- Mantenha seus secrets seguros e não os compartilhe
- Teste primeiro em ambiente de desenvolvimento
- Monitore os custos no Google Cloud Console

## 📞 Suporte

Se tiver problemas durante o setup:
1. Verifique os logs da GitHub Action
2. Verifique as permissões no Google Cloud
3. Confirme que todos os secrets estão configurados
4. Teste a conexão com o banco de dados manualmente