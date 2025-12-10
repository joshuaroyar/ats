import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

// Icons
const Icons = {
  Upload: () => <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242" /><path d="M12 12v9" /><path d="m16 16-4-4-4 4" /></svg>,
  CheckCircle: () => <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>,
  AlertCircle: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="12" x2="12" y1="8" y2="12" /><line x1="12" x2="12.01" y1="16" y2="16" /></svg>,
};

const ATS = () => {
  const navigate = useNavigate();
  const [dragActive, setDragActive] = useState(false);
  const [fileInfo, setFileInfo] = useState(null);
  const [error, setError] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [jdText, setJdText] = useState("");
  const [jdFileName, setJdFileName] = useState("");
  const [jdFile, setJdFile] = useState(null);
  const inputRef = useRef(null);
  const jdFileRef = useRef(null);
  const MAX_SIZE = 5;
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;


  const handleFile = async (file) => {
    if (!file) return;
    setError("");
    if (file.type !== "application/pdf") { setError("Only PDF files are allowed."); return; }
    if (file.size > MAX_SIZE * 1024 * 1024) { setError(`File exceeds ${MAX_SIZE}MB limit.`); return; }

    setFileInfo({ name: file.name, size: (file.size / 1024 / 1024).toFixed(2) + " MB" });
    setIsAnalyzing(true);

    try {
      const fileURL = URL.createObjectURL(file);
      sessionStorage.setItem("pdfURL", fileURL);

      const formData = new FormData();
      formData.append("file", file);
      // Attach JD text or JD file if provided
      if (jdText && jdText.trim()) {
        formData.append("jd_text", jdText);
      } else if (jdFile) {
        formData.append("jd_file", jdFile, jdFile.name);
      }
      // Request AI feedback from backend
      formData.append("include_feedback", "true");

      // Make the API call
      const res = await axios.post(BACKEND_URL, formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      const atsData = res.data;

      navigate("/ats-score/report", { state: { atsData } });

    } catch (e) {
      setError("Analysis failed. Please try again.");
      console.error(e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="h-full w-full bg-slate-50 relative overflow-y-auto overflow-x-hidden flex justify-center">
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-100/50 rounded-full blur-3xl opacity-60" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-indigo-100/50 rounded-full blur-3xl opacity-60" />
      </div>

      <div className="w-full max-w-6xl p-6 md:p-10 flex flex-col justify-center min-h-[600px]">
        <div className="flex w-full justify-center">
          <div className="w-full max-w-2xl space-y-6">
            <div className="text-center relative">
              {/* animated gradient background accents */}
              <div aria-hidden className="pointer-events-none absolute -top-20 -left-20 w-72 h-72 rounded-full opacity-30 blur-3xl transform-gpu animate-blob" />
              <div aria-hidden className="pointer-events-none absolute -bottom-16 -right-16 w-80 h-80 rounded-full opacity-30 blur-3xl transform-gpu animate-blob animation-delay-2000" />
              {/* animations moved to global CSS (frontend/src/index.css) */}
              <h1 className="text-3xl md:text-4xl font-bold text-slate-900 tracking-tight leading-tight">
                Is your resume <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">ATS Ready?</span>
              </h1>
              <p className="mt-3 text-sm text-slate-600">Upload a resume and optionally provide a job description to evaluate against.</p>
            </div>

            {/* Job Description Card */}
            <div className="bg-white/20 backdrop-blur-md rounded-3xl p-6 w-full shadow-lg border border-white/10 transition-transform transform hover:-translate-y-1 hover:scale-[1.01] will-change-transform">
              <div className="absolute inset-0 rounded-3xl animated-gradient animate-gradientShift opacity-10 pointer-events-none -z-10" />
              <h3 className="text-lg font-bold text-slate-900 mb-2">Job Description</h3>
              <p className="text-sm text-slate-600 mb-4">Paste the job description below or upload a .txt file.</p>
              <textarea
                value={jdText}
                onChange={(e) => { setJdText(e.target.value); if (e.target.value) { setJdFileName(''); setJdFile(null); } }}
                placeholder="Paste job description here..."
                className="w-full min-h-[120px] p-3 rounded-xl border border-white/20 mb-3 text-sm bg-white/10 placeholder:text-slate-400 text-slate-900 transition-shadow focus:shadow-lg focus:outline-none"
              />
              <div className="flex items-center gap-3">
                <input ref={jdFileRef} type="file" accept=".txt,text/plain" className="hidden" onChange={(e) => {
                  const f = e.target.files[0];
                  if (f) { setJdFileName(f.name); setJdFile(f); setJdText(''); }
                }} />
                <button type="button" className="px-4 py-2 bg-white/10 text-slate-900 rounded-lg text-sm backdrop-blur-sm border border-white/10 hover:scale-[1.02] transition-transform shadow-sm" onClick={() => jdFileRef.current && jdFileRef.current.click()}>
                  Upload JD (.txt)
                </button>
                <span className="text-sm text-slate-600">{jdFileName || 'No file selected'}</span>
              </div>
            </div>

            {/* Upload Card */}
            <div className={`relative overflow-hidden rounded-3xl p-6 w-full transition-shadow duration-300 ${dragActive ? 'ring-2 ring-blue-400/60' : 'ring-1 ring-white/5'}`} onDragOver={(e) => { e.preventDefault(); setDragActive(true) }} onDragLeave={() => setDragActive(false)} onDrop={(e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]) }}>

              <div className="absolute inset-0 animated-gradient animate-gradientShift opacity-6 -z-10" />
              <div className="bg-white/10 backdrop-blur-md border border-white/8 rounded-3xl p-6 flex flex-col items-center text-center">
                <input ref={inputRef} type="file" accept="application/pdf" onChange={(e) => handleFile(e.target.files[0])} className="hidden" disabled={isAnalyzing} />

                {fileInfo ? (
                  <div className="flex flex-col items-center animate-in fade-in zoom-in">
                    <div className="w-14 h-14 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-3 shadow-sm">
                      <Icons.CheckCircle />
                    </div>
                    <h3 className="text-base font-bold text-slate-900">{fileInfo.name}</h3>
                    {isAnalyzing ? (
                      <div className="flex items-center gap-2 text-blue-200 text-sm font-medium animate-pulse mt-3">
                        <span className="w-2 h-2 bg-blue-200 rounded-full animate-ping"></span>
                        Analyzing...
                      </div>
                    ) : (
                      <p className="text-slate-300 text-sm mt-2">Redirecting...</p>
                    )}
                  </div>
                ) : (
                  <>
                    <div className="w-16 h-16 bg-white/10 text-slate-900 rounded-full flex items-center justify-center mb-4 shadow-md transform transition-transform hover:scale-105">
                      <Icons.Upload />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Upload Resume</h3>
                    <p className="text-slate-600 mb-6 text-sm">Drag & drop PDF or click to select<br /><span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider mt-1 inline-block">Max 5MB</span></p>

                    <div className="flex items-center gap-3">
                      <button onClick={() => inputRef.current && inputRef.current.click()} className="bg-white/90 text-slate-900 px-6 py-2 rounded-xl font-semibold text-sm shadow-md hover:translate-y-[-1px] transition-transform">Select File</button>
                      <button onClick={() => { setJdText(''); setJdFile(null); setJdFileName(''); }} className="px-4 py-2 bg-white/10 text-slate-800 rounded-md text-sm">Clear JD</button>
                    </div>
                  </>
                )}
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-100 rounded-xl flex items-center gap-3 text-red-600 text-sm font-medium animate-in slide-in-from-top-2">
                  <Icons.AlertCircle />{error}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ATS;