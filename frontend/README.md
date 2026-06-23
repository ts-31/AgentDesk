# TeamFlow Frontend

This is the React + Vite frontend for TeamFlow, integrated directly with the FastAPI backend.

## Architecture & Integration

The frontend connects to the backend via a centralized API client (`src/api/client.ts`).
* **Auth**: Uses JWTs stored in `localStorage`. The API client automatically attaches `Bearer` tokens and handles silent token refreshes via the `/auth/refresh` endpoint on 401s.
* **Proxy**: During development, Vite is configured (`vite.config.ts`) to proxy all requests starting with `/api` to `http://127.0.0.1:8000`. This prevents CORS issues and keeps API paths clean.

## Run Locally

**Prerequisites:** Node.js, and the TeamFlow backend must be running on port 8000.

1. Ensure the backend is running (`uvicorn app:app --reload --port 8000` from the backend dir).
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the dev server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000`. You can log in using the mock credentials seeded by the backend (`seed.py`).
