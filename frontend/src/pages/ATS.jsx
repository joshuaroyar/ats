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
  const inputRef = useRef(null);
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-16 items-center">

          {/* Left Column */}
          <div className="flex flex-col justify-center gap-6">
            <div>
              <h1 className="text-3xl md:text-5xl font-bold text-slate-900 tracking-tight leading-tight">
                Is your resume <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  ATS Ready?
                </span>
              </h1>
              <p className="mt-4 text-base md:text-lg text-slate-600 leading-relaxed max-w-lg">
                Stop guessing. Get an AI-powered score and actionable fixes to land your dream job.
              </p>
            </div>

            {/* Upload Card */}
            <div
              className={`bg-white/80 backdrop-blur-xl border-2 border-dashed rounded-3xl p-6 w-full relative transition-all duration-300 shadow-sm
                ${dragActive ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 hover:border-blue-400 hover:shadow-md'}`}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]) }}
            >

              <div className="flex flex-col items-center justify-center text-center cursor-pointer p-6" onClick={() => !fileInfo && !isAnalyzing && inputRef.current.click()}>
                <input ref={inputRef} type="file" accept="application/pdf" onChange={(e) => handleFile(e.target.files[0])} className="hidden" disabled={isAnalyzing} />

                {fileInfo ? (
                  <div className="flex flex-col items-center animate-in fade-in zoom-in">
                    <div className="w-14 h-14 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-3 shadow-sm">
                      <Icons.CheckCircle />
                    </div>
                    <h3 className="text-base font-bold text-slate-800">{fileInfo.name}</h3>
                    {isAnalyzing ? (
                      <div className="flex items-center gap-2 text-blue-600 text-sm font-medium animate-pulse mt-3">
                        <span className="w-2 h-2 bg-blue-600 rounded-full animate-ping"></span>
                        Analyzing...
                      </div>
                    ) : (
                      <p className="text-slate-500 text-sm mt-2">Redirecting...</p>
                    )}
                  </div>
                ) : (
                  <>
                    <div className="w-14 h-14 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4 shadow-sm group-hover:scale-110 transition-transform">
                      <Icons.Upload />
                    </div>
                    <h3 className="text-xl font-bold text-slate-800 mb-2">Upload Resume</h3>
                    <p className="text-slate-500 mb-6 text-sm">
                      Drag & drop PDF <br />
                      <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mt-1 inline-block">Max 5MB</span>
                    </p>

                    <button className="bg-gradient-to-r from-slate-800 to-slate-900 text-white px-8 py-3 rounded-xl font-semibold text-sm shadow-lg hover:shadow-slate-900/20 hover:-translate-y-0.5 transition-all cursor-pointer">
                      Select File
                    </button>
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

          {/* Right Column - Image */}
          <div className="hidden lg:flex flex-col items-center justify-center relative h-[500px]">
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-100 to-indigo-100 rounded-[3rem] rotate-3 scale-95 -z-10" />
            <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl border-4 border-white overflow-hidden flex items-center justify-center h-full relative">
              <img src="/resume-checker.webp" alt="Preview" className="w-full h-full object-cover" onError={(e) => { e.target.style.display = 'none'; }} />
              <span className="text-slate-300 font-medium absolute z-0 pointer-events-none">Preview Image</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ATS;