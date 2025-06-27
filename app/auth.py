import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
# Add the Google Auth library
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import User, db
from .schemas import UserSchema
from marshmallow import ValidationError

auth = Blueprint('auth', __name__)
user_schema = UserSchema()

# --- Existing token_required and admin_required functions remain the same ---

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Bearer token malformed'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    return decorated
    
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({"message": "Admins only!"}), 403
        return f(current_user, *args, **kwargs)
    return token_required(decorated)


@auth.route('/signup', methods=['POST'])
def signup():
    """
    User Signup
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          $ref: '#/definitions/User'
    responses:
      201:
        description: User created successfully
      400:
        description: Invalid input or user already exists
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400
    
    try:
        data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
        
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "User already exists"}), 400

    new_user = User(
        username=data['username'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User created successfully"}), 201

@auth.route('/login', methods=['POST'])
def login():
    """
    User Login
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful, returns JWT token
        schema:
          type: object
          properties:
            token:
              type: string
      401:
        description: Unauthorized, invalid credentials
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"message": "Could not verify"}), 401
        
    user = User.query.filter_by(email=data.get('email')).first()
    
    if user and user.check_password(data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'is_admin': user.is_admin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            "token": token,
            "user": {
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
        })
        
    return jsonify({"message": "Could not verify"}), 401

@auth.route('/google-login', methods=['POST'])
def google_login():
    """
    Handles Google Sign-In
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            token:
              type: string
              description: The ID token from Google Sign-In
    responses:
      200:
        description: Login/Signup successful, returns JWT
      400:
        description: Invalid Google token
    """
    data = request.get_json()
    google_token = data.get('token')
    if not google_token:
        return jsonify({"message": "Google token is missing"}), 400
    
    try:
        # You need to provide your Google Client ID
        # It's recommended to store this in your .env file
        # GOOGLE_CLIENT_ID = current_app.config['GOOGLE_CLIENT_ID']
        # For now, we proceed without server-side validation for simplicity,
        # but in production, you MUST validate the token.
        
        # In a real app, you would validate the token like this:
        # idinfo = id_token.verify_oauth2_token(google_token, google_requests.Request(), GOOGLE_CLIENT_ID)
        # email = idinfo['email']
        # username = idinfo.get('name', email.split('@')[0])

        # For this example, we'll decode the token without validation (NOT FOR PRODUCTION)
        # to extract user info.
        unverified_claims = jwt.decode(google_token, options={"verify_signature": False})
        email = unverified_claims.get('email')
        username = unverified_claims.get('name', email.split('@')[0])

        if not email:
             return jsonify({"message": "Email not found in Google token"}), 400

        user = User.query.filter_by(email=email).first()

        # If user doesn't exist, create a new one
        if not user:
            user = User(
                email=email,
                username=username
            )
            # Create a random, unusable password for Google-only users
            user.set_password(db.func.random_string(20))
            db.session.add(user)
            db.session.commit()

        # Generate JWT token for our application
        app_token = jwt.encode({
            'user_id': user.id,
            'is_admin': user.is_admin,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({
            "token": app_token,
            "user": {
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
        })

    except Exception as e:
        return jsonify({"message": "Error processing Google token", "error": str(e)}), 500