# Troubleshooting: Installing Python Dependencies

If `pip install -r requirements.txt` is not working, try these solutions:

## Solution 1: Update pip first
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Solution 2: Use python -m pip
```bash
python -m pip install -r requirements.txt
```

## Solution 3: Install packages individually
```bash
pip install discord.py
pip install python-dotenv
```

## Solution 4: Use pip3 (on Linux/Mac)
```bash
pip3 install -r requirements.txt
```

## Solution 5: Install with user flag
```bash
pip install --user -r requirements.txt
```

## Solution 6: Use virtual environment (RECOMMENDED)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

## Common Issues and Solutions

### Issue: "pip is not recognized"
- **Windows**: Add Python to PATH or use `python -m pip` instead
- **Linux/Mac**: Install pip with `sudo apt install python3-pip` (Ubuntu/Debian) or `brew install python3` (Mac)

### Issue: "Permission denied"
- Use `pip install --user -r requirements.txt`
- Or run as admin (Windows) / sudo (Linux)

### Issue: "No module named pip"
```bash
python -m ensurepip --upgrade
```

### Issue: discord.py installation fails
- Make sure you have Python 3.8 or higher: `python --version`
- On Linux, install build tools: `sudo apt install python3-dev build-essential`

### Issue: "SSL Certificate error"
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## Verify Installation
After installing, verify with:
```bash
python -c "import discord; print(discord.__version__)"
```

Should output version 2.3.2 or higher.

## Quick Start Without requirements.txt
If you continue having issues, install directly:
```bash
pip install "discord.py>=2.3.2" "python-dotenv>=1.0.0"
```
