#!/bin/bash
# Startup script for ATS Resume Analyzer

echo "🚀 Starting ATS Resume Analyzer..."

# --- 1. Check Prerequisites ---

if ! command -v python &> /dev/null; then
    echo "❌ python is not installed."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js."
    exit 1
fi

# --- Determine Python Interpreter ---
if [ -d "$(pwd)/model/venv" ]; then
    echo "🐍 Using virtual environment: model/venv"
    PYTHON_EXEC="$(pwd)/model/venv/bin/python"
elif [ -d "$(pwd)/venv" ]; then
    # In case venv is at root
    echo "🐍 Using virtual environment: venv"
    PYTHON_EXEC="$(pwd)/venv/bin/python"
else
    echo "🐍 Using system python (ensure dependencies are installed)"
    PYTHON_EXEC="python"
fi

# --- 1.5 Setup spaCy ---
echo "🧠 Checking spaCy models..."
# Check if en_core_web_sm is installed, if not download it
if ! $PYTHON_EXEC -c "import spacy; spacy.load('en_core_web_sm')" &> /dev/null; then
    echo "📥 Downloading spacy model 'en_core_web_sm'..."
    $PYTHON_EXEC -m spacy download en_core_web_sm
else
    echo "✅ spaCy model 'en_core_web_sm' is ready."
fi

# --- 2. Setup Ollama (AI Model) ---

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it from https://ollama.com/"
    echo "   The AI feedback feature requires Ollama."
    # We don't exit here, allowing the app to run without AI if user wants, 
    # but the feedback feature will fail gracefully.
else
    # Start Ollama if not running
    if ! pgrep -x "ollama" > /dev/null && ! pgrep -x "ollama serve" > /dev/null; then
        echo "🦙 Starting Ollama service..."
        ollama serve &
        OLLAMA_PID=$!
        # Give it time to initialize
        sleep 5
    else
        echo "🦙 Ollama is already running."
    fi

    # Check for the specific model
    MODEL="llama3.1:8b"
    echo "🔍 Checking for AI model: $MODEL..."
    
    # List models and check if ours exists
    if ! ollama list | grep -q "$MODEL"; then
        echo "📥 Model $MODEL not found. Pulling it now..."
        echo "   (This may take a few minutes depending on your internet connection)"
        ollama pull $MODEL
    else
        echo "✅ Model $MODEL is ready."
    fi
fi

# --- 3. Start Backend ---

echo "📡 Starting backend API server..."
cd model
# Start API using the determined python executable
# Note: PYTHON_EXEC is absolute path, so it works after cd
$PYTHON_EXEC api.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# --- 4. Start Frontend ---

echo "🌐 Starting frontend development server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ All services are up and running!"
echo "📡 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all servers"

# --- 5. Cleanup Handler ---

cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    
    # Only kill Ollama if we started it
    if [ ! -z "$OLLAMA_PID" ]; then
        echo "🛑 Stopping Ollama..."
        kill $OLLAMA_PID 2>/dev/null
    fi
    exit
}

# Wait for user interrupt
trap cleanup INT
wait