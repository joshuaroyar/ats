import React, { useEffect } from "react";
import { Route, Routes } from "react-router-dom";
import ATS from "./pages/ATS"; 
import ATSReport from "./pages/ATSReport";

const App = () => {
  return (
    <>
      <Routes>
        
        {/* ATS Routes */}
        <Route path="/" element={<ATS />} />
        <Route path="/ats-score" element={<ATS />} />
        <Route path="/ats-score/report" element={<ATSReport />} />

      </Routes>
    </>
  );
};

export default App;