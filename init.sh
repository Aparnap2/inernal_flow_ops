#!/bin/bash

# HubSpot Operations Orchestrator Initialization Script

echo "🚀 Initializing HubSpot Operations Orchestrator..."

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing frontend dependencies..."
cd frontend
pnpm install

echo "🐍 Installing backend dependencies..."
cd ../backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "🔧 Setting up database..."
cd ../frontend
pnpm db:generate
pnpm db:migrate
pnpm db:seed

echo "🔐 Setting up environment variables..."
# Copy example env files if they don't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "No .env.example found in frontend"
fi

cd ../backend
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || echo "No .env.example found in backend"
fi

echo "✅ Initialization complete!"
echo ""
echo "Next steps:"
echo "1. Configure your environment variables in frontend/.env and backend/.env"
echo "2. Start the frontend: cd frontend && pnpm dev"
echo "3. Start the backend: cd backend && source .venv/bin/activate && python main.py"
echo "4. Visit http://localhost:5173 in your browser"