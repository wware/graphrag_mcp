#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")"

# Run the MCP server
"$(dirname "$0")/.venv/bin/python" "$(dirname "$0")/server.py" 