# Architecture

```
                        +---------------------+
                        |       Client        |
                        | (Swagger UI / curl) |
                        +----------+----------+
                                   |
                                   | HTTP (JSON)
                                   v
                        +---------------------+
                        |   FastAPI (main.py) |
                        |   Routers layer     |
                        |  - applications     |
                        |  - reminders        |
                        +----------+----------+
                                   |
                                   v
                        +---------------------+
                        |   Service layer     |
                        |  - application_svc  |
                        |  - reminder_svc     |
                        |  - ai_extractor     |
                        +-----+---------+-----+
                              |         |
                 SQLAlchemy   |         |  optional
                  ORM         |         |
                              v         v
                    +-----------+   +-----------+
                    |  SQLite   |   |  OpenAI   |
                    | (or       |   |  API      |
                    | Postgres) |   | (fallback |
                    +-----------+   | to rules) |
                                    +-----------+
```

## Request flow (paste an email)

```
POST /applications/extract
        |
        v
  ai_extractor.extract_from_email(text)
        |
        +-- OPENAI_API_KEY set?  --yes--> call OpenAI -> parse JSON
        |                                     |
        |                                     +-- on error -> fallback
        |
        +-- no key / on error --> rule-based parser (regex + keywords)
        |
        v
  ExtractedApplication { company, role, status, next_action }
```

## Data model

```
applications 1 ------- * status_events

applications
  id, company, role, location, source, status,
  applied_date, next_action, next_action_date,
  notes, created_at, updated_at

status_events
  id, application_id (FK), old_status,
  new_status, note, created_at
```
