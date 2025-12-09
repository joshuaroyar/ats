# ATS Resume Analyzer - Frontend

Modern, responsive React application for AI-powered resume analysis and ATS optimization.

---

## 📑 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Features](#features)
- [Component Documentation](#component-documentation)
- [Styling Guide](#styling-guide)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Development](#development)
- [Build & Deploy](#build--deploy)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This frontend application provides an intuitive interface for users to upload their resumes and receive comprehensive ATS (Applicant Tracking System) analysis. Built with React 18 and Vite 5, it offers lightning-fast performance and a modern development experience.

### Key Capabilities
- ✅ PDF resume upload with drag-and-drop
- ✅ Real-time file validation
- ✅ AI-powered analysis visualization
- ✅ Interactive score breakdowns
- ✅ Side-by-side PDF preview
- ✅ Fully responsive design

---

## 🛠 Tech Stack

### Core Framework
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "vite": "^7.2.7"
}
```

### Routing & Navigation
- **react-router-dom** `^6.21.3` - Client-side routing with React Router v6

### State Management
- **@reduxjs/toolkit** `^2.1.0` - Modern Redux state management
- **react-redux** `^9.1.0` - React bindings for Redux

### HTTP & Data
- **axios** `^1.6.5` - Promise-based HTTP client
- **react-pdftotext** `latest` - PDF text extraction utilities

### UI & Styling
- **tailwindcss** `^4.1.17` - Utility-first CSS framework
- **framer-motion** `^11.0.3` - Animation library
- **lucide-react** `^0.320.0` - Beautiful icon set

### User Experience
- **react-hot-toast** `^2.4.1` - Toast notifications
- **react-helmet-async** `^2.0.4` - Document head management

### Build Tools
- **@vitejs/plugin-react** `^4.2.1` - Vite React plugin with Fast Refresh
- **autoprefixer** `^10.4.17` - PostCSS plugin for vendor prefixes
- **postcss** `^8.4.33` - CSS transformation tool

---

## 🏗 Project Architecture

```
frontend/
├── public/
│   └── resume-checker.webp          # Preview image asset
├── src/
│   ├── pages/
│   │   ├── ATS.jsx                  # Upload page (main landing)
│   │   └── ATSReport.jsx            # Analysis report page
│   ├── App.jsx                      # Root component with routing
│   ├── main.jsx                     # Application entry point
│   └── index.css                    # Global styles & Tailwind imports
├── index.html                       # HTML template
├── vite.config.js                   # Vite configuration
├── tailwind.config.js               # Tailwind CSS configuration
├── eslint.config.js                 # ESLint configuration
├── package.json                     # Dependencies & scripts
└── README.md                        # This file
```

### Design Patterns
- **Component-based architecture** - Isolated, reusable UI components
- **Page-based routing** - Clear separation between major views
- **Session storage** - Temporary PDF file storage
- **State hoisting** - Data passed via React Router location state

---

## 🚀 Getting Started

### Prerequisites
- Node.js v16 or higher
- npm or yarn package manager

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   
   Create a `.env` file in the frontend directory:
   ```env
   VITE_BACKEND_URL=https://your-backend-api.com/analyze
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open in browser:**
   ```
   http://localhost:5173
   ```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `VITE_BACKEND_URL` | Backend API endpoint for resume analysis | Yes | `https://api.example.com/analyze` |

### Vite Configuration (`vite.config.js`)

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),           // Enable React Fast Refresh
    tailwindcss(),     // Tailwind CSS integration
  ],
  resolve: {
    alias: {
      // Ensure consistent React version across dependencies
      react: path.resolve(__dirname, './node_modules/react'),
      'react-dom': path.resolve(__dirname, './node_modules/react-dom'),
    },
  },
})
```

### Tailwind Configuration (`tailwind.config.js`)

```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Outfit", "sans-serif"],
        serif: ["Goudy Bookletter 1911", "serif"],
      },
    },
  },
  plugins: [],
}
```

---

## ✨ Features

### 1. Resume Upload (ATS.jsx)
**Route:** `/` or `/ats-score`

#### Capabilities:
- Drag-and-drop file upload
- Click-to-browse file selection
- Real-time file validation:
  - Type: PDF only
  - Size: Max 5MB
- Visual upload states:
  - Idle state with upload prompt
  - Active drag overlay
  - Uploading progress indicator
  - Success confirmation
  - Error messages

#### User Flow:
1. User lands on upload page
2. Drags PDF or clicks to select
3. File validated client-side
4. PDF sent to backend API
5. PDF URL stored in sessionStorage
6. Redirected to report page with analysis data

### 2. Analysis Report (ATSReport.jsx)
**Route:** `/ats-score/report`

#### Capabilities:
- Side-by-side layout:
  - Left: PDF preview in iframe
  - Right: Analysis results
- Score visualization:
  - Final ATS score (circular display)
  - Individual score breakdowns with progress bars
  - Color-coded performance indicators
- AI feedback section with detailed recommendations
- Back navigation to upload page

#### Score Metrics:
| Metric | Max Points | Description |
|--------|------------|-------------|
| Impact Score | 10 | Resume's overall impact and achievements |
| Structure Score | 20 | Format, organization, and readability |
| Clarity Score | 5 | Language clarity and conciseness |
| Skill Score | 30 | Relevant skills and keywords |
| **Final Score** | **65** | **Total ATS compatibility** |

---

## 🧩 Component Documentation

### App.jsx
**Purpose:** Root application component with routing configuration

```jsx
<BrowserRouter>
  <Routes>
    <Route path="/" element={<ATS />} />
    <Route path="/ats-score" element={<ATS />} />
    <Route path="/ats-score/report" element={<ATSReport />} />
  </Routes>
