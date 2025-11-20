#!/usr/bin/env python3
"""
Superset MCP Bridge
Connects Claude Desktop to Apache Superset via Model Context Protocol
"""

import os
import sys
import json
import asyncio
from typing import Any, Optional
from dotenv import load_dotenv
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# Configuration
SUPERSET_BASE_URL = os.getenv("SUPERSET_BASE_URL", "").rstrip("/")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Validate configuration
if not all([SUPERSET_BASE_URL, SUPERSET_USERNAME, SUPERSET_PASSWORD]):
    print("ERROR: Missing required environment variables!", file=sys.stderr)
    print("Please set SUPERSET_BASE_URL, SUPERSET_USERNAME, and SUPERSET_PASSWORD", file=sys.stderr)
    sys.exit(1)


class SupersetClient:
    """Client for interacting with Apache Superset API"""
    
    def __init__(self):
        self.base_url = SUPERSET_BASE_URL
        self.username = SUPERSET_USERNAME
        self.password = SUPERSET_PASSWORD
        self.access_token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=REQUEST_TIMEOUT)
    
    async def authenticate(self) -> bool:
        """Authenticate with Superset and get access token"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/security/login",
                json={
                    "username": self.username,
                    "password": self.password,
                    "provider": "db",
                    "refresh": True
                }
            )
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token is not None
        except Exception as e:
            print(f"Authentication failed: {e}", file=sys.stderr)
            return False
    
    async def request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make authenticated request to Superset API"""
        if not self.access_token:
            await self.authenticate()
        
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Token expired, re-authenticate and retry
                await self.authenticate()
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Initialize Superset client
superset = SupersetClient()

# Initialize MCP server
app = Server("superset-mcp-bridge")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Superset tools"""
    return [
        Tool(
            name="list_dashboards",
            description="List all dashboards in Superset",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_dashboard",
            description="Get details of a specific dashboard by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "dashboard_id": {
                        "type": "integer",
                        "description": "The ID of the dashboard"
                    }
                },
                "required": ["dashboard_id"]
            }
        ),
        Tool(
            name="list_charts",
            description="List all charts in Superset",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_chart",
            description="Get details of a specific chart by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "chart_id": {
                        "type": "integer",
                        "description": "The ID of the chart"
                    }
                },
                "required": ["chart_id"]
            }
        ),
        Tool(
            name="list_datasets",
            description="List all datasets in Superset",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="list_databases",
            description="List all database connections in Superset",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="execute_sql",
            description="Execute a SQL query on a specific database",
            inputSchema={
                "type": "object",
                "properties": {
                    "database_id": {
                        "type": "integer",
                        "description": "The ID of the database to query"
                    },
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["database_id", "sql"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "list_dashboards":
            data = await superset.request("GET", "/api/v1/dashboard/")
            dashboards = data.get("result", [])
            return [TextContent(
                type="text",
                text=json.dumps(dashboards, indent=2)
            )]
        
        elif name == "get_dashboard":
            dashboard_id = arguments["dashboard_id"]
            data = await superset.request("GET", f"/api/v1/dashboard/{dashboard_id}")
            return [TextContent(
                type="text",
                text=json.dumps(data.get("result", {}), indent=2)
            )]
        
        elif name == "list_charts":
            data = await superset.request("GET", "/api/v1/chart/")
            charts = data.get("result", [])
            return [TextContent(
                type="text",
                text=json.dumps(charts, indent=2)
            )]
        
        elif name == "get_chart":
            chart_id = arguments["chart_id"]
            data = await superset.request("GET", f"/api/v1/chart/{chart_id}")
            return [TextContent(
                type="text",
                text=json.dumps(data.get("result", {}), indent=2)
            )]
        
        elif name == "list_datasets":
            data = await superset.request("GET", "/api/v1/dataset/")
            datasets = data.get("result", [])
            return [TextContent(
                type="text",
                text=json.dumps(datasets, indent=2)
            )]
        
        elif name == "list_databases":
            data = await superset.request("GET", "/api/v1/database/")
            databases = data.get("result", [])
            return [TextContent(
                type="text",
                text=json.dumps(databases, indent=2)
            )]
        
        elif name == "execute_sql":
            database_id = arguments["database_id"]
            sql = arguments["sql"]
            data = await superset.request(
                "POST",
                "/api/v1/sqllab/execute/",
                json={
                    "database_id": database_id,
                    "sql": sql,
                    "runAsync": False,
                    "schema": None,
                    "sql_editor_id": "mcp-bridge",
                    "tab": "MCP Bridge",
                    "tmp_table_name": "",
                    "select_as_cta": False,
                    "ctas_method": "TABLE",
                    "queryLimit": 1000,
                    "expand_data": True
                }
            )
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())