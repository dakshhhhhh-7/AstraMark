# AstraMark Production Deployment Guide

This guide details how to deploy AstraMark in a production environment using Docker and standard best practices.

## 1. Prerequisites

- **Docker** and **Docker Compose** installed on the host machine.
- Valid **Google Gemini API Key** (for AI features).
- MongoDB instance (included in Docker Compose, or use MongoDB Atlas).

## 2. Configuration Setup

### Backend (.env)
Create a `.env` file in the `backend/` directory (or rely on docker-compose env vars):

```ini
MONGO_URL=mongodb://mongo:27017
DB_NAME=astramark_prod
GOOGLE_API_KEY=your_gemini_api_key_here
CORS_ORIGINS=http://localhost:8080,http://your-domain.com
SECRET_KEY=your_super_secret_key_change_this
```

### Frontend (.env)
Create a `.env.production` file in the `frontend/` directory if you need to override build settings.
To use the Nginx proxying (recommended), leave `REACT_APP_BACKEND_URL` empty.

```ini
REACT_APP_BACKEND_URL=
```

## 3. Deployment with Docker Compose

Running the entire stack is as simple as:

```bash
docker-compose up --build -d
```

This will spin up:
1. **MongoDB** on port `27017`
2. **Backend API** on port `8001` (internal `8000`)
3. **Frontend** on port `8080` (internal `80`)

Access the application at `http://localhost:8080`.

## 4. Production Security & Optimization Checklist

- [ ] **Change the MongoDB URL**: In `docker-compose.yml` or production env, point to a secured MongoDB Atlas instance instead of the local container for data persistence and backup.
- [ ] **HTTPS**: Set up a reverse proxy (like Traefik or another Nginx layer) in front of the frontend container to handle SSL/TLS termination.
- [ ] **Secret Management**: Do not commit `.env` files. Use Docker Swarm secrets or a secrets manager in your deployment pipeline.
- [ ] **CORS**: Update `CORS_ORIGINS` in `backend/.env` to strictly match your production domain.

## 5. Troubleshooting

- **API Connection Failed**: Ensure the frontend is calling the correct URL. If using Nginx proxy, calls should go to `/api/...`. Check Network tab in dev tools.
- **MongoDB Connection Error**: Ensure the `backend` container can resolve the `mongo` hostname.

## 6. Architecture Notes

- The Frontend container builds the React app and serves it via Nginx.
- Nginx is configured to proxy `/api` requests to the Backend container if needed, or you can configure a direct connection.
- The Backend uses `uvicorn` to serve the FastAPI app.
