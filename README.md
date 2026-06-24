# Stock Predictor — Phase 2 Skeleton

This is the project skeleton from Phase 2 of the build plan. It's intentionally
minimal: just enough wiring to prove the frontend and backend boot and the
folder structure matches our Phase 1 architecture.

## Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/health and http://localhost:8000/docs

## Frontend setup

The `frontend/` folder here has hand-written equivalents of what
`npx create-next-app@latest` generates. For a real project, prefer running
the real scaffolding command instead of copying this folder verbatim:

```bash
npx create-next-app@latest frontend
# Choose: TypeScript=Yes, ESLint=Yes, Tailwind=Yes, src/=Yes, App Router=Yes
```

Then copy `src/app/page.tsx`, `src/app/layout.tsx`, and `src/lib/api.ts`
from this skeleton into the generated project, and:

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

## What's NOT here yet

- Database models (Phase 9)
- Real API endpoints beyond /health (Phase 8)
- Authentication (Phase 12)
- Docker Compose for local Postgres/Redis (introduced when needed)

Each will be added in its corresponding phase of the build plan.