</BrowserRouter>
```

### pages/ATS.jsx
**Main Upload Component**

#### State Management:
```javascript
const [dragActive, setDragActive] = useState(false)      // Drag-over state
const [fileInfo, setFileInfo] = useState(null)           // Uploaded file details
const [error, setError] = useState("")                   // Error messages
const [isAnalyzing, setIsAnalyzing] = useState(false)    // Loading state
```

#### Key Functions:
- `handleFile(file)` - File validation, API call, navigation
- Drag event handlers for drag-and-drop UX
- File input ref for programmatic click

#### API Integration:
```javascript
const formData = new FormData()
formData.append("file", file)

const res = await axios.post(BACKEND_URL, formData, {
  headers: { "Content-Type": "multipart/form-data" }
})

navigate("/ats-score/report", { state: { atsData: res.data } })
```

### pages/ATSReport.jsx
**Analysis Display Component**

#### Data Sources:
- `location.state.atsData` - Analysis data from navigation state
- `sessionStorage.getItem("pdfURL")` - PDF blob URL

#### Sub-components:
- `ScoreItem` - Reusable score bar component with progress visualization
- `Icons` - Inline SVG icon components (ChevronLeft, Score, Feedback)

#### Data Structure:
```javascript
atsData = {
  final_ats_score: Number,
  impact_score: Number,
  structure_score: Number,
  clarity_score: Number,
  skill_score: Number,
  feedback: String
}
```

---

## 🎨 Styling Guide

### Design System

#### Color Palette
```css
/* Primary Gradients */
bg-gradient-to-r from-blue-600 to-indigo-600    /* Brand gradient */
bg-gradient-to-r from-slate-800 to-slate-900    /* Button gradient */

/* Status Colors */
bg-green-500   /* Good score (>75%) */
bg-yellow-500  /* Medium score (40-75%) */
bg-red-500     /* Low score (<40%) */

/* Neutral Palette */
bg-slate-50    /* Page background */
bg-white       /* Cards and containers */
text-slate-900 /* Primary text */
text-slate-600 /* Secondary text */
```

#### Typography
```css
/* Headings */
font-family: 'Outfit', sans-serif
font-weight: 700-900 (bold to black)

/* Body */
font-family: 'Outfit', sans-serif
font-weight: 400-600 (normal to semibold)
```

#### Spacing & Layout
- Container max-width: `max-w-6xl`
- Card padding: `p-6` to `p-10`
- Border radius: `rounded-2xl` to `rounded-3xl`
- Shadows: `shadow-lg`, `shadow-2xl`, custom shadows

#### Animation Classes
```css
/* Tailwind Animate */
animate-in fade-in zoom-in      /* Entry animation */
animate-pulse                    /* Loading indicator */
slide-in-from-right-8           /* Slide transition */

