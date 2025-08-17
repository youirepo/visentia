#!/bin/bash

# Visentia Stop Script
# This script stops all running server processes

echo "🛑 Stopping Visentia server..."

# Function to check if a process is running
is_process_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Function to kill processes by pattern
kill_processes() {
    local pattern="$1"
    local process_name="$2"
    
    if is_process_running "$pattern"; then
        echo "🔄 Stopping $process_name processes..."
        pkill -f "$pattern"
        sleep 2
        
        # Force kill if still running
        if is_process_running "$pattern"; then
            echo "⚠️  Force killing $process_name processes..."
            pkill -9 -f "$pattern"
            sleep 1
        fi
        
        echo "✅ $process_name processes stopped"
    else
        echo "✅ No $process_name processes found"
    fi
}

# Kill any existing Node.js processes related to this project
kill_processes "npm run dev" "development server"
kill_processes "npm start" "production server"
kill_processes "node.*server" "Node.js server"
kill_processes "tsx.*server" "TypeScript server"

# Check if port 3000 is still in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 3000 is still in use, freeing it..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo "✅ Port 3000 freed"
fi

echo ""
echo "🎉 All Visentia processes have been stopped!"
echo "💡 Run './launch.sh' to start the server again"
