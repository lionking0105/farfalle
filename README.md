# Farfalle

Open-source AI-powered search engine.

<img width="900" alt="image" src="https://github.com/rashadphz/farfalle/assets/20783686/254d77a6-9e5f-4a95-a50a-d8c66d62cf66">

## 💻 Live Demo

[farfalle.dev](https://farfalle.dev/)

## 📖 Overview

- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Deploy](#deploy)

## 🛠️ Tech Stack

- Frontend: [Next.js](https://nextjs.org/)
- Backend: [FastAPI](fastapi.tiangolo.com/)
- Search API: [Tavily](https://tavily.com/)
- Logging: [Logfire](https://pydantic.dev/logfire)
- Rate Limiting: [Redis](https://redis.io/)
- Components: [shadcn/ui](https://ui.shadcn.com/)

## 🚀 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/en/download/)
- [pnpm](https://pnpm.io/installation) or [npm](https://www.npmjs.com/get-npm)
- [Python](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)

### Get API Keys

- [Tavily](https://app.tavily.com/home)
- [OpenAI](https://platform.openai.com/api-keys)
- [Groq](https://console.groq.com/keys)

### 1. Clone the Repo

```
git clone git@github.com:rashadphz/farfalle.git
```

### 2. Install Dependencies

#### Frontend

```
cd farfalle/src/frontend
pnpm install
```

#### Backend

```
cd farfalle/src/backend
poetry install
```

### 3. Secrets

Create a `.env` file in the root of the project and add these variables:

```
TAVILY_API_KEY=...
OPENAI_API_KEY=...
GROQ_API_KEY=...

# Everything below is optional

# Default (http://localhost:3000)
FRONTEND_URL=

# Logfire
LOGFIRE_TOKEN=

# (True | False)
RATE_LIMIT_ENABLED=

# Redis URL
REDIS_URL=
```

### 4. Run the App Locally

#### Frontend

```
cd farfalle/src/frontend
pnpm dev
```

#### Backend

```
cd farfalle/src/backend
poetry shell
uvicorn backend.main:app --reload
```

Visit [http://localhost:3000](http://localhost:3000) to view the app.

## 🚀 Deploy

### Backend
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/rashadphz/farfalle)

