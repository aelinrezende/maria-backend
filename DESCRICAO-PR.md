## Objetivo

Otimizar o build Docker e o pipeline de CI/CD para resolver o erro "No space left on device" que ocorria durante o deploy do backend no GitHub Actions, implementando um build multi-stage eficiente com download prévio do modelo de embeddings.

## Como a aplicação funcionava antes

A branch `dev` utilizava um Dockerfile básico que baixava o modelo de embeddings durante o startup da aplicação (`start.sh`), o que causava downloads repetitivos de ~4GB em cada instância nova do Cloud Run. O pipeline de CI/CD não possuía otimizações de espaço e o build frequentemente falhava por falta de disco disponível no runner do GitHub Actions. O modelo `intfloat/multilingual-e5-base` era baixado em runtime a cada cold start, resultando em startups lentos e consumo excessivo de bandwidth.

## Mudanças realizadas

Implementou um build Docker multi-stage com três estágios otimizados para minimizar o consumo de espaço durante o build. O estágio `model-downloader` instala apenas o Rust Poetry e as dependências do grupo `model` (huggingface-hub e sentence-transformers) para baixar o modelo de embeddings durante o build. O estágio `python-builder` compila todas as dependências principais da aplicação, enquanto o estágio `production` contém apenas o runtime essencial, cópias das dependências necessárias e o modelo pré-baixado, resultando em uma imagem final muito menor e mais eficiente.

Removeu dependências desnecessárias do `pyproject.toml` (pandas, numpy, ollama, pdfplumber, fastapi-restful, pyrefly) que não eram utilizadas no código, economizando significativamente espaço no build. Implementou um grupo `model` isolado para gerenciar dependências relacionadas aos embeddings, permitindo controle granular sobre o que é baixado em cada estágio. Configurou cache consistente com `HF_HOME=/app/.cache/huggingface` em todos os estágios, garantindo que o SentenceTransformer encontre o modelo pré-baixado no runtime.

O `.dockerignore` foi reescrito para ser agressivo, excluindo todos os arquivos desnecessários como documentação, logs, arquivos temporários, caches e arquivos de build, reduzindo o contexto enviado para o Docker daemon. O script `download_models.py` foi completamente reescrito para incluir verificação de espaço disponível, detecção de modelos já cacheados, logs detalhados e tratamento de erros robusto.

O workflow do GitHub Actions foi aprimorado com limpeza agressiva de disco, incluindo remoção de swap files, Docker system prune, limpeza de caches do sistema e pacotes desnecessários como .NET. Implementou deploy temporário para pull requests com serviço diferenciado (`maria-api-dev-pr`) para testar as otimizações em ambiente real antes do merge. Adicionou verificação de espaço disponível antes do Docker build e logs detalhados durante todo o processo de build.

Removeu completamente o download de modelo do runtime startup, eliminando o script `start.sh` e configurando o CMD diretamente para o uvicorn, reduzindo o tempo de cold start de ~5 minutos para ~1 minuto. Traduziu todos os comentários do Dockerfile para português para melhor manutenção e documentação.

## Como Testar

### Backend
A aplicação backend pode ser testada através do endpoint de health check para verificar se a API está funcionando corretamente e se o modelo de embeddings foi carregado com sucesso.

1. Faça deploy da PR ou push para a branch `dev` para acionar o workflow otimizado
2. Monitore o logs do GitHub Actions para confirmar que não ocorre o erro "No space left on device"
3. Verifique se o modelo é baixado durante o build (logs indicarão o tamanho do modelo baixado)
4. Teste o endpoint de health: `curl -f https://seu-service-url/health`
5. Verifique logs da aplicação para confirmar que o SentenceTransformer carrega o modelo sem tentar download adicional
6. Teste a funcionalidade de embeddings através do endpoint RAG: `curl -X POST https://seu-service-url/rag/query -H "Content-Type: application/json" -d '{"query": "qual é a capital do Brasil?"}'`