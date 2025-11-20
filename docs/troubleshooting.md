# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### "uv: command not found"

**Problem:** The `uv` command isn't recognized.

**Solution:**
1. Restart your terminal after installing uv
2. Check if uv is in your PATH:
```bash
   # macOS/Linux
   echo $PATH | grep .cargo/bin
   
   # Windows
   echo %PATH% | findstr cargo
```
3. Manually add to PATH if needed

#### "Multiple top-level modules discovered"

**Problem:** Error during `uv pip install -e .`

**Solution:**
Add this to your `pyproject.toml`:
```toml
[tool.setuptools]
py-modules = ["main"]
```

### Configuration Issues

#### Claude doesn't show the Superset plugin

**Solutions:**
1. **Restart Claude Desktop completely** (quit, don't just close the window)
2. Check config file location:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Verify JSON syntax (use a JSON validator)
4. Check Python path is correct:
```bash
   # Verify your Python path
   # Windows
   .venv\Scripts\python.exe --version
   
   # macOS/Linux
   .venv/bin/python --version
```

#### Windows path issues

**Problem:** Paths with spaces or incorrect slashes.

**Solution:**
- Use double backslashes: `C:\\Users\\Your Name\\...`
- Or use forward slashes: `C:/Users/Your Name/...`
- Avoid spaces by using short path names

### Connection Issues

#### "Connection refused" or "Cannot connect to Superset"

**Solutions:**
1. Verify Superset is running:
```bash
   curl http://your-superset-url/health
```
2. Check if you need VPN access
3. Test in browser first
4. Verify URL in `.env` has no trailing slash
5. Check firewall settings

#### Authentication failures

**Solutions:**
1. Test credentials manually:
```bash
   curl -X POST http://your-superset-url/api/v1/security/login \
     -H "Content-Type: application/json" \
     -d '{"username":"your_user","password":"your_pass","provider":"db"}'
```
2. Check for special characters in password (may need escaping)
3. Verify user has appropriate Superset permissions
4. Try creating a dedicated service account

### Runtime Issues

#### "ModuleNotFoundError"

**Problem:** Python can't find required modules.

**Solution:**
```bash
# Reinstall dependencies
uv pip install -e .

# Or install individually
uv pip install mcp httpx python-dotenv
```

#### "Permission denied" errors in Superset

**Problem:** User doesn't have access to requested resources.

**Solution:**
1. Check user permissions in Superset Admin > Security
2. Ensure user has at least "Gamma" role
3. For specific datasets/dashboards, grant explicit permissions
4. Consider creating a dedicated "MCP Service" role

#### Tool calls timing out

**Problem:** Queries take too long or timeout.

**Solution:**
1. Increase timeout in `.env`:
```bash
   REQUEST_TIMEOUT=60
```
2. Check if Superset database is slow
3. Simplify queries or limit result sets
4. Check network latency

### Platform-Specific Issues

#### macOS: "Operation not permitted"

**Solution:**
Grant terminal access in System Preferences > Security & Privacy > Privacy > Files and Folders

#### Windows: "Access is denied"

**Solutions:**
1. Run terminal as Administrator
2. Check antivirus isn't blocking Python
3. Verify folder permissions

#### Linux: "Symbol not found" errors

**Solution:**
```bash
# Install required system libraries
sudo apt-get update
sudo apt-get install python3-dev libssl-dev
```

### Debugging Tips

#### Enable debug logging

Add to your `.env`:
```bash
DEBUG=true
```

#### Check Claude Desktop logs

- **macOS:** `~/Library/Logs/Claude/`
- **Windows:** `%APPDATA%\Claude\logs\`

#### Test the bridge directly
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Run main.py directly
python -m main
```

#### Verify environment variables
```bash
# Check if .env is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('SUPERSET_BASE_URL'))"
```

