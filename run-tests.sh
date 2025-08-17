#!/bin/bash

# Visentia MVP Test Runner
echo "🧪 Starting Visentia MVP Test Suite..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Run tests with coverage
echo "🚀 Running tests with coverage..."
npm run test:coverage

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage report generated in coverage/ directory"
    
    # Open coverage report in browser if available
    if command -v open &> /dev/null; then
        open coverage/lcov-report/index.html
    elif command -v xdg-open &> /dev/null; then
        xdg-open coverage/lcov-report/index.html
    fi
else
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi
