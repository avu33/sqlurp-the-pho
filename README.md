SQLurp the Pho — Flask + MySQL

A mini restaurant system with Customers, Menu Items, Orders, Order Details, and Sales.

## Project Timeline & Process
- **Cadence:** Worked asynchronously with a partner in weekly sprints to ship a MySQL database and a Flask/Jinja front end.
- **Feedback loop:** Incorporated TA and peer review feedback at the end of each sprint to refine schema, queries, and UX.
- **What we learned:**
  - Designing a relational schema and seeding real test data.
  - Writing stored procedures and using parameterized queries to mitigate SQL injection risks.
  - Building a unique data view (Order Details) that joins across tables and supports create/update flows.
- **Outcome:** A functioning CRUD app backed by a cloud MySQL instance, with clean routes, reusable SQL, and a demo-ready UI.

## 🎥 Demo
video walkthrough: https://youtu.be/hKtuaQAuawo

## ✨ Features
- CRUD views for Customers, Menu Items, Order Details, and Sales
- Safe DB access via parameterized queries (helps mitigate SQL injection)
- Stored procedures for selected writes (e.g., sp_CreateMenuItem, sp_UpdateMenuItem)
- Clean Jinja templates and simple CSS
- “Reset DB” route to reseed demo data for consistent demos

## 🏗️ Tech Stack
Backend: Python 3, Flask, Jinja
DB Driver: mysql-connector-python
DB: MySQL (cloud instance)
Env: python-dotenv for local .env loading

## 🚀 Quickstart
0) Prerequisites
Python 3.10+
A MySQL database (cloud or local). For cloud (e.g., Aiven), note your:
HOST, PORT, USER, PASSWORD, DATABASE (e.g., defaultdb)

1) Clone & create a venv
python3 -m venv venv
source venv/bin/activate

2) Install dependencies
pip install -r requirements.txt

If requirements.txt isn’t present yet, run pip freeze > requirements.txt and commit it.

3) Configure environment
Create a file named .env in the same folder as app.py:
DATABASE_URL=mysql://<USER>:<PASSWORD>@<HOST>:<PORT>/<DATABASE>
FLASK_APP=app.py

I also included a file called .env.example

Flask auto-loads .env via python-dotenv (the app calls load_dotenv()).

4) (First-time) Create schema / stored procs (optional if already created)
From the project root (where the SQL files live):
# Tables + seed
mysql -h <HOST> -P <PORT> -u <USER> -p --ssl-mode=REQUIRED <DATABASE> < DDL.sql

# Stored procedures (create/update)
mysql -h <HOST> -P <PORT> -u <USER> -p --ssl-mode=REQUIRED <DATABASE> < plsql.sql

5) Run the app
flask run --debug
Open http://127.0.0.1:5000

## 📁 Project Structure (key files)
project/
│  app.py
│  requirements.txt
│  .env.example
│  README.md
│
├─ database/
│   └─ db_connector.py
│
├─ templates/
│   ├─ main.j2
│   ├─ index.j2
│   ├─ customers.j2
│   ├─ orders.j2
│   ├─ menu_items.j2
│   └─ order_details.j2
│
├─ static/
│   └─ style.css
│
├─ DDL.sql        # schema
├─ plsql.sql      # stored procedures
└─ DML.sql        # scratch/test queries