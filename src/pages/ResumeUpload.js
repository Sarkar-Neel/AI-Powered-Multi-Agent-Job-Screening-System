
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function ResumeUpload() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setStatus("❗ Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    try {
      setStatus("Uploading resume...");
      const uploadRes = await axios.post("http://localhost:5000/upload-resume", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        }
      });

      const candidateId = uploadRes.data.candidate_id;
      setStatus("Resume uploaded! Running shortlisting...");

      await axios.post(`http://localhost:5000/run-shortlist?candidate_id=${candidateId}`);

      navigate(`/candidate-dashboard?candidate_id=${candidateId}`);
    } catch (error) {
      console.error(error);
      setStatus("❌ Failed to upload or process resume.");
    }
  };

  return (
    <div className="page-container" style={{ padding: "2rem", textAlign: "center" }}>
      <h2>Upload Your Resume</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          style={{ marginBottom: "1rem" }}
        />
        <br />
        <button type="submit" className="btn btn-primary">Submit</button>
      </form>
      <p style={{ marginTop: "1rem" }}>{status}</p>
    </div>
  );
}

export default ResumeUpload;
