import React, { useState, useEffect } from "react";

const ATSReport = () => {
    const score = 92;
    const improvementAreas = [
        "Add measurable achievements to experience",
        "Use more industry-focused keywords",
        "Optimize resume formatting for ATS scanning",
        "Expand skill section with hard skills",
    ];

    const [pdf, setPdf] = useState()

    const radius = 80;
    const semiLength = Math.PI * radius;
    const dashOffset = semiLength * (1 - score / 100);

    useEffect(() => {
        const pdfURL = sessionStorage.getItem("pdfURL");
        setPdf(pdfURL);
    }, []);


    return (
        <div className="w-full min-h-screen bg-[#ebe3cc] flex items-center justify-center py-12">
            <div className="bg-white w-[650px] p-10 rounded-xl shadow-xl">

                <h2 className="text-4xl font-black mb-2 text-center">
                    Your Resume Score
                </h2>
                <p className="text-gray-600 text-center mb-10">
                    Here’s your ATS compatibility result & suggestions to improve.
                </p>

                <div className="flex flex-col items-center mb-10">
                    <svg className="w-48 h-32" viewBox="0 0 180 100">
                        <path
                            d="M10 90 A80 80 0 0 1 170 90"
                            stroke="#ddd"
                            strokeWidth="16"
                            fill="none"
                        />

                        <path
                            d="M10 90 A80 80 0 0 1 170 90"
                            stroke="#16a34a"
                            strokeWidth="16"
                            fill="none"
                            strokeDasharray={semiLength}
                            strokeDashoffset={dashOffset}
                            strokeLinecap="round"
                        />

                    </svg>
                    <p className="mt-3 text-3xl font-bold">
                        {score}
                        <span className="text-lg text-gray-600">/100</span>
                    </p>
                </div>

                <h3 className="text-lg font-semibold text-gray-800 mb-3 uppercase">
                    Suggestions for Improvement
                </h3>

                <ul className="mb-6 space-y-2">
                    {improvementAreas.map((point, i) => (
                        <li key={i} className="text-gray-700 flex items-center gap-2">
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth="2"
                                stroke="green"
                                className="w-5 h-5"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                                />
                            </svg>

                            {point}
                        </li>
                    ))}
                </ul>

                <button className="w-full mt-10 bg-black hover:bg-gray-900 text-white py-3 rounded-lg cursor-pointer text-lg font-medium transition">
                    Upload Another Resume
                </button>
            </div>
        </div>
    );
}

export default ATSReport;
