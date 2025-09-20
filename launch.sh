#!/bin/bash

# Visentia Launch Script
# This script ensures a clean startup by killing existing processes and restarting the server

echo "🚀 Starting Visentia with clean launch..."

# Function to check if a process is running
is_process_running() {
    pgrep -f "$1" > /dev/null 2>&1
}

# Function to kill processes by pattern
kill_processes() {
    local pattern="$1"
    local process_name="$2"
    
    if is_process_running "$pattern"; then
        echo "🔄 Stopping existing $process_name processes..."
        pkill -f "$pattern"
        sleep 2
        
        # Force kill if still running
        if is_process_running "$pattern"; then
            echo "⚠️  Force killing $process_name processes..."
            pkill -9 -f "$pattern"
            sleep 1
        fi
    else
        echo "✅ No existing $process_name processes found"
    fi
}

# Function to check if port is in use
check_port() {
    local port="$1"
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is still in use, attempting to free it..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Clean up any existing processes
echo "🧹 Cleaning up existing processes..."

# Kill any existing Node.js processes related to this project
kill_processes "npm run dev" "development server"
kill_processes "npm start" "production server"
kill_processes "node.*server" "Node.js server"
kill_processes "tsx.*server" "TypeScript server"

# Check and free port 3000 if needed
check_port 3000

# Wait a moment for processes to fully terminate
sleep 3

# Verify cleanup
if is_process_running "npm run dev" || is_process_running "npm start"; then
    echo "❌ Failed to stop existing processes. Please check manually."
    exit 1
fi

echo "✅ Process cleanup completed"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Check if server directory exists
if [ ! -d "server" ]; then
    echo "❌ Error: server directory not found. Please run this script from the project root."
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "📥 Installing dependencies..."
    npm install
fi

# Set up hybrid visual system if needed
echo "🎨 Checking hybrid visual system..."
if [ ! -d "server/generated-scenes" ] || [ ! -f "server/services/hybrid-visual-generator.py" ]; then
    echo "🔧 Setting up hybrid visual system..."
    ./server/setup-hybrid.sh
fi

# Start the server from the root directory
echo "🚀 Starting development server..."
echo "🔄 Launching server with: npm run dev"
npm run dev &

# Wait a moment for server to start
sleep 5

# Check if server is running
if is_process_running "npm run dev"; then
    echo "✅ Server started successfully!"
    echo "🌐 Application should be available at: http://localhost:3000"
    echo ""
    echo "📋 Server process info:"
    ps aux | grep "npm run dev" | grep -v grep
    echo ""
    echo "🔍 To view logs, run: tail -f server/logs/*.log (if logs exist)"
    echo "🛑 To stop the server, run: pkill -f 'npm run dev'"
else
    echo "❌ Failed to start server. Check for errors above."
    exit 1
fi

# Already in root directory

echo ""
echo "🎉 Launch script completed successfully!"
echo "💡 The server is now running in the background."
echo "🌐 Open your browser and navigate to: http://localhost:3000"
