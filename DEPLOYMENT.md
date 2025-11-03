# Guia de Deploy - Mar.IA Backend para Google Cloud Run

Este guia cobre o processo completo de deploy do backend Mar.IA para Google Cloud Run usando GitHub Actions, otimizado para o orçamento de $300 grátis.

## 🏗️ Arquitetura de Deploy

```
GitHub Repository → GitHub Action → Docker Build → Cloud Run ← → Cloud SQL (PostgreSQL + pgvector)
```

## 📋 Pré-requisitos

### 1. Google Cloud Project
- ✅ Projeto Google Cloud já configurado (informado)
- Conta com $300 de crédito gratuito ativado

### 2. Database Setup
- PostgreSQL Cloud SQL com extensão pgvector
- Instância `db-f1-micro` recomendada para economia
- Database e usuário criados

### 3. Service Account
Crie uma service account com as seguintes permissions:
- **Cloud Run Admin** (`roles/run.admin`)
- **Cloud SQL Client** (`roles/cloudsql.client`)
- **Artifact Registry Writer** (`roles/artifactregistry.writer`)
- **Service Account User** (`roles/iam.serviceAccountUser`)

### 4. APIs Ativadas
No Google Cloud Console, ative:
- Cloud Run API
- Cloud SQL Admin API
- Artifact Registry API

## 🔧 Configuração do Repositório

### Estrutura de Arquivos Criados
```
backend/
├── .github/workflows/deploy-backend.yml  # GitHub Action
├── Dockerfile                           # Multi-stage build otimizado
├── .dockerignore                        # Build otimizado
├── SECRETS-SETUP.md                     # Guia de configuração
└── DEPLOYMENT.md                        # Este arquivo
```

### Configuração de Secrets
Siga o guia completo em `SECRETS-SETUP.md`. Os secrets obrigatórios são:

**Google Cloud:**
- `GOOGLE_APPLICATION_CREDENTIALS`: Service Account JSON
- `GCLOUD_PROJECT`: ID do projeto
- `GCLOUD_REGION`: Região (default: `us-central1`)

**Database:**
- `DATABASE_URL`: PostgreSQL connection string

**Application:**
- `SECRET_KEY`: JWT secret key
- `ANTHROPIC_API_KEY`: Claude API key
- `GOOGLE_AI_API_KEY`: Gemini API key
- `DEFAULT_LLM_PROVIDER`: `claude` ou `gemini`

## 🚀 Processo de Deploy

### 1. Configurar Secrets
```bash
# Exemplo usando GitHub CLI
gh secret set GOOGLE_APPLICATION_CREDENTIALS < service-account.json
gh secret set GCLOUD_PROJECT "maria-backend-prod"
gh secret set GCLOUD_REGION "us-central1"
gh secret set DATABASE_URL "postgresql+asyncpg://user:pass@IP:5432/maria_db"
gh secret set SECRET_KEY "$(openssl rand -base64 32)"
gh secret set ANTHROPIC_API_KEY "sk-ant-..."
gh secret set GOOGLE_AI_API_KEY "AIza..."
gh secret set DEFAULT_LLM_PROVIDER "gemini"
```

### 2. Deploy Automático
O deploy é **totalmente automático**:

1. **Trigger**: Push para branch `main`
2. **Build**: Docker image multi-stage otimizado
3. **Push**: Image para Artifact Registry
4. **Deploy**: Atualização do Cloud Run service
5. **Health Check**: Validação automática

### 3. Deploy Manual (se necessário)
```bash
# Build e push manual
docker build -t us-central1-docker.pkg.dev/PROJECT/maria-backend:latest .
docker push us-central1-docker.pkg.dev/PROJECT/maria-backend:latest

# Deploy manual
gcloud run deploy maria-backend \
  --image us-central1-docker.pkg.dev/PROJECT/maria-backend:latest \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --allow-unauthenticated
```

## 📊 Configurações de Produção

### Cloud Run Service
- **CPU**: 1 vCPU
- **Memory**: 2GB RAM (otimizado para ML models)
- **Timeout**: 300 segundos (5 minutos)
- **Concurrency**: 10 requisições simultâneas
- **Scaling**: 0-10 instâncias
- **Minimum instances**: 0 (economia)
- **Maximum instances**: 10

