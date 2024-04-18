from flask import request, jsonify, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

def get_db():
    if 'db' not in g:
        # Use the database connection stored in the application context
        g.db = current_app.config['DB_CONNECTION'].cursor(dictionary=True)
    return g.db

def close_db(e=None):
    # Close the database connection when the request is finished
    db = g.pop('db', None)
    if db is not None:
        db.close()

def user_exists(email):
    db = get_db()
    db.execute("SELECT id FROM users WHERE email = %s", (email,))
    return db.fetchone() is not None

def login():
    with current_app.app_context():
        # Get user input from request
        name = request.json.get('username')
        password = request.json.get('password')

        # Check if username and password are provided
        if not name or not password:
            return jsonify({"error": "Username and password are required"}), 400

        try:
            # Get database cursor
            db = get_db()

            # Check if the user exists and retrieve the stored hashed password and user ID
            db.execute("SELECT id, password FROM users WHERE name = %s", (name,))
            user = db.fetchone()

            if user:
                # User exists, check the password
                if check_password_hash(user['password'], password):
                    # Login successful, return user ID
                    return jsonify({"message": "Login successful", "user_id": user['id']})
                else:
                    return jsonify({"error": "Invalid password"}), 401
            else:
                return jsonify({"error": "User not found"}), 404

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": "Database error"}), 500

def register_client():
    # Get user input from request
    name = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    # Check if username, password, and email are provided
    if not name or not password or not email:
        return jsonify({"error": "Username, password, and email are required"}), 400

    try:
        # Get database cursor
        db = get_db()

        # Check if the user already exists
        if user_exists(email):
            return jsonify({"error": "User already exists"}), 409

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the new user into the database with hashed password
        db.execute("INSERT INTO users (name, password, email) VALUES (%s, %s, %s)", (name, hashed_password, email))
        current_app.config['DB_CONNECTION'].commit()

        return jsonify({"message": "User successfully registered"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    
def register_therapist():
    # Get user input from request
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    experience = request.form['experience']  # Get years of experience if provided
    specialization = request.form['specialization']  # Get specialization if provided
    on_call1 = request.form['onCall']  # Get on call status if provided
    on_call = '0'
    if on_call1 == 'Yes':
        on_call == '1'
    if on_call1 == 'No':
        on_call == '0'
    # Check if username, password, email, and resume are provided
    if not username or not password or not email:
        return jsonify({"error": "Username, password, and email are required"}), 400

    try:
        # Get database cursor
        db = get_db()

        # Check if the user already exists
        if user_exists(email):
            return jsonify({"error": "User already exists"}), 409

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the new therapist into the database
        db.execute("INSERT INTO therapists (username, password, email, experience, specialization, on_call) VALUES (%s, %s, %s, %s, %s, %s)",
                   (username, hashed_password, email, experience, specialization, on_call,))
        db.execute("SELECT id FROM therapists WHERE email = %s", (email,))
        therapist_id = db.fetchone()['id']
        current_app.config['DB_CONNECTION'].commit()

        return jsonify({"message": "Therapist successfully registered", "therapist_id": therapist_id})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500

    
# insert a therapist survey
def insert_survey(user_id, gender, price, specializations, bio, photo):
    try:
        # Get database cursor
        db = get_db()

        # Insert the survey into the database
        db.execute("INSERT INTO therapistSurvey (user_id, gender, price, specialtizations, bio, photo) VALUES (%s, %s, %s, %s, %s, %s)",
                   (user_id, gender, price, specializations, bio, photo))
        current_app.config['DB_CONNECTION'].commit()

        return jsonify({"message": "Survey successfully inserted"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    
def therapist_search(gender=None, min_experience=None, max_price=None):
    try:
        # Get database cursor
        db = get_db()

        # Construct the SQL query based on provided conditions
        query = """
            SELECT therapists.email, therapists.username, therapists.experience, therapists.specialization,
                   therapistSurvey.gender, therapistSurvey.price, therapistSurvey.photo, therapists.id
            FROM therapists
            INNER JOIN therapistSurvey ON therapists.id = therapistSurvey.user_id
            WHERE 1
        """
        params = []

        if gender:
            query += " AND therapistSurvey.gender = %s"
            params.append(gender)
        if min_experience:
            query += " AND therapists.experience >= %s"
            params.append(min_experience)
        if max_price:
            query += " AND therapistSurvey.price <= %s"
            params.append(max_price)

        db.execute(query, params)
        therapists = db.fetchall()
        
        # Return a list of dictionaries containing therapist information
        return [{'email': therapist['email'],
                 'name': therapist['username'],
                 'years_of_experience': therapist['experience'],  # Consistent variable name
                 'specialization': therapist['specialization'],
                 'gender': therapist['gender'],
                 'price': therapist['price'],
                 'photo': therapist['photo'],
                 'id': therapist['id']
                 } for therapist in therapists]

    except Exception as e:
        print(f"Error: {e}")
        return None

def therapist_details(email):
    try:
        # Get database cursor
        db = get_db()

        # Fetch therapist details including survey details
        query = """
            SELECT t.id, t.username, t.email, t.experience, t.specialization, t.on_call,
                   ts.gender, ts.price, ts.specializations, ts.bio, ts.photo
            FROM therapists AS t
            LEFT JOIN therapistSurvey AS ts ON t.id = ts.user_id
            WHERE t.email = %s
        """
        db.execute(query, (email,))
        therapist_details = db.fetchone()

        return therapist_details

    except Exception as e:
        print(f"Error: {e}")
        return None

def schedule_appointment():
    try:
        # Get database cursor
        db = get_db()
        # Extract data from JSON request body
        data = request.json
        user_id = data.get('user_id')
        therapist_id = data.get('therapist_id')
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        am_pm = data.get('am_pm')

        # Perform any necessary validation on the received data

        # Insert the appointment into the database
        db.execute("""
            INSERT INTO appointments (user_id, therapist_id, appointment_date, appointment_time, am_pm) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, therapist_id, appointment_date, appointment_time, am_pm))

        # Commit the transaction
        current_app.config['DB_CONNECTION'].commit()

        return jsonify({"message": "Appointment successfully scheduled"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to schedule appointment"}), 500

def get_user_appointments():
    try:
        # Extract user_id from query parameters
        user_id = request.args.get('user_id')

        # Get database cursor
        db = get_db()

        # Fetch appointments for the given user_id
        db.execute("""
            SELECT * FROM appointments WHERE user_id = %s
        """, (user_id,))
        appointments = db.fetchall()

        appointment_dates = [appointment['appointment_date'] for appointment in appointments]

        return jsonify(appointment_dates)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Database error"}), 500
    
def insert_payment():
    try:
        # Get database cursor
        db = get_db()
        # Extract payment details from the request
        data = request.json
        user_id = data.get('user_id')
        purpose = data.get('purpose')
        date_posted = data.get('date_posted')  # You may use the current date or the date from PayPal

        # Insert payment into the database
        # Example code assuming you have a database connection (db) established
        db.execute("""
            INSERT INTO payments (user_id, purpose, date_posted) 
            VALUES (%s, %s, %s)
        """, (user_id, purpose, date_posted))

        # Commit the transaction
        db.commit()

        return jsonify({"message": "Payment successfully inserted"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to insert payment"}), 500

# Register close_db to be called after each request
current_app.teardown_appcontext(close_db)
