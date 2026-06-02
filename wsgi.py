"""Pequeño lanzador WSGI usado por el host (gunicorn, render, etc.).
Este archivo importa `app` desde `app.py` y permite ejecutar la
aplicación en modo local con `python wsgi.py`.
"""

from app import app

if __name__ == "__main__":
    # Ejecutar localmente para desarrollo
    app.run()
