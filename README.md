# Justice Link Kenya - Backend API 🇰🇪

This is the backend server for the **Justice Link Kenya** platform. It is a Flask-based REST API that handles user authentication, data storage, and business logic for incident reports and news articles.

---

## 🛠️ Tech Stack

| Area           | Technology                                  |
|----------------|---------------------------------------------|
| **Framework**  | Python, Flask                               |
| **Database**   | SQLAlchemy (ORM), Flask-Migrate             |
| **Authentication** | JWT (JSON Web Tokens), Flask-Bcrypt    |
| **API Docs**   | Flasgger (Swagger UI)                       |
| **CORS**       | Flask-CORS                                  |
| **Dependencies** | `requirements.txt`                       |

---

## 📋 Prerequisites

- Python (v3.8 or later)  
- pip (Python package installer)

---

## 🚀 Setup and Installation

Follow these steps to get your backend development environment set up.

### 1. Navigate to the Backend Folder

cd path/to/your/backend

# Create the environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

#Installing dependencies
pip install -r requirements.txt

# (Run these commands only once for initial setup)
-flask db init
-flask db migrate -m "Initial migration."
-flask db upgrade

## 2. 👮 Create an Admin User
The application includes a command to grant admin privileges to an existing user.

First, register a new user through the frontend application's sign-up page.

Then run the following command in your backend terminal, replacing the email:

flask create-admin "your-admin-email@example.com"

## ▶️ Running the Backend Server
To start the Flask API server, run:

python run.py
The API will be running and accessible at:


http://127.0.0.1:5000

## 📄 API Documentation
This project uses Flasgger to automatically generate interactive API docs (Swagger UI). Once the server is running, visit:

http://127.0.0.1:5000/apidocs/

to view and test all available endpoints.

