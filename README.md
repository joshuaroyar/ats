# ATS Resume Analyzer

<div align="center">
  
  ![ATS Resume Analyzer](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
  ![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=for-the-badge&logo=react)
  ![Vite](https://img.shields.io/badge/Vite-7.2.7-646CFF?style=for-the-badge&logo=vite)
  ![TailwindCSS](https://img.shields.io/badge/Tailwind-4.1.17-06B6D4?style=for-the-badge&logo=tailwindcss)
  ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
  ![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch)
  ![Ollama](https://img.shields.io/badge/Ollama-0.1.0+-000000?style=for-the-badge&logo=ollama)

  **AI-powered ATS (Applicant Tracking System) resume analysis tool**
  
  Get instant feedback and actionable insights to optimize your resume for ATS systems and land your dream job.

  [Live Demo](https://cv.krytil.com) • [Report Bug](https://github.com/joshuaroyar/ats/issues) • [Request Feature](https://github.com/joshuaroyar/ats/issues)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Application](#running-the-application)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [API Integration](#-api-integration)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

**ATS Resume Analyzer** is a modern, AI-powered web application that helps job seekers optimize their resumes for Applicant Tracking Systems. The tool analyzes uploaded resumes and provides:

- **ATS Compatibility Score** - Overall rating out of 100 points
- **Detailed Score Breakdown** - Impact, Structure, Clarity, and Skill scores
- **AI-Generated Feedback** - Actionable recommendations for improvement
- **Side-by-Side View** - Preview your resume while reviewing the analysis

Built with React and Vite for the frontend, and Python with PyTorch/spacy for the AI-powered backend, this application features a beautiful, modern UI with smooth animations and an intuitive user experience.

---

## ✨ Features

### 🚀 Core Functionality
- **PDF Resume Upload** - Drag-and-drop or click to upload (max 5MB)
- **Job Description Analysis** - Upload text or file for targeted scoring
- **Real-time Analysis** - Instant AI-powered resume evaluation
- **Comprehensive Scoring** - Multi-dimensional assessment across 4 key metrics:
  - Impact Score (25 points)
  - Structure Score (20 points)
  - Clarity Score (10 points)
  - Skill Score (45 points)
- **Detailed Feedback** - Generative AI insights powered by Ollama (Llama 3.1)
- **PDF Preview** - View your resume alongside the analysis report

### 🎨 UI/UX Features
- **Modern, Clean Design** - Gradient accents and glassmorphism effects
- **Responsive Layout** - Optimized for desktop, tablet, and mobile devices
- **Smooth Animations** - Framer Motion powered transitions
- **Progress Indicators** - Visual feedback during upload and analysis
- **Error Handling** - Clear user-friendly error messages
- **Accessible** - Built with web accessibility best practices

---

## 🛠 Tech Stack

### Frontend Framework
- **React 18.2.0** - UI component library
- **React Router DOM 6.** - Client-side routing
- **Vite 7** - Build tool and dev server

### State Management & HTTP
- **Axios** - HTTP client for API requests

### Styling & UI
- **Tailwind CSS 4** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

### Backend Framework
- **Python 3.10+** - Core script language
- **FastAPI** - Backend API server
- **PyTorch / SentenceTransformers** - Embedding and semantic search

### AI/ML Libraries
- **spaCy** - Natural language processing
- **Ollama** - Local LLM runner (Llama 3.1)
- **scikit-learn** - Similarity calculations
- **networkx** - Knowledge graph processing

### Utilities
- **React Hot Toast 2.4.1** - Toast notifications
- **React Helmet Async 2.0.4** - Document head management
- **React PDFtoText** - PDF text extraction

---

## 🚀 Getting Started

The easiest way to run the application is using the provided startup script, which handles dependencies and services automatically.

### Prerequisites

- **Linux or WSL (Windows Subsystem for Linux)** (Recommended)
- **Python 3.10+**
- **Node.js** (v18+)
- **Ollama** (for AI feedback) - [Installation Guide](https://ollama.com)

### Quick Start (Recommended)

1.  **Make the script executable** (first time only):
    ```bash
    chmod +x start.sh
    ```

2.  **Run the application**:
    ```bash
    ./start.sh
    ```

This script will setup the Python virtual environment, install dependencies, download required AI models, and start both the backend and frontend servers.

### Manual Installation

For detailed step-by-step instructions, including handling common errors, please refer to our [**Setup Tutorial**](docs/SETUP_TUTORIAL.md).

#### Backend Setup
1. **Navigate to model directory**
   ```bash
   cd ../model
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Ollama and pull required models**
   ```bash
   # Install Ollama (if not already installed)
   # Then pull the required model, e.g.:
   ollama pull llama2  # or your preferred model
   ```

4. **Download ESCO skill data** (if not present)
   - Ensure `utils/esco/skills_en.csv` and related files are present

### Environment Variables

#### Frontend
Create a `.env` file in the `frontend` directory:

```env
VITE_BACKEND_URL=http://localhost:8000/analyze  # or your backend API endpoint
```

#### Backend
Create a `.env` file in the `model` directory (if needed):

```env
OLLAMA_BASE_URL=http://localhost:11434  # Default Ollama URL
# Add other environment variables as required
```

### Running the Application

#### Quick Start (Recommended)
```bash
# Start both frontend and backend with one command
./start.sh
```

#### Manual Start

##### Backend (Start First)
```bash
cd model
python api.py
```

The backend API will be available at `http://localhost:8000` (adjust port as needed).

##### Frontend
###### Development Mode
```bash
cd frontend
npm run dev
# or
yarn dev
```

The app will be available at `http://localhost:5173`

##### Build for Production
```bash
npm run build
# or
yarn build
```

##### Preview Production Build
```bash
npm run preview
# or
yarn preview
```

---

## 📁 Project Structure

```
ats/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── ATS.jsx              # Main upload page
│   │   │   └── ATSReport.jsx         # Analysis report page
│   │   ├── App.jsx                   # Main app component with routing
│   │   ├── main.jsx                  # Application entry point
│   │   └── index.css                 # Global styles
│   ├── public/
│   │   └── resume-checker.webp       # Preview image
│   ├── index.html                    # HTML template
│   ├── package.json                  # Dependencies and scripts
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   └── eslint.config.js              # ESLint configuration
├── model/
│   ├── ats_score.py                  # Main scoring script
│   ├── run.py                        # Backend server entry point
│   ├── requirements.txt              # Python dependencies
│   ├── jd.txt                        # Job description template
│   ├── core/
│   │   ├── ontology/
│   │   │   └── map_to_ontology.py    # Ontology mapping logic
│   │   └── scoring/
│   │       ├── advanced_skill_matcher.py
│   │       ├── domain_impact_analyzer.py
│   │       ├── domain_noun_builder.py
│   │       ├── domain_verb_builder.py
│   │       ├── feedback_engine.py
│   │       ├── scoring_engine.py
│   │       ├── skill_matcher.py
│   │       └── __pycache__/
│   ├── preprocessing/
│   │   ├── clarity_analyzer.py
│   │   ├── evaluate_resume.py
│   │   ├── generate_skill_embeddings.py
│   │   ├── structure_analyzer.py
│   │   └── __pycache__/
│   ├── resources/
│   │   ├── business_nouns.json
│   │   ├── business_verbs.json
│   │   ├── design_nouns.json
│   │   ├── design_verbs.json
│   │   ├── finance_nouns.json
│   │   ├── finance_verbs.json
│   │   ├── hr_nouns.json
│   │   ├── hr_verbs.json
│   │   ├── marketing_nouns.json
│   │   ├── marketing_verbs.json
│   │   ├── operations_nouns.json
│   │   ├── operations_verbs.json
│   │   ├── tech_nouns.json
│   │   └── tech_verbs.json
│   ├── utils/
│   │   ├── columns.py
│   │   ├── pdf_reader.py
│   │   ├── __pycache__/
│   │   └── esco/
│   │       ├── esco_graph_builder.py
│   │       ├── esco_skill_graph.json
│   │       ├── skill_embeddings.json
│   │       ├── skills_en.csv
│   │       ├── skillsHierarchy_en.csv
│   │       └── skillSkillRelations_en.csv
│   └── README.md                     # Backend documentation
└── README.md                         # This file
```

---

## 🔍 How It Works

### 1. Resume Upload (`/` or `/ats-score`)
- User drags and drops or selects a PDF file
- Client-side validation checks file type and size
- File is stored temporarily in session storage
- PDF is sent to backend API via FormData

### 2. Analysis Processing
- Backend API processes the resume using AI
- Returns structured JSON with:
  ```json
  {
    "final_ats_score": 45,
    "impact_score": 7,
    "structure_score": 15,
    "clarity_score": 3,
    "skill_score": 20,
    "feedback": "Detailed AI-generated feedback..."
  }
  ```

### 3. Report Display (`/ats-score/report`)
- User is redirected to report page
- Left panel shows PDF preview via iframe
- Right panel displays:
  - Final ATS score (large circular display)
  - Score breakdown with progress bars
  - AI-generated feedback and recommendations

---

## 🔌 API Integration

### Expected Backend Endpoint

**Endpoint:** `POST /analyze` (or as configured in `VITE_BACKEND_URL`)

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: FormData with `file` field containing PDF

**Response:**
```json
{
  "final_ats_score": 45,
  "impact_score": 7,
  "structure_score": 15,
  "clarity_score": 3,
  "skill_score": 20,
  "feedback": "Your resume demonstrates good structure but could benefit from more quantifiable achievements..."
}
```

**Status Codes:**
- `200 OK` - Successful analysis
- `400 Bad Request` - Invalid file, unsupported format, or text extraction failed
- `500 Internal Server Error` - Analysis failed

**Error Handling:**
- Automatic fallback to CPU if CUDA is unavailable
- Robust PDF text extraction with multiple engines
- Graceful degradation when AI feedback is unavailable
- Comprehensive logging for debugging

---

## 🚢 Deployment

### Backend Deployment
1. **Set up Python environment**
   ```bash
   cd model
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   - Set `OLLAMA_BASE_URL` if using remote Ollama
   - Configure any other backend settings

3. **Run the backend server**
   ```bash
   python run.py
   ```

4. **Deploy to cloud** (Heroku, AWS, etc.)
   - Ensure Ollama is accessible (local or hosted)
   - Use Gunicorn or similar for production

### Frontend Deployment (Vercel, Netlify, etc.)

1. **Build the project:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Configure environment variables** in your hosting platform:
   - `VITE_BACKEND_URL` - Your backend API endpoint

3. **Deploy the `dist` folder**

### Recommended Platforms
- **Backend:** Heroku, Railway, Render, AWS EC2
- **Frontend:** Vercel, Netlify, Cloudflare Pages, AWS S3 + CloudFront

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing code style
- Write meaningful commit messages
- Test your changes thoroughly
- Update documentation as needed

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Project Maintainer:** Joshua Royar
**Repository:** [github.com/joshuaroyar/ats](https://github.com/joshuaroyar/ats)  
**Live Demo:** [cv.krytil.com](https://cv.krytil.com)

For questions, suggestions, or issues, please [open an issue](https://github.com/joshuaroyar/ats/issues) on GitHub.

---

## 🙏 Acknowledgments

- Icons by [Lucide Icons](https://lucide.dev/)
- UI inspiration from modern design trends
- Built with ❤️ for job seekers worldwide

---

<div align="center">
  
  **Made with ❤️ by the Krytil Team**
  
  ⭐ Star this repo if you find it helpful!

</div>
