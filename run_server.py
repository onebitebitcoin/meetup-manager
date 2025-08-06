#!/usr/bin/env python
import os
import sys
import subprocess

def run_server():
    # Activate virtual environment and run Django server
    venv_python = os.path.join('venv', 'bin', 'python')
    
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt")
        return
    
    try:
        subprocess.run([venv_python, 'manage.py', 'runserver', '0.0.0.0:8000'], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error running server: {e}")

if __name__ == '__main__':
    run_server()