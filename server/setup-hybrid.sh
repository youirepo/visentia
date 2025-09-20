#!/bin/bash
# Setup script for Hybrid Visual Generator

echo "🚀 Setting up Hybrid Visual Generator..."

# Create directories
echo "📁 Creating directories..."
mkdir -p server/generated-scenes
mkdir -p server/temp-stitching
mkdir -p server/templates

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r server/requirements-hybrid.txt
else
    echo "⚠️  pip3 not found. Please install Python 3 and pip3."
    exit 1
fi

# Install Node.js dependencies for video capture (from root directory)
echo "📦 Installing Node.js dependencies..."
cd ..
npm install
echo "✅ Node.js dependencies installed"

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x server/services/hybrid-visual-generator.py
chmod +x server/services/video-capture.js

# Test Python installation
echo "🧪 Testing Python installation..."
python3 -c "import jinja2, matplotlib, numpy, PIL; print('✅ Python dependencies OK')" 2>/dev/null || {
    echo "❌ Python dependencies test failed"
    exit 1
}

# Test Node.js installation
echo "🧪 Testing Node.js installation..."
node -e "console.log('✅ Node.js OK')" 2>/dev/null || {
    echo "❌ Node.js test failed"
    exit 1
}

echo "✅ Hybrid Visual Generator setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test the system with: node server/services/video-capture.js --help"
echo "2. Test Python generator with: python3 server/services/hybrid-visual-generator.py --help"
echo "3. Update your video generation pipeline to use HybridVisualService"
echo ""
echo "🎯 The hybrid approach uses:"
echo "  • Reveal.js for structured slides"
echo "  • Mermaid.js for diagrams"
echo "  • KaTeX for math expressions"
echo "  • Matplotlib for graphs"
echo "  • Puppeteer for video capture"

