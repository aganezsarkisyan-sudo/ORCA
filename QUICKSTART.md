# 🚀 ORCA Quick Start Guide

## Fastest Way to Run

### Windows
Simply double-click: `setup.bat`

### macOS / Linux
```bash
chmod +x setup.sh
./setup.sh
```

## What the setup script does:
1. ✓ Checks if Python 3.11+ is installed
2. ✓ Creates a virtual environment (`venv`)
3. ✓ Installs all dependencies from `requirements.txt`
4. ✓ Launches the application

## If you prefer manual setup:

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the App
```bash
python main.py
```

## Troubleshooting

### "Python not found"
- Install Python 3.11+ from https://www.python.org
- Make sure Python is added to PATH

### "Permission denied" (Linux/macOS)
```bash
chmod +x setup.sh
./setup.sh
```

### "ModuleNotFoundError"
Make sure your virtual environment is activated:
- Windows: `venv\Scripts\activate`
- Linux/macOS: `source venv/bin/activate`

### Application won't start
Try running with verbose output:
```bash
python main.py --debug
```

## Dependencies
- **PySide6**: Desktop UI framework
- **SQLAlchemy**: Database ORM
- **httpx**: HTTP client
- **loguru**: Logging
- **openpyxl**: Excel support
- **pydantic-settings**: Configuration management
- **qasync**: Async/await for Qt

---

**Need help?** Check the main [README.md](README.md)
