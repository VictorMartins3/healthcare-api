# Healthcare Data Processing API

FastAPI app for managing patient records, clinical notes, and generating AI-powered summaries.

## Running

```bash
docker compose up
```

Server runs on `http://localhost:8000`. Swagger docs at `/docs`.

## Endpoints

**Patients**: `GET /patients` (list), `POST /patients` (create), `GET /patients/{id}`, `PUT /patients/{id}`, `DELETE /patients/{id}`

**Notes**: `POST /patients/{id}/notes`, `GET /patients/{id}/notes`, `DELETE /patients/{id}/notes/{note_id}`

**Summary**: `GET /patients/{id}/summary?audience=clinician` (generates AI summary, works without API key)

**Health**: `GET /health`

## Testing

```bash
docker compose exec db createdb -U postgres healthcare_test
pytest tests/ -v
```

## Tech

FastAPI, SQLAlchemy 2.0 async, PostgreSQL.
