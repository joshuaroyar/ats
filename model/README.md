# ATS Resume Scoring Model

## Project Description

This project implements an advanced Applicant Tracking System (ATS) model designed to evaluate and score resumes against job descriptions. The system uses a multi-faceted approach combining natural language processing, semantic embeddings, domain-specific ontologies, and machine learning to provide comprehensive resume analysis and scoring.

The model assesses resumes across five key dimensions:
- **Impact Analysis**: Evaluates the strength of achievements, metrics, and domain-specific language
- **Structure Analysis**: Checks for proper resume formatting and section completeness
- **Clarity Analysis**: Analyzes grammar, readability, and communication effectiveness
- **Skill Matching**: Performs semantic matching of skills against job requirements using embeddings
- **Feedback Generation**: Provides actionable improvement suggestions using local LLM

The final ATS score is computed as a weighted combination of these components, providing recruiters with data-driven insights for candidate evaluation.

## Features

- **Multi-Engine PDF Text Extraction**: Robust extraction from resume PDFs with column detection and cleanup
- **Domain-Aware Impact Scoring**: Specialized analysis for tech, business, marketing, finance, operations, HR, and design domains
- **Semantic Skill Matching**: Uses sentence-transformers and ESCO ontology for accurate skill identification
- **Comprehensive Structure Validation**: Detects and scores resume sections, formatting, and content density
- **Clarity and Readability Assessment**: Grammar checking, passive voice detection, and readability scoring
- **LLM-Powered Feedback**: Generates personalized improvement suggestions using local Llama model
- **Ontology Integration**: Leverages ESCO (European Skills, Competences, Qualifications and Occupations) framework
- **Batch Processing Capability**: Supports evaluation of multiple resumes against job descriptions

## Installation

### Prerequisites
- Python 3.8+
- Ollama (for LLM feedback generation)
- CUDA-compatible GPU (recommended for faster embeddings)

### Setup Steps

1. **Clone the repository** (if applicable) and navigate to the model directory:
   ```bash
   cd model/
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required NLTK data**:
   ```bash
   python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('verbnet')"
   ```

## Running the Model as an API (FastAPI)

A production-friendly FastAPI wrapper is included as `api.py`. This exposes a simple `/analyze` endpoint that accepts a PDF resume and returns the ATS scores and feedback JSON used by the frontend.

Quick start (development):

```bash
# From repository root
cd model
python api.py
```

The server runs on `http://0.0.0.0:8000` by default. Example endpoints:

- `GET /health` — simple health check
- `POST /analyze` — accepts `multipart/form-data` with `file` field (PDF)

Example `curl` request:

```bash
curl -X POST \
   -F "file=@resume.pdf;type=application/pdf" \
   http://localhost:8000/analyze
```

Response format (JSON):

```json
{
   "final_ats_score": 65.5,
   "impact_score": 8,
   "structure_score": 15,
   "clarity_score": 4,
   "skill_score": 22,
   "feedback": "AI feedback lines..."
}
```

Where to configure the JD (job description):

- By default the API loads `jd.txt` from the `model/` folder. If you need dynamic JD input in future, update `api.py` to accept an additional form field or JSON body.

Environment variables and notes:

- `OLLAMA_BASE_URL` — used by the local LLM integration (if required)
- The system auto-detects GPU availability and will fallback to CPU if CUDA is not present.

Troubleshooting & common runtime notes
------------------------------------

- "Could get FontBBox from font descriptor because None cannot be parsed as 4 floats": this message comes from PDF parsing libraries when fonts are missing or malformed in the PDF. It's typically a warning — text extraction should still work. If extraction fails, try a different PDF or convert scanned PDFs via OCR before upload.
- If the `/analyze` endpoint returns `400` with "Could not extract text from PDF", the PDF may be image-only (scanned). Use an OCR step or provide a machine-readable PDF.
- If Ollama is not installed or times out, the API will still return scores and a placeholder feedback message.

Developer notes
---------------

- Start both servers quickly from repository root using `./start.sh` (this script launches the backend API and the frontend dev server).
- To run only the backend in production, run with an ASGI server: `uvicorn api:app --host 0.0.0.0 --port 8000 --workers 1`.


4. **Download SpaCy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Install and setup Ollama** (for feedback generation):
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama pull llama3.1:8b
   ```

6. **Generate ESCO embeddings** (one-time setup):
   ```bash
   cd utils/esco/
   python esco_graph_builder.py
   cd ../..
   python preprocessing/generate_skill_embeddings.py
   ```

## Usage Examples

### Basic Resume Evaluation

```python
from ats_score import ats_score

# Evaluate a resume against a job description
result = ats_score("resume.pdf", "job_description.txt")
print(f"Final ATS Score: {result['final_ats_score']}")
print(f"Impact Score: {result['impact_score']}")
print(f"Structure Score: {result['structure_score']}")
print(f"Clarity Score: {result['clarity_score']}")
print(f"Skill Score: {result['skill_score']}")
print(f"Feedback: {result['feedback']}")
```

### Command Line Usage

```bash
# Run evaluation from command line
python run.py
```

This will evaluate `resume.pdf` against `jd.txt` and output JSON results.

### Individual Module Usage

```python
# Impact analysis only
from core.scoring.domain_impact_analyzer import analyze_resume_impact
impact = analyze_resume_impact("resume.pdf")

# Structure analysis only
from preprocessing.structure_analyzer import analyze_structure
structure = analyze_structure(resume_text)

