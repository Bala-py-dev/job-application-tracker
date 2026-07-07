# Job Application Tracker

A simple backend app that keeps all your job applications in one place.

When you apply for jobs, the replies get lost across Gmail, LinkedIn, and company
portals. A week later you cannot remember which company replied, what stage each
application is at, or which ones you still need to follow up on.

This app fixes that. You save each application, it remembers the full history of every
status change, it tells you when to follow up, and it can even read a recruiter email and
fill in the details for you.

---

## In one line

You paste a recruiter email -> the app reads it -> it saves the company, role, and status
-> it reminds you to follow up.

---

## The main file

`main.py` is the **root file**. It starts the whole app. When you run the project, you run
`main.py`. Everything else lives inside the `app/` folder and is used by `main.py`.

---

## Project structure (what each file does)

```
demo/
├── main.py                 <-- START HERE. Runs the app and connects everything.
├── requirements.txt            The list of libraries to install.
├── .env.example                Example settings file (copy it to .env).
├── architecture.md             A simple diagram of how the app works.
├── README.md                   This file.
└── app/
    ├── config.py               App settings (database location, OpenAI key, etc).
    ├── logger.py               Prints clear log messages.
    ├── database.py             Connects to the database.
    ├── models.py               The database tables (Application, StatusEvent).
    ├── schemas.py              The shape of data going in and out of the API.
    ├── utils.py                Small helper for the current time.
    ├── routers/
    │   ├── applications.py     The web addresses for adding/updating applications.
    │   └── reminders.py        The web address for "what should I follow up on".
    └── services/
        ├── application_service.py   The logic for saving and updating applications.
        ├── reminder_service.py      The logic for finding due follow-ups.
        └── ai_extractor.py          Reads an email and pulls out the details.
```

---

## How the project works (in plain words)

1. You send a request to the app (for example: "save this application").
2. The **router** (`app/routers/`) receives the request. Think of it as the front desk.
3. The router passes the work to a **service** (`app/services/`). This is where the real
   logic happens.
4. The service reads or writes to the **database** (`app/models.py`) using the tables.
5. The answer travels back to you.

For reading emails, the `ai_extractor` uses OpenAI **if** you provide a key. If you do not,
it uses a simple built-in parser instead, so the app always works even without a key.

---

## How to run this project

You need Python 3.11 or newer.

**Step 1 — create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**Step 2 — install the libraries**

```bash
pip install -r requirements.txt
```

If this fails with an SSL certificate error (common on office/college networks), use:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Step 3 — copy the settings file**

```bash
copy .env.example .env
```

**Step 4 — start the app**

```bash
uvicorn main:app --reload
```

**Step 5 — open it in your browser**

Go to: http://127.0.0.1:8000/docs

This opens a ready-made web page where you can click every feature and try it. You do not
need any special tool.

---

## How to test it (try it yourself)

Open http://127.0.0.1:8000/docs and try these in order. Each one has a blue "Try it out"
button, then an "Execute" button.

**Test 1 — Is the app alive?**
Open `GET /health`. Expected answer: `{"status": "healthy"}`.

**Test 2 — Read a recruiter email (the AI part)**
Open `POST /applications/extract` and send:
```json
{ "text": "We would like to invite you to an interview at Example Corp for the Backend Developer position." }
```
Expected: it returns `company: Example Corp`, `role: Backend Developer`, `status: interview`.

**Test 3 — Save an application**
Open `POST /applications` and send:
```json
{ "company": "Example Corp", "role": "Backend Developer" }
```
Expected: you get back the saved application with `status: applied` and one history event.

**Test 4 — Move it to the next stage**
Open `POST /applications/1/status` and send:
```json
{ "status": "interview", "note": "Call scheduled" }
```
Expected: the status becomes `interview`, and a second history event appears. This proves
the app keeps a full timeline.

**Test 5 — See all your applications**
Open `GET /applications`. Expected: a list of everything you saved.

**Test 6 — See what to follow up on**
Open `GET /reminders`. Expected: applications whose follow-up date has arrived.

**Test 7 — Check error handling**
Open `GET /applications/999` (an id that does not exist). Expected: a clear `404 Not found`
message instead of a crash.

If all seven behave as described, the project works correctly.

---

## The features

- Add, view, update, and delete job applications.
- Track each application through stages: applied, screening, interview, offer, rejected,
  accepted, withdrawn.
- Keep a full history of every status change.
- Read a recruiter email and auto-fill company, role, and status.
- Get a follow-up reminder list.

---

## The web addresses (API)

| Method | Address | What it does |
|--------|---------|--------------|
| GET | `/health` | Check the app is running |
| POST | `/applications` | Save a new application |
| GET | `/applications` | List all applications (add `?status=interview` to filter) |
| GET | `/applications/{id}` | View one application and its history |
| PATCH | `/applications/{id}` | Update some fields |
| POST | `/applications/{id}/status` | Change status and record it |
| DELETE | `/applications/{id}` | Delete an application |
| POST | `/applications/extract` | Read an email and pull out the details |
| GET | `/reminders` | List follow-ups that are due |

---

## The database (two tables)

- **applications** — the current details of each application.
- **status_events** — one row for every status change, so you always have the full history.

Each application has many status_events (a one-to-many relationship).

---

## Technology used and why

- **Python** — clear and widely used; the language for this role.
- **FastAPI** — builds the API quickly and gives the free `/docs` test page.
- **SQLAlchemy** — talks to the database and works with both SQLite and PostgreSQL.
- **SQLite** — needs zero setup, so the project runs immediately.
- **Pydantic** — checks that incoming data is valid.
- **OpenAI** — reads messy emails into clean data, with a built-in fallback so no key is
  required to run.

---

## Why I chose this problem

I chose it because it is a real frustration I have right now while job hunting, not an idea
from the assignment's example list (the assignment asks not to reuse its examples). Because
the pain is genuine, every design decision came from something I actually needed.
