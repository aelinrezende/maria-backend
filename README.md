# Mar.IA - Backend

Sistema RAG Agentic para fornecer informações seguras para a população trans.

## Sobre o Projeto

Mar.IA é um sistema de inteligência artificial que fornece informações educativas e orientações para a população trans brasileira, focando em três áreas principais:

1. **Riscos e Caminhos Seguros - Automedicação Hormonal**
2. **Retificação de Nome e Gênero em Documentos**
3. **Processo para Acesso a Cirurgias de Afirmação de Gênero via Planos de Saúde**

## Arquitetura

- **Framework**: FastAPI
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Embeddings**: Sentence Transformers
- **LLM**: Claude (Anthropic)
- **Vector Store**: FAISS

## Instalação

### Pré-requisitos

- Python 3.10+
- PostgreSQL
- Redis

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

## Estrutura do Projeto

```
backend/
├── src/backend/
│   ├── core/           # Configurações centrais
│   ├── models/         # Modelos de dados
│   ├── modules/        # Módulos da aplicação
│   │   ├── rag/        # Sistema RAG
│   │   └── user/       # Sistema de usuários
│   ├── services/       # Serviços
│   │   └── embedding_service.py
│   └── utils/          # Utilitários
│       ├── chunking.py
│       └── disclaimers.py
├── tests/              # Testes
├── logs/               # Logs da aplicação
└── pyproject.toml      # Dependências
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
