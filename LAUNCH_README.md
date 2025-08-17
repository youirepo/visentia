# 🚀 Visentia Launch Scripts

This directory contains convenient scripts to manage your Visentia application server.

## 📁 Scripts

### `launch.sh` - Start the Application
A comprehensive script that ensures a clean startup by:
- 🧹 Cleaning up any existing server processes
- 🔌 Freeing port 3000 if it's in use
- 📦 Installing dependencies if needed
- 🚀 Starting the development server
- ✅ Verifying the server is running properly

### `stop.sh` - Stop the Application
A simple script that:
- 🛑 Stops all running server processes
- 🔌 Frees port 3000
- ✅ Confirms all processes are terminated

## 🎯 Usage

### Starting the Application
```bash
# Make sure you're in the project root directory
cd /path/to/Visentia

# Run the launch script
./launch.sh
```

### Stopping the Application
```bash
# Stop all server processes
./stop.sh
```

### Manual Process Management
If you need to manually manage processes:

```bash
# Check what's running
ps aux | grep "npm run dev"

# Stop the development server
pkill -f "npm run dev"

# Force stop if needed
pkill -9 -f "npm run dev"

# Check if port 3000 is free
lsof -i :3000
```

## 🔧 What the Launch Script Does

1. **Process Cleanup**: Kills any existing Node.js/npm processes
2. **Port Management**: Ensures port 3000 is available
3. **Dependency Check**: Installs node_modules if missing
4. **Server Start**: Launches the development server with `npm run dev`
5. **Verification**: Confirms the server is running and accessible

## 🌐 Accessing the Application

After running `./launch.sh`:
- The server will be available at: **http://localhost:3000**
- The script runs the server in the background
- You can continue using the terminal for other commands

## 🚨 Troubleshooting

### Script Permission Issues
If you get permission denied errors:
```bash
chmod +x launch.sh stop.sh
```

### Port Already in Use
If port 3000 is still occupied after running the stop script:
```bash
# Find what's using the port
lsof -i :3000

# Kill the process manually
kill -9 <PID>
```

### Server Won't Start
Check the server logs and ensure:
- You're in the project root directory
- All dependencies are installed (`npm install`)
- No other processes are using port 3000

## 💡 Pro Tips

- **Quick Restart**: Use `./stop.sh` then `./launch.sh` for a clean restart
- **Background Running**: The server runs in the background, so you can close the terminal
- **Process Monitoring**: Use `ps aux | grep "npm run dev"` to see server status
- **Logs**: Check server logs if you encounter issues

## 🔄 Development Workflow

1. **Start**: `./launch.sh`
2. **Develop**: Make your changes
3. **Test**: Open http://localhost:3000 in your browser
4. **Stop**: `./stop.sh` when done
5. **Restart**: `./launch.sh` if you need to restart

---

**Note**: These scripts are designed for development use. For production deployment, use appropriate process managers like PM2 or Docker.
