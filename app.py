from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from emailverify import send_email
from req import get_weather
import secrets
import random, json
import mysql.connector



app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:adminU$er@localhost/forekast'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
# app.add_url_rule('/sendotpemail', view_func=send_email, methods=['POST'])



class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50),nullable=False)
    lastname = db.Column(db.String(50),nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    default_location = db.Column(db.String(255))
    default_location_two = db.Column(db.String(255))
    default_location_three = db.Column(db.String(255))
    default_location_four = db.Column(db.String(255))


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    # otp = data['otp']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already registered'}), 400
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(firstname = data['firstname'], lastname = data['lastname'], username=data['username'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    # send_email(email,otp)
    return jsonify({'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'message': 'Login successful','login':'true', 'access_token':access_token})
        # return jsonify({'message': 'Login successful','login':'true'})
    else:
        return jsonify({'message': 'Invalid credentials','login':'false'})
    
@app.route('/loginhelp', methods=['POST'])
def loginhelp():
    data = request.get_json()
    otp = data['otp']
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User.query.filter_by(email=data['useremail']).first()
    # email = User.query.filter_by(username=data['email']).first()
    # send_email(email,otp)
    if user:
        user.password = hashed_password
        db.session.commit()
        return jsonify({'message': 'User password updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/sendotpemail', methods=['POST'])
def send_otp_email():
    data = request.get_json()
    user_email = data.get('useremail') or data.get('email')
    otp = data['otp']
    send_email(user_email=user_email, otp=otp)  # Call the send_email function directly
    return jsonify({'message': 'Email verification otp sent'}), 200

@app.route('/getweatherdata', methods=['POST'])
def get_weather_data():
    data = request.get_json()
    city = data["city"]
    state = data["state"]
    country = data["country"]
    weather_response = get_weather(city,state,country)
    return jsonify(weather_response)

@app.route('/dropdowndata')
def get_data():
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT distinct(country_code) FROM cities order by country_code asc;')
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)

@app.route('/dropdowndatastate', methods=['POST'])
def get_datastate():
    api_data = request.get_json()
    country = api_data["country"]
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT distinct(state_code) FROM cities where country_code="{country}" order by state_code asc;')
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)

@app.route('/dropdowndatacity',  methods=['POST'])
def get_datacity():
    api_data = request.get_json()
    state = api_data["state"]
    country = api_data["country"]
    print("state"+state)
    print("country"+country)
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT distinct(name) FROM cities where state_code="{state}" and country_code = "{country}" order by name asc;')
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(data)

@app.route('/getdefaultlocation', methods=['POST'])
def getdefaultlocation():
    api_data = request.get_json()
    username = api_data["username"]
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT default_location FROM user WHERE username="{username}";')
    data = cursor.fetchone()
    cursor.close()
    connection.close()    
    # Check if data is found
    if data:
        default_location_json = data['default_location']
        default_location_data = json.loads(default_location_json)
        location = default_location_data['location']
        city, state, country = location.split(", ")
        default_location = {
            'city': city,
            'state': state,
            'country': country
        }
        return jsonify({'default_location': default_location}), 200
    else:
        return jsonify({'message': 'User not found or default location not set'}), 404
    

@app.route('/getdefaultlocationtwo', methods=['POST'])
def getdefaultlocationtwo():
    api_data = request.get_json()
    username = api_data["username"]
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT default_location_two FROM user WHERE username="{username}";')
    data = cursor.fetchone()
    cursor.close()
    connection.close()    
    # Check if data is found
    if data:
        default_location_json = data['default_location_two']
        default_location_data = json.loads(default_location_json)
        location = default_location_data['location']
        city, state, country = location.split(", ")
        default_location = {
            'city': city,
            'state': state,
            'country': country
        }
        return jsonify({'default_location': default_location}), 200
    else:
        return jsonify({'message': 'User not found or default location not set'}), 404
    
@app.route('/getdefaultlocationthree', methods=['POST'])
def getdefaultlocationthree():
    api_data = request.get_json()
    username = api_data["username"]
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT default_location_three FROM user WHERE username="{username}";')
    data = cursor.fetchone()
    cursor.close()
    connection.close()    
    # Check if data is found
    if data:
        default_location_json = data['default_location_three']
        default_location_data = json.loads(default_location_json)
        location = default_location_data['location']
        city, state, country = location.split(", ")
        default_location = {
            'city': city,
            'state': state,
            'country': country
        }
        return jsonify({'default_location': default_location}), 200
    else:
        return jsonify({'message': 'User not found or default location not set'}), 404
    


@app.route('/getdefaultlocationfour', methods=['POST'])
def getdefaultlocationfour():
    api_data = request.get_json()
    username = api_data["username"]
    connection = mysql.connector.connect(host='localhost', database='forekast', user='root', password='adminU$er')
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f'SELECT default_location_four FROM user WHERE username="{username}";')
    data = cursor.fetchone()
    cursor.close()
    connection.close()    
    # Check if data is found
    if data:
        default_location_json = data['default_location_four']
        default_location_data = json.loads(default_location_json)
        location = default_location_data['location']
        city, state, country = location.split(", ")
        default_location = {
            'city': city,
            'state': state,
            'country': country
        }
        return jsonify({'default_location': default_location}), 200
    else:
        return jsonify({'message': 'User not found or default location not set'}), 404


@app.route('/updatedefaultlocation', methods=['POST'])
def updateDefaultLocation():
    data = request.get_json()
    location_data = data['default_location']
    # Format the location data as JSON
    location_json = json.dumps({"location": location_data})
    user = User.query.filter_by(username=data['username']).first()
    if user:
        user.default_location = location_json 
        db.session.commit()
        return jsonify({'message': 'Default location updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/updatedefaultlocationtwo', methods=['POST'])
def updateDefaultLocationTwo():
    data = request.get_json()
    location_data = data['default_location']
    # Format the location data as JSON
    location_json = json.dumps({"location": location_data})
    user = User.query.filter_by(username=data['username']).first()
    if user:
        user.default_location_two = location_json 
        db.session.commit()
        return jsonify({'message': 'Default location updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/updatedefaultlocationthree', methods=['POST'])
def updateDefaultLocationThree():
    data = request.get_json()
    location_data = data['default_location']
    # Format the location data as JSON
    location_json = json.dumps({"location": location_data})
    user = User.query.filter_by(username=data['username']).first()
    if user:
        user.default_location_three = location_json 
        db.session.commit()
        return jsonify({'message': 'Default location updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/updatedefaultlocationfour', methods=['POST'])
def updateDefaultLocationFour():
    data = request.get_json()
    location_data = data['default_location']
    # Format the location data as JSON
    location_json = json.dumps({"location": location_data})
    user = User.query.filter_by(username=data['username']).first()
    if user:
        user.default_location_four = location_json 
        db.session.commit()
        return jsonify({'message': 'Default location updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


@app.route('/deletedefaultlocation', methods=['POST'])
def deletedefaultlocation():
    data = request.get_json()
    location_data = data['default_location']
    loc = data['loc']
    location_json = json.dumps({"location": location_data})
    user = User.query.filter_by(username=data['username']).first()
    if user:
        if loc == 'one':
            user.default_location = location_json 
            db.session.commit()
        elif loc == 'two':
            user.default_location_two = location_json 
            db.session.commit()
        elif loc == 'three':
            user.default_location_three = location_json 
            db.session.commit()
        elif loc == 'four':
            user.default_location_four = location_json 
            db.session.commit()
        return jsonify({'message': 'Default location updated successfully'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)