# Skill matching
from core.scoring.advanced_skill_matcher import advanced_score
skills = advanced_score("resume.pdf", jd_text)
```

## File Structure Overview

```
model/
├── ats_score.py              # Main unified scoring endpoint
├── run.py                    # Command-line entry point
├── jd.txt                    # Sample job description
├── requirements.txt          # Python dependencies
├── core/
│   ├── ontology/
│   │   └── map_to_ontology.py # ESCO ontology mapping
│   └── scoring/
│       ├── scoring_engine.py      # Core evaluation logic
│       ├── domain_impact_analyzer.py  # Impact scoring
│       ├── advanced_skill_matcher.py  # Semantic skill matching
│       ├── skill_matcher.py       # Legacy skill matcher
│       ├── domain_noun_builder.py # Domain noun generation
│       ├── domain_verb_builder.py # Domain verb generation
│       └── feedback_engine.py     # LLM feedback generation
├── preprocessing/
│   ├── evaluate_resume.py         # Resume evaluation wrapper
│   ├── structure_analyzer.py      # Structure analysis
│   ├── clarity_analyzer.py        # Clarity analysis
│   └── generate_skill_embeddings.py # Embedding generation
├── resources/
│   ├── business_nouns.json        # Business domain nouns
│   ├── business_verbs.json        # Business domain verbs
│   ├── design_nouns.json          # Design domain nouns
│   ├── design_verbs.json          # Design domain verbs
│   ├── finance_nouns.json         # Finance domain nouns
│   ├── finance_verbs.json         # Finance domain verbs
│   ├── hr_nouns.json              # HR domain nouns
│   ├── hr_verbs.json              # HR domain verbs
│   ├── marketing_nouns.json       # Marketing domain nouns
│   ├── marketing_verbs.json       # Marketing domain verbs
│   ├── operations_nouns.json      # Operations domain nouns
│   ├── operations_verbs.json      # Operations domain verbs
│   ├── tech_nouns.json            # Tech domain nouns
│   └── tech_verbs.json            # Tech domain verbs
└── utils/
    ├── columns.py                 # Column utilities
    ├── pdf_reader.py              # PDF text extraction
    ├── __pycache__/               # Python cache
    ├── esco/
    │   ├── esco_graph_builder.py  # ESCO graph construction
    │   ├── esco_skill_graph.json  # ESCO skill graph
    │   ├── skill_embeddings.json  # Pre-computed embeddings
    │   ├── skills_en.csv          # ESCO skills data
    │   ├── skillsHierarchy_en.csv # ESCO hierarchy data
    │   └── skillSkillRelations_en.csv # ESCO relations data
    ├── extraction/
    │   └── skill_extractor.py     # Skill phrase extraction
    └── linguistic/
        └── linguistic_engine.py   # Linguistic resource building
```

## Dependencies

### Core Dependencies
- **networkx**: Graph operations for ESCO ontology
- **nltk**: Natural language processing toolkit
- **numpy**: Numerical computing
- **pdfminer**: PDF text extraction
- **pdfplumber**: Alternative PDF processing
- **sentence-transformers**: Semantic embeddings
- **spacy**: Advanced NLP processing
- **torch**: Deep learning framework

### External Requirements
- **Ollama**: Local LLM inference (llama3.1:8b model)
- **CUDA**: GPU acceleration for embeddings (optional but recommended)

## Architecture

### Workflow Overview

1. **Text Extraction**: PDF resume is processed to extract clean, structured text
2. **Preprocessing**: Text is analyzed for structure, clarity, and initial skill extraction
3. **Impact Analysis**: Domain-specific scoring based on verbs, nouns, and metrics
4. **Skill Matching**: Semantic similarity matching against job description requirements
5. **Feedback Generation**: LLM generates personalized improvement suggestions
6. **Score Aggregation**: Weighted combination of all components into final ATS score

### Key Components

- **ESCO Integration**: Uses European Skills ontology for standardized skill classification
- **Embedding-Based Matching**: Sentence-transformers provide semantic understanding
- **Domain Specialization**: Separate models for different professional domains
- **Multi-Modal Analysis**: Combines rule-based and ML approaches for comprehensive evaluation

## Configuration

### Scoring Weights
The final ATS score is calculated as:
```
Final Score = (Impact × 1.45) + (Structure × 1.5) + (Clarity × 1.3) + (Skills × 1.5)
```

Weights can be adjusted in `ats_score.py` for different evaluation priorities.

### Thresholds
- Skill similarity threshold: 0.72 (configurable in advanced_skill_matcher.py)
- ESCO mapping threshold: 0.60 (configurable in map_to_ontology.py)

## Performance Notes

- First run requires ESCO embedding generation (~10-15 minutes)
- GPU acceleration significantly speeds up embedding computations
- Memory usage scales with resume complexity and ESCO database size
- Local LLM feedback generation requires ~4GB RAM for Llama 3.1 8B

## Troubleshooting

### Common Issues

1. **Missing embeddings**: Run `python preprocessing/generate_skill_embeddings.py`
2. **NLTK data**: Ensure all required NLTK corpora are downloaded
3. **SpaCy model**: Verify `en_core_web_sm` is installed
4. **Ollama connection**: Ensure Ollama service is running and model is pulled

### Performance Optimization

- Use GPU for embedding computations
- Reduce candidate limits in advanced_skill_matcher.py for faster processing
- Pre-compute embeddings for frequently used job descriptions

## Contributing

When contributing to the model:
1. Maintain separation between preprocessing, core analysis, and utilities
2. Add comprehensive docstrings to new functions
3. Include unit tests for scoring functions
4. Update requirements.txt for new dependencies
5. Document any configuration changes

## License

This project is part of the ATS system. Please refer to the main project license for usage terms.