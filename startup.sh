#!/bin/bash

# --- Configuration ---
# Adjust these paths if your folder names differ
CPP_DIR="./cpp_engine"
PY_DIR="./py_ingestor"
CS_DIR="./csharp_processer/LogProcessor"
WEB_DIR="./web_dashboard"

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}   LogStream: Distributed Analytics System     ${NC}"
echo -e "${BLUE}===============================================${NC}"

# 1. Cleanup Function (Runs when you hit Ctrl+C)
cleanup() {
    echo -e "\n${RED}[!] Shutting down all microservices...${NC}"
    # Kill all child processes of this script
    kill $(jobs -p) 2>/dev/null
    wait $(jobs -p) 2>/dev/null
    echo -e "${GREEN}[✓] System stopped.${NC}"
    exit
}
trap cleanup SIGINT

# 2. Check/Start Database (PostgreSQL)
echo -e "${GREEN}[+] Checking PostgreSQL Service...${NC}"
if ! systemctl is-active --quiet postgresql; then
    echo "    PostgreSQL is not running. Attempting to start..."
    sudo systemctl start postgresql
    sleep 2
fi

# 3. Start C++ Search Engine (The Brain)
echo -e "${GREEN}[+] Starting C++ Search Engine (Port 5555 & 5556)...${NC}"
if [ -f "$CPP_DIR/build/engine" ]; then
    "$CPP_DIR/build/engine" > cpp_log.txt 2>&1 &
    CPP_PID=$!
    echo "    Started C++ Engine (PID: $CPP_PID)"
else
    echo -e "${RED}[Error] C++ binary not found in $CPP_DIR/build/engine${NC}"
    exit 1
fi

# DELAY for cpp to catch up
echo -e "${BLUE}    Waiting 2 seconds for C++ to initialize...${NC}"
sleep 2

# 4. Start C# Log Processor (The Worker)
echo -e "${GREEN}[+] Starting C# Processor Service (SQL Ingest)...${NC}"
# Run dotnet in background
(cd "$CS_DIR" && dotnet run) > csharp_log.txt 2>&1 &
CS_PID=$!
echo "    Started C# Service (PID: $CS_PID)"

# 5. Start Python API (The Orchestrator)
echo -e "${GREEN}[+] Starting Python API Gateway (Port 8000)...${NC}"
source "$PY_DIR/venv/bin/activate"
(cd "$PY_DIR" && uvicorn main:app --reload --port 8000) > python_log.txt 2>&1 &
PY_PID=$!
echo "    Started Python API (PID: $PY_PID)"

# 6. Start Angular Dashboard (Optional)
echo -e "${GREEN}[+] Starting Angular Dashboard (Port 4200)...${NC}"
(cd "$WEB_DIR" && ng serve --open) > web_log.txt 2>&1 &
WEB_PID=$!
echo "    Started Angular (PID: $WEB_PID)"

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}   SYSTEM LIVE! Logs are redirecting to *.txt  ${NC}"
echo -e "${BLUE}   Press Ctrl+C to stop the system.            ${NC}"
echo -e "${BLUE}===============================================${NC}"

# Keep script running to maintain the trap
wait