import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

const Icons = {
    ChevronLeft: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6" /></svg>,
    Score: () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" /></svg>,
    Feedback: () => <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
};

const ATSReport = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [pdfUrl, setPdfUrl] = useState(null);
    const [mounted, setMounted] = useState(false);
    const atsData = location.state?.atsData;

    useEffect(() => {
        const storedUrl = sessionStorage.getItem("pdfURL");
        if (storedUrl) setPdfUrl(storedUrl);
    }, []);

    // trigger mount animation when component is rendered
    useEffect(() => {
        const t = setTimeout(() => setMounted(true), 50);
        return () => { clearTimeout(t); setMounted(false); };
    }, []);

    if (!atsData || !pdfUrl) {
        return (
            <div className="h-full w-full flex flex-col items-center justify-center bg-slate-50 space-y-4">
                <p className="text-xl text-slate-600 font-medium">No report data found.</p>
                <button
                    onClick={() => navigate('/ats-score')}
                    className="flex items-center gap-2 bg-gradient-to-r from-slate-800 to-slate-900 text-white px-6 py-3 rounded-xl font-bold hover:shadow-lg transition-all cursor-pointer"
                >
                    <Icons.ChevronLeft /> Upload a Resume
                </button>
            </div>
        );
    }

    const ScoreItem = ({ label, value, max }) => {
        const percentage = (value / max) * 100;
        let barColor = percentage > 75 ? "bg-green-500" : percentage > 40 ? "bg-yellow-500" : "bg-red-500";
        return (
            <div className="mb-5">
                <div className="flex justify-between mb-2">
                    <span className="text-sm font-bold text-slate-700">{label}</span>
                    <span className="text-sm font-bold text-slate-900">{value} <span className="text-slate-400 font-normal">/ {max}</span></span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                    <div className={`${barColor} h-2.5 rounded-full transition-all duration-1000 ease-out shadow-sm`} style={{ width: `${percentage}%` }}></div>
                </div>
            </div>
        );
    };

    return (
        <div className="flex flex-col lg:flex-row h-full w-full bg-slate-50 overflow-hidden font-sans">

            {/* === LEFT SIDE: PDF PREVIEW === */}
            <div className="w-full lg:w-1/2 h-full bg-slate-200/50 p-4 lg:p-6 flex flex-col border-r border-slate-200">
                <div className="flex items-center justify-between mb-4">
                    <button
                        onClick={() => navigate('/ats-score')}
                        className="flex items-center gap-2 text-slate-600 hover:text-slate-900 font-medium transition-colors bg-white px-4 py-2 rounded-lg shadow-sm border border-slate-200"
                    >
                        <Icons.ChevronLeft /> Back to Upload
                    </button>
                    <h2 className="text-sm font-bold text-slate-500 uppercase tracking-wide">Resume Preview</h2>
                </div>
                <div className="flex-1 bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-300 relative">
                    <iframe src={pdfUrl} title="Resume PDF" className="w-full h-full" />
                </div>
            </div>

            {/* RIGHT SIDE: ATS REPORT DATA */}
            <div className="w-full lg:w-1/2 h-full overflow-y-auto p-6 lg:p-10 bg-white">
                <div className={`max-w-2xl mx-auto transition-transform duration-700 ease-out ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0'}`}>

                    {/* Final Score Header */}
                    <div className="text-center mb-10">
                        <h1 className="text-3xl font-black text-slate-900 mb-6">ATS Analysis Report</h1>

                        {/* Unified Brand Gradient Circle */}
                        <div className="inline-flex flex-col items-center justify-center bg-gradient-to-br from-white to-blue-50 rounded-full w-48 h-48 border-4 border-white shadow-2xl ring-4 ring-blue-50 relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-600/5" />
                            <span className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-blue-600 to-indigo-600 tracking-tight relative z-10">
                                {atsData.final_ats_score}
                            </span>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mt-1 relative z-10">Final Score</span>
                        </div>
                    </div>

                    {/* Detailed Scores Section */}
                    <div className="bg-white rounded-3xl p-8 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-100 mb-8">
                        <div className="flex items-center gap-4 mb-8 pb-4 border-b border-slate-50">
                            <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
                                <Icons.Score />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-slate-900">Score Breakdown</h2>
                                <p className="text-xs text-slate-500">Analysis across key metrics</p>
                            </div>
                        </div>

                        <ScoreItem label="Impact Score" value={atsData.impact_score} max={25} />
                        <ScoreItem label="Structure Score" value={atsData.structure_score} max={20} />
                        <ScoreItem label="Clarity Score" value={atsData.clarity_score} max={10} />
                        <ScoreItem label="Skill Score" value={atsData.skill_score} max={45} />
                    </div>

                    {/* Feedback Section */}
                    {atsData.feedback && (
                        <div className="bg-white rounded-3xl p-8 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-slate-100 mt-8">
                            <div className="flex items-center gap-4 mb-6 pb-4 border-b border-slate-50">
                                <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl">
                                    <Icons.Feedback />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-slate-900">AI Feedback</h2>
                                    <p className="text-xs text-slate-500">Generated insights & recommendations</p>
                                </div>
                            </div>
                            <div className="prose prose-slate max-w-none">
                                <div className="bg-slate-50 rounded-2xl p-6 text-slate-700 leading-relaxed whitespace-pre-line border border-slate-100">
                                    {atsData.feedback}
                                </div>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default ATSReport;