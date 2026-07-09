# ORCA

ORCA is a minimal Python desktop application scaffold using PySide6 following a clean-architecture layout.

Requirements
- Python 3.12
- PySide6
- SQLAlchemy
- SQLite
- httpx
- loguru
- openpyxl
- pydantic-settings

How to run

1. Create a virtual environment and install dependencies (example using poetry or pip):

   poetry install
   # or
   pip install -r requirements.txt

2. Run the application:

   python main.py

What this initial scaffold provides
- A MainWindow with a dark theme
- Left navigation with Dashboard / Accounts / Settings pages
- A status bar
- Clean architecture folders for future business logic

