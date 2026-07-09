# ORCA

ORCA is a minimal Python desktop application scaffold using PySide6 following a clean-architecture layout.

## Requirements
- Python 3.11+
- PySide6
- SQLAlchemy
- SQLite
- httpx
- loguru
- openpyxl
- pydantic-settings
- qasync

## Quick Start (One Command!)

### Windows
```bash
setup.bat
```

### macOS / Linux
```bash
chmod +x setup.sh
./setup.sh
```

## Manual Installation

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. Run the application:

   ```bash
   python main.py
   ```

What this initial scaffold provides
- A MainWindow with a dark theme
- Left navigation with Dashboard / Accounts / Settings pages
- A status bar
- Clean architecture folders for future business logic

