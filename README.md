# Mar.IA - Backend

Sistema RAG Agentic para fornecer informações seguras para a população trans.

## Sobre o Projeto

Mar.IA é um sistema de inteligência artificial que fornece informações educativas e orientações para a população trans brasileira, focando em três áreas principais:

1. **Riscos e Caminhos Seguros - Automedicação Hormonal**
2. **Retificação de Nome e Gênero em Documentos**
3. **Processo para Acesso a Cirurgias de Afirmação de Gênero via Planos de Saúde**

## Arquitetura

- **Framework**: FastAPI
- **Banco de Dados**: PostgreSQL com pgvector
- **Embeddings**: Sentence Transformers (intfloat/multilingual-e5-base)
- **LLM**: Claude (Anthropic), Gemini (Google), OpenAI
- **Dependency Injection**: Wireup
- **Logging**: Loguru

## Instalação

### Pré-requisitos

- Python 3.13+
- PostgreSQL com pgvector
- Poetry

### Configuração

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
cp env.example .env
# Editar .env com suas configurações
```

4. **Configurar banco de dados**

```bash
# Criar banco PostgreSQL
createdb maria_db

# Executar migrations (quando implementadas)
# poetry run alembic upgrade head
```

5. **Executar aplicação**

```bash
poetry run uvicorn src.backend.main:app --reload
```

## Endpoints

### RAG

- `POST /rag/query` - Consulta RAG
- `POST /rag/query/stream` - Consulta RAG com streaming
- `GET /rag/embeddings/encode` - Teste de embeddings
- `GET /rag/health` - Health check do RAG
- `GET /rag/disclaimers/test` - Teste de disclaimers

### Geral

- `GET /` - Informações da aplicação
- `GET /health` - Health check geral
- `GET /docs` - Documentação Swagger

## 🚀 Deploy para Produção

### Deploy Automático (Google Cloud Run)

Este projeto está configurado para deploy **totalmente automatizado** via GitHub Actions para Google Cloud Run.

**Documentação completa:** [DEPLOYMENT.md](./DEPLOYMENT.md)

**Setup rápido:**
1. Configure os secrets no GitHub (veja [SECRETS-SETUP.md](./SECRETS-SETUP.md))
2. Faça push para branch `main`
3. Deploy automático acontece em ~5 minutos

**Arquivos de deploy:**
- `.github/workflows/deploy-backend.yml` - GitHub Action
- `Dockerfile` - Multi-stage build otimizado
- `SECRETS-SETUP.md` - Guia de configuração
- `DEPLOYMENT.md` - Documentação completa

### Configuração de Production
- **CPU**: 1 vCPU
- **Memory**: 2GB RAM (otimizado para ML models)
- **Scaling**: 0-10 instâncias (economia)
- **Region**: `us-central1`
- **Database**: PostgreSQL + pgvector via Cloud SQL

### Links Úteis
- Service URL: `https://maria-backend-xxxxx.a.run.app`
- API Documentation: `/docs`
- Health Check: `/health`

## Estrutura do Projeto

```
backend/
├── .github/workflows/   # GitHub Actions (CI/CD)
├── src/backend/
│   ├── core/           # Configurações centrais (DB, settings, validators)
│   ├── modules/        # Módulos de negócio
│   │   ├── auth/       # Autenticação JWT
│   │   ├── document/   # Gestão de documentos
│   │   ├── chunk/      # Processamento de chunks
│   │   └── rag/        # Sistema RAG principal
│   ├── integrations/   # Integrações externas
│   │   ├── llm/        # Interfaces LLM (Claude, Gemini, OpenAI)
│   │   └── embeddings/ # Providers de embeddings
│   └── services/       # Serviços de domínio
├── Dockerfile          # Multi-stage build para produção
├── .dockerignore       # Build otimizado
├── pyproject.toml      # Dependências Poetry
├── SECRETS-SETUP.md    # Configuração de secrets
└── DEPLOYMENT.md       # Guia completo de deploy
```

## Responsabilidade Digital

O sistema implementa várias camadas de responsabilidade digital:

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
- Dados de usuário limitados a nome e email
- Anonimização automática de consultas

## Desenvolvimento

### Adicionando Dependências

```bash
poetry add <package-name>
```

### Executando Testes

```bash
poetry run pytest
```

### Logs

Os logs são salvos em `logs/maria.log` e também exibidos no console.

## Próximos Passos

1. **Sprint 1**: ✅ Fundação - Sistema básico implementado
2. **Sprint 2**: Base de Conhecimento - Coletar dados das 3 áreas
3. **Sprint 3**: RAG Core - Integrar Claude
4. **Sprint 4**: Sistema Agentic - Implementar agentes
5. **Sprint 5**: Interface - Criar frontend
6. **Sprint 6**: Validação - Testes e deploy

## Contribuição

Este é um projeto de TCC. Para contribuições, entre em contato com o autor.

## Licença

Projeto acadêmico - TCC.
