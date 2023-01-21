import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, request

# SQL QUERIES

CREATE_TRAVEL_PLAN_TABLE = (
    "CREATE TABLE IF NOT EXISTS travel_plan (id SERIAL PRIMARY KEY, title TEXT, type TEXT, description TEXT);"
)

ADD_TRAVEL_DEST = "INSERT INTO travel_plan (title, type, description) VALUES (%s, %s, %s) RETURNING id;"

SELECT_ALL = "SELECT * FROM travel_plan;"

DELETE_ALL = "DELETE FROM travel_plan;"

RESTART_ID = "ALTER SEQUENCE travel_plan_id_seq RESTART WITH 1"

load_dotenv( )

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get('/')
def home():
    return "COOL GEESE BACKEND :)"

@app.post('/api/add_destination')
def add_destination():
    data = request.get_json()
    title = data["title"]
    type = data["type"]
    desc = data["description"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TRAVEL_PLAN_TABLE)
            cursor.execute(ADD_TRAVEL_DEST, (title, type, desc))
            dest_id = cursor.fetchone()[0]
        return {"type": "SUCCESS", "id": dest_id, "message": "Destination {title} added."}, 201

@app.post('/api/get_all')
def get_all():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL)
            result = cursor.fetchall()
            return {"type": "SUCCESS", "response": result}

@app.post('/api/delete_all')
def delete_all():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ALL)
            cursor.execute(RESTART_ID)
        return {"type": "SUCCESS"}, 201

if __name__=="__main__":
    app.run(debug=True)