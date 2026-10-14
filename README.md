# University Research Opportunity Portal



**Program:** BS (CS 5B)   
**University:** National University of Computer & Emerging Sciences (NUCES)

**Student Name:** Wasi kamal 
**Registration No:** 24P-0743

A web application where faculty members can post, view, update, close and delete research opportunities.

- **Backend:** Python + Flask REST API (PyMySQL for the database)
- **Database:** MySQL
- **Frontend:** HTML, JavaScript, Bootstrap 5 (served by the same Flask server)

GitHub Repository: https://github.com/wasi765/research-opportunity-portal

## Project structure

```
app.py                  Flask app: all API routes + serves the frontend
db.py                   MySQL connection
validation.py           Input validation
requirements.txt        Python packages
public/index.html, app.js   Frontend
database/schema.sql     Database setup
postman/                Exported Postman collection
.env.example            Template for your private .env file
```

## Setup and run (Windows)

1. Install **Python 3.10+** (tick "Add Python to PATH") and **MySQL** (e.g. XAMPP).
2. Open the project folder in a terminal and create a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install the packages:
   ```
   pip install -r requirements.txt
   ```
4. Start MySQL, then create the database by running `database/schema.sql`
   (phpMyAdmin -> SQL tab -> paste -> Go).
5. Copy `.env.example` to `.env` and write your MySQL password in it.
6. Start the server:
   ```
   python app.py
   ```
7. Open **http://localhost:3000** in the browser. The API is at `http://localhost:3000/api/opportunities`.

## API endpoints

| Method | URL | Description | Success code |
|--------|-----|-------------|--------------|
| POST   | /api/opportunities     | Create an opportunity | 201 |
| GET    | /api/opportunities     | Get all opportunities | 200 |
| GET    | /api/opportunities/:id | Get one opportunity   | 200 |
| PUT    | /api/opportunities/:id | Update (partial updates allowed, e.g. only `status`) | 200 |
| DELETE | /api/opportunities/:id | Delete an opportunity | 200 |

Error codes: `400` invalid/missing data or bad ID, `404` opportunity not found, `500` server/database error.

### Example body (POST)

```json
{
  "title": "Deep Learning for Medical Imaging",
  "description": "Develop CNN models to detect anomalies in X-ray images.",
  "research_area": "Artificial Intelligence",
  "faculty_name": "Dr. Ahmed Khan",
  "department": "Computer Science",
  "required_skills": "Python, PyTorch",
  "positions": 2,
  "deadline": "2026-12-31",
  "status": "Open"
}
```
Error body format:

{ "error": "Human readable message", "details": ["field x is required"] }
Example: create an opportunity
curl -X POST http://localhost:3000/api/opportunities \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning for Medical Imaging",
    "description": "Deep learning models for early detection of retinal diseases.",
    "research_area": "Artificial Intelligence",
    "faculty_name": "Dr. Ayesha Khan",
    "department": "Computer Science",
    "required_skills": "Python, TensorFlow, CNN",
    "positions_available": 3,
    "application_deadline": "2026-12-15",
    "status": "Open"
  }'
Response — 201 Created:

{
  "id": 1,
  "title": "Machine Learning for Medical Imaging",
  "description": "Deep learning models for early detection of retinal diseases.",
  "research_area": "Artificial Intelligence",
  "faculty_name": "Dr. Ayesha Khan",
  "department": "Computer Science",
  "required_skills": "Python, TensorFlow, CNN",
  "positions_available": 3,
  "application_deadline": "2026-12-15",
  "status": "Open",
  "created_at": "2026-10-07 10:15:00",
  "updated_at": "2026-10-07 10:15:00"
}
Example: close an opportunity (partial update)
curl -X PUT http://localhost:3000/api/opportunities/1 \
  -H "Content-Type: application/json" \
  -d '{ "status": "Closed" }'
Response — 200 OK with the updated object. PUT accepts any subset of fields; an empty body returns 400.

## Testing with Postman

Import `postman/research-portal.postman_collection.json` and run the requests in order (1 to 10).
It covers creating three opportunities, get all, get one, update, close, delete, the 404 after
deletion and a 400 validation error.

## Security note

Database credentials live only in `.env`, which is listed in `.gitignore` and is never uploaded.
