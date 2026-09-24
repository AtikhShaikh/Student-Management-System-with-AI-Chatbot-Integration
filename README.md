# Student Database Management System — Backend

A modular FastAPI backend for managing student records, with an AI chatbot
(Google Gemini + LangGraph) that can answer natural-language questions
about the database.

Built for the **EWB Courses AI + ML Internship — Final Capstone Project**.

## Features

- Full CRUD API for student records (Create, Read, Update, Delete)
- SQLite database via SQLAlchemy ORM
- Request/response validation with Pydantic
- Auto-generated Swagger docs at `/docs`
- AI chatbot at `POST /chat/` — ask things like *"How many students are there?"*
  or *"How many female students?"*, powered by a small LangGraph workflow
  (intent classification → DB retrieval → Gemini-generated answer)
- Secrets kept out of source code via `.env`

## Project Structure

```
student_management_project/
├── .env.example      # Template for required environment variables
├── .gitignore
├── main.py            # FastAPI app + route definitions
├── database.py        # SQLite engine / session setup
├── models.py           # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── crud.py               # DB helper functions (CRUD + aggregate queries)
├── chatbot.py              # Gemini + LangGraph chatbot workflow
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repo and enter the project folder.**

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your real Gemini API key:
   ```
   GOOGLE_API_KEY=your_actual_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
   Get a key from [Google AI Studio](https://aistudio.google.com/apikey).
   **Never commit your real `.env` file** — it's already in `.gitignore`.

4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

5. **Open the interactive API docs:**
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

   The SQLite database file (`students.db`) is created automatically on first run.

## API Overview

| Method | Endpoint            | Description                     |
|--------|----------------------|----------------------------------|
| GET    | `/`                   | Health check                    |
| POST   | `/students/`           | Create a student                |
| GET    | `/students/`             | List all students               |
| GET    | `/students/{id}`          | Get one student                 |
| PUT    | `/students/{id}`           | Update a student                |
| DELETE | `/students/{id}`            | Delete a student                |
| POST   | `/chat/`                     | Ask the AI chatbot a question   |

### Example: create a student
```bash
curl -X POST http://127.0.0.1:8000/students/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Asha Rao", "age": 21, "gender": "Female", "course": "AI/ML", "grade": 8.7, "email": "asha@example.com"}'
```

### Example: chat with the AI
```bash
curl -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"question": "How many students are there?"}'
```

## Chatbot Architecture

```
User question
     │
     ▼
[classify_intent]   -- Gemini turns the question into a structured intent
     │                 (count_all / count_by_gender / average_grade /
     │                  students_by_course / unknown)
     ▼
[retrieve_data]     -- Runs the matching SQL query via crud.py
     │
     ▼
[generate_answer]   -- Gemini phrases the retrieved data as a natural
     │                 language answer
     ▼
  Final answer
```

Keeping the LLM out of writing raw SQL directly (it only picks an intent
from a fixed set) keeps responses predictable and avoids SQL-injection-style
risks from freeform generated queries.

## Notes on the Vector Database Requirement

This project's chatbot currently answers structured/aggregate questions
(counts, averages, filtering by course) directly against the relational
database, which doesn't require semantic/similarity search. If your
use case is extended to include **semantic search over unstructured text**
(e.g. searching free-text student notes, essays, or feedback), a vector
database such as **ChromaDB** (lightweight, easy local setup, good for a
capstone-scale project) would be added at that point to store embeddings
and support similarity search, with Gemini used to summarize or answer
using the retrieved text chunks.

## Interview / Revision Notes

- **Why modular structure?** Separates concerns (DB setup, models, schemas,
  business logic, API routes) so the code is easier to test, maintain, and
  extend.
- **How are secrets managed?** Via a `.env` file loaded with `python-dotenv`,
  never committed to version control.
- **CRUD** = Create, Read, Update, Delete — the four core operations this
  API implements for student records.
