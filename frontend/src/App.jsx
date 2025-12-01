import { BrowserRouter, Route, Routes } from 'react-router-dom';
import React from 'react'
import './App.css';
import ATS from './pages/ATS';
import ATSReport from './pages/ATSReport';

function App() {

  return (
    <BrowserRouter>
    <Routes>
      <Route path='/ats-score' element={<ATS/>}/>
      <Route path='/ats-score/report' element={<ATSReport/>}/>
    </Routes>
    </BrowserRouter>
  )
}

export default App
