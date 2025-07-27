# WSGI Configuration for PythonAnywhere Deploy

"""
WSGI file for PUCRS Gamification System deployment on PythonAnywhere
This file should be used as the WSGI configuration in PythonAnywhere web app setup
"""

import sys
import os
from pathlib import Path

# Add the project directory to Python path
username = "seuusuario"  # Replace with your PythonAnywhere username
project_path = f'/home/{username}/pucrs-gamification'

if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Add the backend directory specifically
backend_path = f'{project_path}/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set environment variables for production
os.environ.setdefault('MONGO_URL', 'mongodb+srv://edsonvivo2020:<db_password>@cluster0.dc0orfj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
os.environ.setdefault('DB_NAME', 'pucrs_gamification')
os.environ.setdefault('SECRET_KEY', 'sua_chave_jwt_super_segura_256_bits_2025')

# Import the FastAPI application
import_error = None
try:
    from backend.server import app
    application = app
    print("PUCRS Gamification System loaded successfully!")
except ImportError as import_err:
    import_error = import_err
    print(f"Error importing application: {import_error}")
    # Create a simple error application
    def application(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/html')]
        start_response(status, response_headers)
        error_msg = f'<h1>Import Error</h1><p>{str(import_error)}</p>'
        return [error_msg.encode('utf-8')]

# Debug information (will appear in error logs)
print(f"Python path: {sys.path}")
print(f"Environment variables: MONGO_URL set: {'MONGO_URL' in os.environ}")
print(f"Project path: {project_path}")
print(f"Backend path: {backend_path}")