/* Framer Motion */
Used for complex page transitions and interactive elements
```

---

## 🗄 State Management

### Current Implementation: Local State
The application currently uses React's built-in `useState` for component-level state management.

### Redux Toolkit (Available for Scaling)
Redux is installed and ready for global state management when needed:

```javascript
import { configureStore } from '@reduxjs/toolkit'
import { Provider } from 'react-redux'

// Future store configuration
const store = configureStore({
  reducer: {
    // Add slices here
  }
})
```

### Data Flow
```
User Upload → Local State → API Call → Navigation State → Report Display
                                    ↓
                              sessionStorage (PDF URL)
```

---

## 🔌 API Integration

### Backend Endpoint

**URL:** `VITE_BACKEND_URL` (from environment variables)

**Request:**
```http
POST /analyze
Content-Type: multipart/form-data

Body:
{
  file: <PDF File>
}
```

**Response:**
```json
{
  "final_ats_score": 45,
  "impact_score": 7,
  "structure_score": 15,
  "clarity_score": 3,
  "skill_score": 20,
  "feedback": "Your resume shows strong technical skills..."
}
```

**Error Handling:**
```javascript
try {
  const res = await axios.post(BACKEND_URL, formData)
  // Success
} catch (e) {
  setError("Analysis failed. Please try again.")
  console.error(e)
}
```

---

## 💻 Development

### Available Scripts

```bash
# Start development server with HMR
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview
```

### Development Server
- **URL:** http://localhost:5173
- **Hot Module Replacement:** Enabled
- **Fast Refresh:** React components update without full reload

### Code Style
- Use functional components with hooks
- Prefer arrow functions for component definitions
- Use destructuring for props and state
- Keep components focused and single-purpose
- Use Tailwind utility classes for styling

### Best Practices
```jsx
// ✅ Good: Functional component with hooks
const MyComponent = () => {
  const [state, setState] = useState(initial)
  
  return <div className="p-4">...</div>
}

// ✅ Good: Destructured props
const Card = ({ title, children }) => {
  return <div>{title}{children}</div>
}

// ✅ Good: Early returns for edge cases
if (!data) return <Loading />
```

---

## 📦 Build & Deploy

### Production Build

```bash
# Build optimized bundle
npm run build

# Output directory: dist/
# - index.html
# - assets/
#   ├── index-[hash].js
#   └── index-[hash].css
```

### Build Optimization
- Code splitting by route
- CSS purging with Tailwind
- Asset optimization and compression
- Tree-shaking for unused code

### Deployment Options

#### Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Environment variables set via Vercel dashboard
```

#### Netlify
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

#### Build Configuration
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "environmentVariables": {
    "VITE_BACKEND_URL": "your-backend-url"
  }
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: "Module not found" errors
**Solution:**
```bash
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Environment variables not working
**Solution:**
- Ensure `.env` file exists in frontend root
- Variables must start with `VITE_`
- Restart dev server after changes

#### Issue: PDF not displaying in report
**Solution:**
- Check browser console for CORS errors
- Verify PDF URL in sessionStorage
- Ensure iframe allows PDF display

#### Issue: API calls failing
**Solution:**
- Verify `VITE_BACKEND_URL` is correct
- Check network tab for request details
- Ensure backend CORS is configured

#### Issue: Styles not applying
**Solution:**
```bash
# Rebuild Tailwind
npm run dev
# Or clear Vite cache
rm -rf node_modules/.vite
```

### Debug Mode

```javascript
// Add to vite.config.js for verbose logging
export default defineConfig({
  logLevel: 'info',
  clearScreen: false
})
```

---

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Framer Motion](https://www.framer.com/motion/)
- [Axios Documentation](https://axios-http.com)

---

## 🤝 Contributing

When contributing to the frontend:

1. Follow the existing code structure
2. Use Tailwind utilities instead of custom CSS
3. Test on multiple screen sizes
4. Ensure accessibility standards
5. Add JSDoc comments for complex functions
6. Update this README for significant changes

---

## 📄 License

MIT License - See parent repository for details.

---

<div align="center">

**Built with React + Vite + Tailwind CSS**

⚡️ Fast | 🎨 Beautiful | 📱 Responsive

</div>
