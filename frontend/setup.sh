#!/bin/bash

# Scout Badge Inventory - Frontend Setup Script
# This script sets up the Next.js frontend environment

set -e

echo "================================================"
echo "Scout Badge Inventory - Frontend Setup"
echo "================================================"
echo ""

# Check Node.js version
echo "Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js version 18 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✓ Node.js $(node -v) detected"
echo ""

# Install dependencies
echo "Installing dependencies..."
npm install

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The application will be available at:"
echo "  http://localhost:3000"
echo ""
echo "Make sure the backend server is running at:"
echo "  http://localhost:8000"
echo ""
echo "For more information, see README.md"
echo ""
