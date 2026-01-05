# Virtual Environment Setup Guide

This project requires Python 3.11+ and a virtual environment for dependency isolation.

## Quick Setup (Windows PowerShell)

```powershell
# Navigate to project directory
cd "d:\Projects\NHS NEPPA Project"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install Sprint 1 dependencies
pip install -r requirements.txt
```

## Quick Setup (Windows CMD)

```cmd
# Navigate to project directory
cd "d:\Projects\NHS NEPPA Project"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate.bat

# Upgrade pip
python -m pip install --upgrade pip

# Install Sprint 1 dependencies
pip install -r requirements.txt
```

## Quick Setup (Linux/Mac)

```bash
# Navigate to project directory
cd /path/to/NHS\ NEPPA\ Project

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install Sprint 1 dependencies
pip install -r requirements.txt
```

## Verification

After activation, verify the environment:

```bash
# Check Python version (should be 3.11+)
python --version

# Check pip version
pip --version

# Verify packages installed
pip list
```

## Deactivation

To deactivate the virtual environment:

```bash
deactivate
```

## Notes

- The `venv` folder should be added to `.gitignore` (if using git)
- Always activate the virtual environment before running scripts
- Install new dependencies with: `pip install package_name==version`
- Update `requirements.txt` after installing new packages: `pip freeze > requirements.txt`

