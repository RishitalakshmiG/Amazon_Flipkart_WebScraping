# 🔧 Installation & Troubleshooting Guide

Complete setup instructions and solutions for common issues.

---

## System Requirements

### Minimum Requirements
- **OS:** Windows, macOS, or Linux
- **Python:** 3.7 or higher
- **RAM:** 500 MB
- **Disk Space:** 50 MB
- **Internet:** Required for web scraping

### Recommended
- **Python:** 3.9 or higher
- **RAM:** 2 GB or more
- **Disk Space:** 100 MB

---

## Installation Steps

### Step 1: Verify Python Installation

Check if Python is installed:
```bash
python --version
```

Expected output: `Python 3.x.x`

#### If Not Installed:

**Windows:**
1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**macOS:**
```bash
brew install python3
```

**Linux:**
```bash
sudo apt-get install python3
```

### Step 2: Navigate to Project

```bash
cd c:\Users\grish\Downloads\amazon_flipkart
```

Or navigate to wherever you extracted the project.

### Step 3: Create Virtual Environment (Recommended)

Virtual environment isolates dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

**What it installs:**
- `requests` (2.31.0) - HTTP library
- `beautifulsoup4` (4.12.0) - HTML parsing
- `openpyxl` (3.1.0) - Excel file creation
- `lxml` (4.9.0) - XML/HTML parsing

**Expected output:**
```
Successfully installed requests beautifulsoup4 openpyxl lxml
```

### Step 5: Verify Installation

Test if everything works:

```bash
python -c "import requests, bs4, openpyxl; print('✓ All dependencies installed')"
```

Expected output: `✓ All dependencies installed`

### Step 6: Run Application

```bash
python main.py
```

You should see the menu!

---

## Troubleshooting

### Issue 1: "python: command not found"

**Cause:** Python not installed or not in PATH

**Solutions:**

**Windows:**
1. Press `Win + R`
2. Type `cmd`
3. Run: `py --version`
4. If works, use `py main.py` instead of `python main.py`

**macOS/Linux:**
```bash
# Try python3 instead
python3 --version
python3 main.py
```

**Permanent Fix:**
- Reinstall Python
- Ensure "Add to PATH" is checked

---

### Issue 2: "ModuleNotFoundError: No module named 'requests'"

**Cause:** Dependencies not installed

**Solution:**
```bash
# Make sure you're in the project directory
cd c:\Users\grish\Downloads\amazon_flipkart

# Install dependencies
pip install -r requirements.txt

# Verify
pip list
```

Should show:
```
requests                2.31.0
beautifulsoup4          4.12.0
openpyxl                3.1.0
lxml                    4.9.0
```

---

### Issue 3: "Permission denied" on Excel file

**Cause:** Excel file locked by another process

**Solutions:**

1. **Close Excel:** If Excel is open, close it completely
2. **Restart Python:** Close and rerun `python main.py`
3. **Delete file:** Remove `output/product_comparison.xlsx`
4. **Wait:** Excel might need time to release lock

**Advanced:**
```bash
# Force delete (Windows)
del /f output\product_comparison.xlsx

# Force delete (macOS/Linux)
rm -f output/product_comparison.xlsx
```

---

### Issue 4: Slow Internet / Timeout Errors

**Cause:** Website slow or connection issue

**Solutions:**

1. **Check Internet:**
   - Test: `ping google.com`
   - Restart router if needed

2. **Increase Timeout:**
   Edit `config.py`:
   ```python
   REQUEST_TIMEOUT = 20  # Increased from 10
   MAX_RETRIES = 5       # Increased from 3
   ```

3. **Use VPN:** Some regions block web scraping
   - Try with VPN if blocked

4. **Try Later:** Website might be busy
   - Wait a few minutes
   - Try again

---

### Issue 5: "No products found" or "Empty results"

**Cause:** Product not available or wrong search term

**Solutions:**

1. **Check Spelling:**
   - "iPhone" not "iphone 15pro"
   - Use exact product names

2. **Be Specific:**
   ```
   GOOD:  "iPhone 15 128GB"
   BAD:   "iPhone"
   
   GOOD:  "HP Pavilion 14"
   BAD:   "Laptop"
   ```

3. **Product Not Available:**
   - Product might not exist on both platforms
   - Try a different product

4. **Check Website:**
   - Manually search on Amazon.in
   - If not there, system can't find it either

---

### Issue 6: "ConnectionError" or "No connection"

**Cause:** Network issue

**Solutions:**

1. **Check Connection:**
   ```bash
   ping google.com
   ```

2. **Check Firewall:** 
   - Ensure Python isn't blocked
   - Check antivirus

3. **Try Different WiFi:**
   - Mobile hotspot
   - Different network

4. **Check Websites:**
   - Open Amazon.in in browser
   - Open Flipkart.com in browser
   - If they load, issue is with app

---

