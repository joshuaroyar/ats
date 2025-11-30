import React, { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router";

const ATS = () => {
  const [dragActive, setDragActive] = useState(false);
  const [fileInfo, setFileInfo] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);
  const navigate = useNavigate()

  const MAX_SIZE = 5; // MB

  const validateFile = (file) => {
    setError("");
    if (!file) return false;

    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed ❗");
      return false;
    }

    if (file.size > MAX_SIZE * 1024 * 1024) {
      setError("File exceeds 5MB limit ❗");
      return false;
    }

    return true;
  };

  const handleFile = (file) => {
    if (!file) return;
    if (!validateFile(file)) return;
    setFileInfo({
      name:file.name,
      size:file.size
    })

    //creating URL for pdf
    //might display later
    const fileURL = URL.createObjectURL(file);
    sessionStorage.setItem("pdfURL", fileURL);

    navigate(`/ats-score/report`)
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFile(droppedFile);
  }, []);

  const onDragOver = (e) => e.preventDefault();
  const onDragEnter = () => setDragActive(true);
  const onDragLeave = () => setDragActive(false);

  return (
    <div className="min-h-screen bg-[#EFE6CF] flex items-center justify-center px-8 py-20 text-black">

      <div className="w-full max-w-7xl grid grid-cols-1 md:grid-cols-2 gap-10 items-center">

        <div className="flex flex-col gap-6 text-center md:text-left">

          <h1 className="text-5xl md:text-6xl font-bold">
            Is your resume good enough?
          </h1>

          <p className="text-neutral-700 text-lg max-w-lg">
            Upload your resume and get AI-powered ATS score, keyword analysis and improvement suggestions instantly.
          </p>

          <div className="bg-white shadow-xl border border-black rounded-2xl p-8 w-full">

            <div
              className={`border-2 border-dashed rounded-xl p-10 text-center transition duration-200 hover:border-black cursor-pointer 
              ${dragActive ? "border-black bg-neutral-100 scale-[1.02]" : "border-gray-400"}`}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onDragEnter={onDragEnter}
              onDragLeave={onDragLeave}
              onClick={() => inputRef.current.click()}
            >
              <p className="text-xl font-semibold mb-2">{fileInfo ? fileInfo.name : 'Drag & Drop Resume'}</p>
              <p className="text-sm text-neutral-500">PDF Format • Max 5MB</p>

              <label className="inline-block mt-6">
                <div className="bg-black text-white px-6 py-3 rounded-lg text-sm font-medium cursor-pointer hover:bg-gray-900 transition">
                  Select File
                </div>
                <input
                  ref={inputRef}
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => handleFile(e.target.files[0])}
                  className="hidden"
                />
              </label>

              {error && <p className="text-red-600 mt-3 text-sm">{error}</p>}
            </div>
          </div>

          <p className="text-xs text-neutral-600">Files are processed securely — No data stored.</p>
        </div>

        <div className="flex justify-center">
          <img
            src="/resume-checker.webp"
            className="w-[560px] h-[560px] rounded-xl"
          />
        </div>

      </div>
    </div>
  );
};

export default ATS;
