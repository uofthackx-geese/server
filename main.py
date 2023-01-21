import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask, jsonify, request

CREATE_TRAVEL_PLAN_TABLE = (
    "CREATE TABLE IF NOT EXISTS travel_plan (id SERIAL PRIMARY KEY, title TEXT, type TEXT, country TEXT, city TEXT, description TEXT);"
)

CREATE_USER_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT, password TEXT);"
)

CREATE_MAPPING_TABLE = (
    "CREATE TABLE IF NOT EXISTS mappings (id SERIAL PRIMARY KEY, user_id INT, dest_id INT, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (dest_id) REFERENCES travel_plan(id));"
)

ADD_USER = "INSERT INTO users (username, password) VALUES (%s, %s);"

ADD_TRAVEL_DEST = "INSERT INTO travel_plan (title, type, country, city, description) VALUES (%s, %s, %s, %s, %s) RETURNING id;"

ADD_MAPPING  = "INSERT INTO mappings (user_id, dest_id) VALUES (%s, %s);"

SELECT_ALL_USERS = "SELECT * FROM users;"

SELECT_ALL_USERNAMES = "SELECT username FROM users;"

SELECT_ALL_MAPPINGS = "SELECT * FROM mappings;"

SELECT_ALL_DEST = "SELECT * FROM travel_plan;"

DELETE_ALL_DEST = "DELETE FROM travel_plan;"

DELETE_ALL_USERS = "DELETE FROM users;"

DELETE_ALL_MAP = "DELETE FROM mappings;"

DELETE_DEST = "DELETE FROM travel_plan WHERE id = %s;"

DELETE_MAP = "DELETE FROM mappings WHERE dest_id = %s;"

RESTART_ID = "ALTER SEQUENCE travel_plan_id_seq RESTART WITH 1;"

SELECT_ONE = "SELECT * FROM travel_plan where id = 2;"

DROP_TRAVEL_PLAN = "DROP TABLE travel_plan;"

load_dotenv( )

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get('/')
def home():
    return "COOL GEESE BACKEND :)"

def checkUniqueUser(curr_username: str, cursor) -> bool:
    cursor.execute(SELECT_ALL_USERNAMES)
    response = cursor.fetchall()
    if (len(response) > 0):
        for username in response[0]:
            if (curr_username == username):
                return False
    return True

@app.post('/api/signup')
def signup():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USER_TABLE)
            if (checkUniqueUser(username, cursor) == False):
                return {"type": "FAIL", "message": "username is duplicate"}
            cursor.execute(ADD_USER, (username, password))
        return {"type": "SUCCESS"}

@app.post('/api/add_destination')
def add_destination():
    data = request.get_json()
    title = data["title"]
    type = data["type"]
    country = data["country"]
    city = data["city"]
    desc = data["description"]
    user_id = data["user_id"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TRAVEL_PLAN_TABLE)
            cursor.execute(ADD_TRAVEL_DEST, (title, type, country, city, desc))
            dest_id = cursor.fetchone()[0]
            cursor.execute(CREATE_MAPPING_TABLE)
            cursor.execute(ADD_MAPPING, (user_id, dest_id))
        return {"type": "SUCCESS", "id": dest_id, "message": f"Destination {title} added."}, 201

@app.get('/api/get_all_destinations')
def get_all_dest():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_DEST)
            result = cursor.fetchall()
            return {"type": "SUCCESS", "response": result}

@app.get('/api/get_all_users')
def get_all_users():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_USERS)
            result = cursor.fetchall()
            return {"type": "SUCCESS", "response": result}

@app.get('/api/get_all_mappings')
def get_all_mappings():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_MAPPINGS)
            result = cursor.fetchall()
            return {"type": "SUCCESS", "response": result}

@app.get('/api/select_one')
def get_one():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ONE)
            result = cursor.fetchall()
        return {"type": "SUCCESS", "response": result}, 201

@app.delete('/api/delete_destination')
def delete_dest():
    data = request.get_json()
    dest_id = data["dest_id"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_MAP, (dest_id, ))
            cursor.execute(DELETE_DEST, (dest_id, ))
        return {"type": "SUCCESS"}, 201

@app.delete('/api/drop_travel_plan') # for dev only
def drop_travel_plan():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DROP_TRAVEL_PLAN)
        return {"type": "SUCCESS"}, 201

@app.delete('/api/delete_all_users')
def delete_all_users():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ALL_USERS)
        return {"type": "SUCCESS"}, 201


@app.delete('/api/delete_all_mappings')
def delete_all_map():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ALL_MAP)
        return {"type": "SUCCESS"}, 201

@app.delete('/api/delete_all_destinations')
def delete_all_dest():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_ALL_DEST)
            cursor.execute(RESTART_ID)
        return {"type": "SUCCESS"}, 201

# filter by specific types (namely city and destination)
@app.get('/api/travel_spot')
def filterBy():
    '''
    city TEXT -> City  
    type TEXT -> Destination
    '''
    # ?city=some-value&type=another_value
    city = request.args.get('city')
    destination = request.args.get('type')

    select_city_dest = ""

    if city and destination:
        select_city_dest = f"SELECT * FROM travel_plan WHERE city={city} AND type={destination};"
    elif city:
        select_city_dest = f"SELECT * FROM travel_plan WHERE city={city};"
    elif destination:
        select_city_dest = f"SELECT * FROM travel_plan WHERE type={destination};"

    with connection:
        with connection.cursor() as cursor:
            if len(select_city_dest) > 0:
                cursor.execute(select_city_dest)
                result = cursor.fetchall()
            else:
                result = select_city_dest

    return {"type": "SUCCESS", "response": result}

if __name__=="__main__":
    app.run(debug=True, port=8080)