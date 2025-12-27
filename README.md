# MAR.IA - Agentic RAG Backend

![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-green)
![Architecture](https://img.shields.io/badge/Architecture-Clean%20%7C%20Modular-orange)
![Deploy](https://img.shields.io/badge/Deploy-Google%20Cloud%20Run-blueviolet)

**MAR.IA** is an Agentic RAG (Retrieval-Augmented Generation) system designed to provide safe, verified information to the Transgender community in Brazil.

> **🏆 Academic Highlight:** Developed as a Bachelor's Thesis (TCC), this project bridges the gap between advanced AI and social responsibility, focusing on harm reduction (hormone therapy safety) and legal rights (name rectification).

---

## 🏗️ Technical Architecture

This backend is built for **scalability** and **maintainability**, strictly following **SOLID** principles and **Clean Architecture**.

### Core Stack
* **Framework:** FastAPI (Python 3.13+)
* **Database:** PostgreSQL + `pgvector` (Vector Search)
* **ORM:** SQLModel (Type-safe database interaction)
* **Dependency Injection:** `Wireup` (Async DI container)
* **Package Manager:** Poetry

### AI & RAG Pipeline
* **Embeddings:** `intfloat/multilingual-e5-base` (Sentence Transformers)
* **LLM Integration:** Factory Pattern supporting multiple providers (**Claude, Gemini, OpenAI**).
* **Agentic Flow:** The system validates sources *before* generating answers to minimize hallucinations.

---

## 🐛 Module Structure

The codebase follows a **Modular Monolith** approach. Each domain is self-contained:

```text
modules/<domain_name>/
├── <name>_router.py      # FastAPI Endpoints
├── <name>_service.py     # Business Logic & AI Orchestration
├── <name>_repository.py  # Data Access (SQLModel)
└── <name>_dto.py         # Pydantic Models (Validation)

```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.13+
* PostgreSQL (with `vector` extension)
* [Poetry](https://python-poetry.org/)

### Local Setup

1. **Clone the repository**
```bash
git clone [https://github.com/aelinrezende/maria-backend.git](https://github.com/aelinrezende/maria-backend.git)
cd maria-backend

```


2. **Install Dependencies (via Poetry)**
```bash
poetry install

```


3. **Environment Configuration**
```bash
cp .env.template .env
# Edit .env with your local credentials (DB, API Keys)

```


4. **Run the Server**
```bash
poetry run uvicorn app.main:app --reload

```


API Documentation: `http://localhost:8090/docs`

---

## ☁️ DevOps & Deployment (Google Cloud)

The project is fully containerized and deployed on **Google Cloud Run** via GitHub Actions.

### CI/CD Pipeline

1. **Trigger:** Push to `main`.
2. **Build:** Multi-stage Docker build (Optimized image).
3. **Push:** Uploads to Google Artifact Registry.
4. **Deploy:** Updates the Cloud Run Service.
5. **Health Check:** Automatic readiness probe.

### Manual Deploy (Emergency)

```bash
# Build & Push
docker build -t us-central1-docker.pkg.dev/PROJECT/maria-api:latest .
docker push us-central1-docker.pkg.dev/PROJECT/maria-api:latest

# Deploy to Cloud Run
gcloud run deploy maria-api \
  --image us-central1-docker.pkg.dev/PROJECT/maria-api:latest \
  --region us-central1 \
  --memory 2Gi --cpu 1 \
  --allow-unauthenticated

```

### 💰 Cloud Cost Estimation

Designed to run within the Google Cloud Free Tier (or very low cost):

* **Cloud Run:** ~$0 - $20/mo (Pay-per-use)
* **Cloud SQL (Micro):** ~$15/mo
* **Artifact Registry:** ~$5/mo

---

## 👩‍💻 Author

**Aelin Rezende**
*Senior Fullstack Engineer | Computer Scientist*

Building software that matters. Expert in **.NET** and **Python/AI** ecosystems.

[LinkedIn](http://linkedin.com/in/aelin-rezende/)
