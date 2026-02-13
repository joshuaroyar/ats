# 🎓 ATS Resume Analyzer - Step-by-Step Setup Tutorial

This guide provides a detailed walkthrough to get the ATS Resume Analyzer running on your local system. 

**Target OS:** Linux (Ubuntu/Debian) or Windows Subsystem for Linux (WSL).

---

## 📦 Phase 1: Prerequisites

Before starting, ensure you have the core tools installed.

### 1. Install System Dependencies (Linux/WSL)

Open your terminal and check for updates and basic tools.

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nodejs npm git curl
```

### 2. Install Ollama (For AI Feedback)

The application uses **Ollama** to run the Llama 3.1 model locally for generating resume feedback.

1.  **Download & Install:**
    Run the following command (works for Linux & WSL):
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

2.  **Verify Installation:**
    ```bash
    ollama --version
    ```

3.  **Start Ollama Service:**
    If it's not running automatically:
    ```bash
    ollama serve &
    ```

---

## 🚀 Phase 2: Project Setup

### 1. navigate to the project folder

```bash
cd path/to/ats
```

(Replace `path/to/ats` with the actual path where you have this code).

### 2. The Setup Script (Recommended Method)

We have provided a `start.sh` script that automates the environment creation, dependency installation, and server startup.

**Step 2a: Make the script executable**
```bash
chmod +x start.sh
```

**Step 2b: Run the script**
```bash
./start.sh
```

**What this script does:**
1.  Creates a Python virtual environment (`model/venv`).
2.  Installs Python dependencies (`fastapi`, `torch`, `spacy`, etc.).
3.  Downloads the `en_core_web_sm` spaCy model.
4.  Pulls the `llama3.1:8b` model via Ollama (this might take a few minutes on first run).
5.  Starts the Backend API at `http://localhost:8000`.
6.  Starts the Frontend React App at `http://localhost:5173`.

---

## 🔧 Phase 3: Manual Setup (If Script Fails)

If you prefer to set things up manually, follow these steps.

### Backend Setup (Python)

1.  **Navigate to the model directory:**
    ```bash
    cd model
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the Environment:**
    ```bash
    source venv/bin/activate
    ```

4.  **Install Requirements:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This includes torch, sentence-transformers, fastapi, uvicorn, spacy, etc.*

5.  **Download NLP Language Model:**
    ```bash
    python -m spacy download en_core_web_sm
    ```

6.  **Run the Server:**
    ```bash
    python api.py
    ```
    You should see `Uvicorn running on http://0.0.0.0:8000`.

### Frontend Setup (Node/React)

1.  **Open a NEW terminal window.**

2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

3.  **Install Dependencies:**
    ```bash
    npm install
    ```

4.  **Configure Environment:**
    Ensure `.env` exists:
    ```bash
    echo "VITE_BACKEND_URL=/api/analyze" > .env
    ```
    *Note: We use `/api` because Vite is configured to proxy requests to port 8000.*

5.  **Start the Dev Server:**
    ```bash
    npm run dev
    ```
    You should see `Local: http://localhost:5173`.

---

## 🛠 Phase 4: Troubleshooting Common Issues

### 1. "Ollama connection failed" or "AI Feedback unavailable"
- Ensure Ollama is running: `ps aux | grep ollama`
- If not, run `ollama serve`.
- Ensure you have the model: `ollama list`. If empty, run `ollama pull llama3.1:8b`.

### 2. GPU/CUDA Errors
- The system is designed to fallback to CPU if CUDA is not found.
- If you see warnings about CUDA, they are safe to ignore unless you specifically want GPU acceleration.

### 3. "Network Error" on Frontend
- If using WSL, ensure `vite.config.js` has the proxy setup (already included in this codebase).
- Ensure the backend is actually running on port 8000.

### 4. "Externally managed environment" Error
- This happens on newer Linux versions if you try `pip install` without a virtual environment.
- **Solution:** Always use the `venv` as described in Phase 3.