### Environment Variables
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `ALLOWED_ORIGINS`: Configurado via `FRONTEND_URL`
- Modelos ML: `intfloat/multilingual-e5-base`
- Chunking: 512 tokens, 50 overlap

## 💰 Otimização de Custos ($300 grátis)

### Cloud Run (Pay-per-use)
- **Free tier**: 180,000 vCPU-seconds/mês
- **Memory**: 2GB × tempo de uso
- **Zero custo quando sem tráfego** (min-instances: 0)

### Cloud SQL PostgreSQL
- **db-f1-micro**: ~$15/mês (free tier aplicável)
- **Storage**: 10GB SSD incluídos
- **Connections**: Ilimitadas

### Estimativa Mensal (tráfego moderado)
- Cloud Run: ~$20-50
- Cloud SQL: ~$15
- Artifact Registry Storage: ~$5
- **Total**: ~$40-70/mês (dentro dos $300 grátis)

## 🔍 Monitoramento e Logs

### Health Checks
- `/health`: Health check básico
- `/ready`: Readiness check com dependências
- Monitoramento automático via Cloud Logging

### Logs em Tempo Real
```bash
# Ver logs do serviço
gcloud logs read "resource.type=cloud_run_revision" --limit 50 --follow

# Logs específicos de erros
gcloud logs read "resource.type=cloud_run_revision AND severity>=ERROR" --limit 20
```

### Métricas
- Request count, response time
- Error rate, memory usage
- Disponíveis no Cloud Monitoring (grátis para uso básico)

## 🛠️ Troubleshooting

### Deploy Falha
```bash
# Verificar status do workflow
gh run list --limit 5

# Verificar logs da última execução
gh run view --log

# Verificar serviço Cloud Run
gcloud run services describe maria-backend --region=us-central1
```

### Database Issues
```bash
# Testar conexão com banco
gcloud sql connect maria-db --user=postgres

# Verificar logs do Cloud SQL
gcloud sql instances logs list maria-db
```

### Performance Issues
- Aumentar memory para 4GB se cold starts lentos
- Configurar minimum instances = 1 para baixa latência
- Monitorar cold start time nos logs

## 🔄 Rollback

### Automatic Rollback
Cloud Run mantém versões anteriores:
```bash
# Listar revisões
gcloud run revisions list --service=maria-backend

# Rollback para revisão anterior
gcloud run services update-traffic maria-backend \
  --to-revisions=maria-backend-00002-abc=100
```

### Manual Rollback
```bash
# Deploy versão específica
gcloud run deploy maria-backend \
  --image us-central1-docker.pkg.dev/PROJECT/maria-backend:sha-anterior \
  --region us-central1
```

## 📱 URLs de Acesso

Após deploy bem-sucedido:
- **API**: `https://maria-backend-abcdef.a.run.app`
- **Documentation**: `/docs` e `/redoc`
- **Health Check**: `/health`
- **Ready Check**: `/ready`

## 🔐 Segurança

- ✅ Non-root Docker user
- ✅ Health checks configurados
- ✅ CORS restrito por frontend URL
- ✅ Secrets gerenciados via GitHub
- ✅ Database via Cloud SQL (conexão segura)
- ✅ Rate limiting via Cloud Run

## 🚀 Próximos Passos

1. **Configurar frontend URL** no secret `FRONTEND_URL`
2. **Monitorar custos** no Google Cloud Console
3. **Configurar alertas** (opcional)
4. **Testar integração completa** com frontend
5. **Considerar custom domain** (opcional)

## 📞 Suporte

### Recursos Úteis
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)

### Comandos Úteis
```bash
# Status geral do projeto
gcloud projects describe PROJECT

# Verificar serviços ativos
gcloud run services list

# Verificar custos estimados
gcloud billing accounts list
```

---

**Deploy automatizado configurado com sucesso!** 🎉

Seu backend será automaticamente deployado para Cloud Run em cada push para a branch `main`.