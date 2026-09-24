#!/usr/bin/env bash
# ==============================================================================
# ClauseGuard — Unified Development & Demo Launcher
# Launches the FastAPI backend (port 8000) and Next.js frontend (port 3000)
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "================================================================================"
echo "  ClauseGuard: AI Real-Estate Transaction Intelligence Platform"
echo "================================================================================"
echo "Project Root: $PROJECT_ROOT"
echo ""

# Check Python environment
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "❌ Backend virtualenv not found at $BACKEND_DIR/.venv"
    echo "   Please create it: cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Locate Node.js runtime
NODE_PATH=""
if command -v node >/dev/null 2>&1; then
    NODE_PATH="$(command -v node)"
elif [ -d "$HOME/.nvm/versions/node" ]; then
    LATEST_NVM_NODE=$(find "$HOME/.nvm/versions/node" -maxdepth 2 -name "node" | head -n 1)
    if [ -n "$LATEST_NVM_NODE" ]; then
        export PATH="$(dirname "$LATEST_NVM_NODE"):$PATH"
        NODE_PATH="$LATEST_NVM_NODE"
    fi
fi

if [ -z "$NODE_PATH" ]; then
    echo "❌ Node.js 18+ runtime not found."
    exit 1
fi

echo "✅ Python Virtualenv: $BACKEND_DIR/.venv"
echo "✅ Node.js Runtime:   $($NODE_PATH --version) ($NODE_PATH)"
echo ""

# Trap to kill both background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down ClauseGuard services..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    echo "✅ Shutdown complete."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

echo "🚀 [1/2] Starting FastAPI Backend on http://127.0.0.1:8000..."
cd "$BACKEND_DIR"
"$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "🚀 [2/2] Starting Next.js Production Server on http://localhost:3000..."
cd "$FRONTEND_DIR"
npm start -- -p 3000 &
FRONTEND_PID=$!

echo ""
echo "================================================================================"
echo "✨ ClauseGuard is live and operational!"
echo "   - Frontend Web UI:        http://localhost:3000"
echo "   - Demo Transaction:       http://localhost:3000/dashboard/transactions/skyview-a1204"
echo "   - Interactive API Docs:   http://127.0.0.1:8000/docs"
echo "   - Health & Probes:        http://127.0.0.1:8000/api/v1/health/ready"
echo "================================================================================"
echo "Press Ctrl+C at any time to gracefully terminate both services."
echo ""

wait
