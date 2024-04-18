from flask import Flask
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration (replace these values with your actual database configuration)
db_config = { # Add MYSQL database info
    'host': '',
    'user': '',
    'password': '',
    'database': '',
}

# Establish database connection at the beginning
try:
    # Establish the connection
    db_connection = mysql.connector.connect(**db_config)
    app.config['DB_CONNECTION'] = db_connection

    # Notify on successful connection
    print("Successfully connected to the database!")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    raise SystemExit(1)

# Register routes
with app.app_context():
    from app.routes import login, register_client, register_therapist, insert_survey, therapist_search, therapist_details, schedule_appointment, get_user_appointments, insert_payment
    app.add_url_rule('/login', 'login', login, methods=['POST'])
    app.add_url_rule('/register_client', 'register_client', register_client, methods=['POST'])
    app.add_url_rule('/register_therapist', 'register_therapist', register_therapist, methods=['POST'])
    app.add_url_rule('/insert_survey', 'insert_survey', insert_survey, methods=['POST'])
    app.add_url_rule('/therapist_search', 'therapist_search', therapist_search, methods=['GET'])
    app.add_url_rule('/therapist_details', 'therapist_details', therapist_details, methods=['GET'])
    app.add_url_rule('/schedule_appointment', 'schedule_appointment', schedule_appointment, methods=['POST'])
    app.add_url_rule('/get_user_appointments', 'get_user_appointments', get_user_appointments, methods=['GET'])
    app.add_url_rule('/insert_payment', 'insert_payment', insert_payment, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True, port=8000)
