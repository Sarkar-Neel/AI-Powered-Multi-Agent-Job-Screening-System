import React from 'react';
// import ReactDOM from 'react-dom'
// import logo from './logo.svg';
import './App.css';
import UserRole from './pages/UserRole';
import ResumeUpload from './pages/ResumeUpload';
import CandidateDashboard from './pages/CandidateDashboard'
import Recruiter from './pages/Recruiter';
import RecruiterDashboard from './pages/RecruiterDashboard';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
function App() {
  return (
    <Router>
      <Routes>
        <Route path='/' element={<UserRole/>} />
        <Route path="/candidate" element={<ResumeUpload/>} />
        <Route path='/recruiter' element={<Recruiter/>} />
        <Route path="/candidate-dashboard" element={<CandidateDashboard />} />
        <Route path="/recruiter-dashboard/:job_id" element={<RecruiterDashboard />} />
      </Routes>
    </Router>    
  );
}

export default App;
