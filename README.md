# Superset MCP Bridge

🤖 **Connect Apache Superset to Claude Desktop** - Ask questions about your data in natural language!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## What is This?

This MCP (Model Context Protocol) bridge allows you to connect Claude Desktop to your Apache Superset instance. Ask data questions in plain English and get instant answers from your dashboards and datasets.

**Example queries:**
- "Show me all available dashboards"
- "What were Q3 sales by region?"
- "List all datasets in the Finance database"
- "Execute this SQL: SELECT * FROM users LIMIT 10"

## Features

✅ **Secure** - All queries respect Superset's RBAC and RLS  
✅ **Local** - Runs on your machine, connects to internal Superset  
✅ **Fast** - Get answers in seconds, not minutes  
✅ **Easy** - 15-minute setup with step-by-step instructions  

## Quick Start

### Prerequisites

- Apache Superset instance (accessible via HTTP/HTTPS)
- Claude Desktop installed ([Download here](https://claude.ai/download))
- Python 3.10 or higher
- Basic command line knowledge

### Installation

**1. Install uv (Python package manager):**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone this repository:**
```bash
git clone https://github.com/YOUR_USERNAME/superset-mcp-bridge.git
cd superset-mcp-bridge
```

**3. Create virtual environment and install dependencies:**
```bash
uv venv
uv pip install -e .
```

**4. Configure environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Superset credentials
# (Use your favorite text editor)
```

Edit `.env` to include:

SUPERSET_BASE_URL=https://your-superset-instance.com
SUPERSET_USERNAME=your_username
SUPERSET_PASSWORD=your_password

**5. Configure Claude Desktop:**

Locate your Claude Desktop config file:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add this configuration (adjust paths for your system):

**For Windows:**
```json
{
  "mcpServers": {
    "superset": {
      "command": "C:\\Users\\YOUR_USERNAME\\superset-mcp-bridge\\.venv\\Scripts\\python.exe",
      "args": ["-m", "main"],
      "env": {
        "SUPERSET_BASE_URL": "https://your-superset-instance.com",
        "SUPERSET_USERNAME": "your_username",
        "SUPERSET_PASSWORD": "your_password"
      }
    }
  }
}
```

**For macOS/Linux:**
```json
{
  "mcpServers": {
    "superset": {
      "command": "/Users/YOUR_USERNAME/superset-mcp-bridge/.venv/bin/python",
      "args": ["-m", "main"],
      "env": {
        "SUPERSET_BASE_URL": "https://your-superset-instance.com",
        "SUPERSET_USERNAME": "your_username",
        "SUPERSET_PASSWORD": "your_password"
      }
    }
  }
}
```

**6. Restart Claude Desktop**

Completely quit and restart Claude Desktop for the configuration to take effect.

**7. Test the connection**

In Claude Desktop, look for the 🔌 plugin icon. You should see a green indicator next to "superset".

Try asking Claude:

"List all available dashboards in Superset"

## Usage Examples

Once connected, you can ask Claude natural language questions about your Superset data:

### Dashboards
- "Show me all my dashboards"
- "Get details of dashboard with ID 5"
- "Create a new dashboard called 'Sales Overview'"

### Charts
- "List all charts in Superset"
- "Show me chart with ID 10"
- "Create a bar chart from dataset 3"

### Datasets & Databases
- "What datasets are available?"
- "Show me tables in database 1"
- "List all connected databases"

### SQL Queries
- "Execute: SELECT * FROM users LIMIT 10"
- "Format this SQL: SELECT id,name FROM users WHERE active=1"
- "Validate SQL: SELECT COUNT(*) FROM orders"

## Available Tools

This bridge provides Claude with access to these Superset operations:

**Authentication:**
- Check token validity
- Refresh authentication token

**Dashboards:**
- List, get, create, update, delete dashboards

**Charts:**
- List, get, create, update, delete charts

**Databases:**
- List, get, create, update, delete database connections
- Get tables, schemas, catalogs
- Test connections
- Validate SQL

**Datasets:**
- List, get, create datasets

**SQL Lab:**
- Execute queries
- Format SQL
- Get query results
- Estimate query costs
- Export results

**User & Admin:**
- Get current user info
- Get user roles
- View recent activity
- Manage tags

## Security

🔒 **This bridge is designed with security in mind:**

- **No training data:** Your data is NOT used to train AI models
- **RBAC enforced:** All Superset permissions are fully respected
- **Local execution:** Bridge runs on your machine
- **Internal connections:** Connects directly to your internal Superset
- **No data storage:** Bridge is stateless, stores no data
- **Credential control:** You manage all credentials locally

**Security Best Practices:**
- Use environment variables for credentials (never hardcode)
- Use a dedicated Superset service account with minimal permissions
- Keep credentials in `.env` (already in `.gitignore`)
- For production, consider using a secrets manager
- Rotate credentials regularly

## Troubleshooting

### "Multiple top-level modules discovered" error

Add this to your `pyproject.toml`:
```toml
[tool.setuptools]
py-modules = ["main"]
```

### Authentication failures

1. Verify credentials in `.env` file
2. Ensure Superset is accessible at the URL specified
3. Check that username has appropriate permissions
4. Try logging in to Superset manually with the same credentials

### Claude doesn't show the plugin

1. Ensure you completely restarted Claude Desktop
2. Check that paths in `claude_desktop_config.json` are correct
3. On Windows, ensure backslashes are doubled (`\\`)
4. Verify Python path points to virtual environment's Python

### "Connection refused" errors

1. Verify Superset is running
2. Check firewall settings
3. If using VPN, ensure you're connected
4. Test Superset URL in a browser

### Permission denied errors

The Superset user account needs appropriate permissions. Verify in Superset's Security settings.

For more troubleshooting, see [docs/troubleshooting.md](docs/troubleshooting.md)

## System Requirements

- **Python:** 3.10 or higher
- **OS:** Windows 10+, macOS 11+, or Linux
- **Memory:** 512MB RAM minimum
- **Network:** Access to your Superset instance
- **Claude Desktop:** Latest version

## Architecture

┌─────────────────┐
│  Claude Desktop │
│   (Local AI)    │
└────────┬────────┘
│ MCP Protocol
▼
┌─────────────────┐
│  MCP Bridge     │
│  (Python)       │
│  - main.py      │
└────────┬────────┘
│ Superset REST API
│ (Authenticated)
▼
┌─────────────────┐
│  Superset       │
│  Instance       │
│  (Your Server)  │
└─────────────────┘

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Inspired by [aptro/superset-mcp](https://github.com/aptro/superset-mcp)
- Powered by [Apache Superset](https://superset.apache.org/)
- Uses [Anthropic's Claude](https://www.anthropic.com/claude)

## Support

- 📖 [Full Documentation](docs/)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/superset-mcp-bridge/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/superset-mcp-bridge/discussions)

## Related Projects

- [aptro/superset-mcp](https://github.com/aptro/superset-mcp) - Original Superset MCP implementation
- [Model Context Protocol](https://github.com/modelcontextprotocol) - MCP specification
- [Claude Desktop](https://claude.ai/download) - AI assistant

---

**Made with ❤️ for the data community**