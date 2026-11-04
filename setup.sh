#!/bin/bash

echo "="
echo "  GameHub - Automated Setup Script (Linux/macOS)"
echo "="
echo ""

echo "[1/3] Installing Root / Backend Dependencies..."
npm install
if [ $? -ne 0 ]; then
echo "Error installing backend dependencies!"
exit 1
fi

echo ""
echo "[2/3] Installing Frontend Dependencies..."
cd frontend || exit 1
npm install
if [ $? -ne 0 ]; then
echo "Error installing frontend dependencies!"
cd ..
exit 1
fi
cd ..

echo ""
echo "="
echo "  Setup Complete!"
echo "="
echo ""
echo "To start the backend:"
echo "  node server.js"
echo ""
echo "To start the frontend:"
echo "  cd frontend && npm run dev"
echo ""
