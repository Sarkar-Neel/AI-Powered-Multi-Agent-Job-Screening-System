import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Recruiter() {
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jobTitle || !jobDescription) {
      alert("Please fill out all fields.");
      return;
    }

    const formData = new FormData();
    formData.append('title', jobTitle);
    formData.append('description', jobDescription);

    try {
      const response = await fetch('http://localhost:5000/post-job', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();  // parse JSON response
        const jobId = data.job_id;
        alert("Job posted successfully!");
        navigate(`/recruiter-dashboard/${jobId}`);  // pass job_id to URL
      } else {
        alert("Failed to post job.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="page-container">
      <h2>Recruiter - Post a Job</h2>
      <form onSubmit={handleSubmit} className="form-container">
        <label>
          Job Title:
          <input
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            required
          />
        </label>

        <label>
          Job Description:
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={5}
            required
          />
        </label>

        <button type="submit">Post Job</button>
      </form>
    </div>
  );
}

export default Recruiter;
