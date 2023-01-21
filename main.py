import os
import psycopg2
from dotenv import load_dotenv
from flask import Flask

CREATE_TRAVEL_PLAN_TABLE = (
    "CREATE TABLE IF NOT EXISTS travel_plan (id INT PRIMARY KEY AUTO_INCREMENT, title TEXT, type TEXT, description TEXT)"
)

#ADD_TRAVEL_DEST = INSERT 

load_dotenv( )

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

@app.get('/')
def home():
    return "GEEEEEESSEEE HUH"

if __name__=="__main__":
    app.run(debug=True)