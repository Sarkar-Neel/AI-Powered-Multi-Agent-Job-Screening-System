
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";

function RecruiterDashboard() {
  // const [searchParams] = useSearchParams();
  // const job_id = searchParams.get("job_id");
  const [candidates, setCandidates] = useState([]);
  const [status, setStatus] = useState("Fetching candidates...");
  const { job_id } = useParams();
  const fetchCandidates = async () => {
    try {
      const res = await axios.get(`http://localhost:5000/run-shortlist-job?job_id=${job_id}`);
      setCandidates(res.data);
      if (res.data.length === 0) {
        setStatus("No candidates found for this job.");
      } else {
        setStatus("");
      }
    } catch (err) {
      console.error(err);
      setStatus("Failed to fetch candidates.");
    }
  };

  useEffect(() => {
    if (job_id) {
      fetchCandidates();
    } else {
      setStatus("Missing job ID.");
    }
  }, [job_id]);

  const handleShortlist = async () => {
    try {
      await axios.post(`http://localhost:5000/run-shortlist-job?job_id=${job_id}`);
      alert("Shortlisting completed.");
      fetchCandidates(); // refresh list
    } catch (err) {
      console.error(err);
      alert("Shortlisting failed.");
    }
  };

  const handleSchedule = async () => {
    try {
      await axios.post(`http://localhost:5000/schedule-interviews?job_id=${job_id}`);
      alert("Interviews scheduled.");
    } catch (err) {
      console.error(err);
      alert("Interview scheduling failed.");
    }
  };

  return (
    <div className="container mt-5">
      <h2>Recruiter Dashboard</h2>
      <p>{status}</p>
      {candidates.length > 0 && (
        <>
          <table className="table table-striped mt-4">
            <thead>
              <tr>
                <th>Candidate ID</th>
                <th>Name</th>
                <th>Match Score (%)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c, index) => (
                <tr key={index}>
                  <td>{c.candidate_id}</td>
                  <td>{c.name}</td>
                  <td>{(c.match_score * 100).toFixed(2)}%</td>
                  <td>{c.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="btn btn-primary me-3" onClick={handleShortlist}>Shortlist Candidates</button>
          <button className="btn btn-success" onClick={handleSchedule}>Schedule Interviews</button>
        </>
      )}
    </div>
  );
}

export default RecruiterDashboard;