### Issue 7: "UnicodeEncodeError"

**Cause:** Special characters (₹, é, etc.) in terminal

**Solutions:**

1. **Windows:** Change encoding
   ```bash
   chcp 65001
   ```

2. **Restart PowerShell:** 
   - Close and reopen terminal

3. **Use WSL:** 
   - Windows Subsystem for Linux

4. **Upgrade Python:**
   ```bash
   python -m pip install --upgrade python
   ```

---

### Issue 8: Database locked / "Database is locked"

**Cause:** Two instances running simultaneously

**Solutions:**

1. **Close Previous Instance:**
   - Press Ctrl+C in other terminal
   - Wait 2 seconds

2. **Delete Lock File:**
   ```bash
   # Check for lock files
   ls database/
   
   # Delete if exists
   rm database/*.db-wal
   ```

3. **Clear Database:**
   - Option 3 in menu: Clear Database
   - Recreates fresh database

---

### Issue 9: Excel file appears corrupted

**Cause:** Process interrupted during save

**Solutions:**

1. **Delete and Regenerate:**
   ```bash
   rm output/product_comparison.xlsx
   python main.py
   ```

2. **Search Again:**
   - Run a new search
   - Excel file is regenerated

---

### Issue 10: Application crashes on startup

**Cause:** Missing dependencies or corrupted database

**Solutions:**

1. **Reinstall Dependencies:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Clear Database:**
   ```bash
   rm database/price_comparison.db
   python main.py
   ```

3. **Check Logs:**
   ```bash
   cat logs/app.log
   ```

4. **Full Reset:**
   ```bash
   # Remove all generated files
   rm -rf database/
   rm -rf output/
   rm -rf logs/
   
   # Reinstall
   pip install -r requirements.txt
   
   # Run
   python main.py
   ```

---

## Virtual Environment Setup (Detailed)

### Why Use Virtual Environment?

- Isolates project dependencies
- Prevents version conflicts
- Easy to share project
- Easy to remove/manage

### Setup Steps

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# You should see (venv) in terminal

# Install dependencies
pip install -r requirements.txt

# Run project
python main.py

# Deactivate when done
deactivate
```

---

## Updating Dependencies

If you encounter dependency issues:

```bash
# Upgrade pip
pip install --upgrade pip

# Upgrade all packages
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated
```

---

## Checking Installation

### Verify All Components

```bash
# Python version
python --version

# Pip version
pip --version

# Check packages
pip list | grep -E "requests|beautifulsoup4|openpyxl|lxml"

# Test imports
python -c "import requests, bs4, openpyxl, lxml; print('All OK')"

# Check directories
ls -la database/
ls -la output/
ls -la logs/
```

### All Should Return ✅

---

## Running Without Installation (Docker)

If you prefer Docker:

```bash
# Create Dockerfile
docker build -t price-comparison .

# Run
docker run -it price-comparison python main.py
```

---

## Uninstalling / Cleanup

If you want to completely remove:

```bash
# Windows
rmdir /s amazon_flipkart

# macOS/Linux
rm -rf amazon_flipkart

# Or just the database
rm database/price_comparison.db
```

---

## Getting Help

1. **Check Logs:**
   ```bash
   cat logs/app.log
   ```

2. **Test Manually:**
   - Try accessing Amazon.in in browser
   - Try accessing Flipkart.com in browser
   - If they work, issue is specific to app

3. **Verify Network:**
   ```bash
   ping google.com
   ping amazon.in
   ping flipkart.com
   ```

4. **Reset Everything:**
   ```bash
   # Full reset
   pip install --upgrade -r requirements.txt
   rm -rf database/
   rm -rf output/
   python main.py
   ```

---

## System Specific Notes

### Windows

- Use `python` not `python3`
- Use `\` for paths or `\\` in code
- Use `venv\Scripts\activate`
- PowerShell or Command Prompt both work

### macOS

- Use `python3` if Python 2 is default
- Use `/` for paths
- Use `source venv/bin/activate`
- Terminal recommended

### Linux

- Use `python3` typically
- Use `/` for paths
- Use `source venv/bin/activate`
- Bash or Zsh both work

---

## Performance Tips

1. **Use Cache:** Repeat searches are instant
2. **Specific Search:** "iPhone 15 128GB" faster than "phone"
3. **Offline Mode:** Search cached products without internet
4. **Database:** Clean old entries occasionally

---

## Security Notes

- App only reads from websites
- No passwords stored
- No personal data collected
- Respects website terms of service
- No malware or suspicious code

---

## Next Steps

✅ Installation complete?
- Run: `python main.py`
- Read: `QUICKSTART.md`
- Try: First search!

❌ Still having issues?
- Check: logs/app.log
- Read: Troubleshooting section above
- Try: Full reset procedure

---

**Version:** 1.0  
**Status:** Ready to Use ✅
#13-12-25