
import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";

function CandidateDashboard() {
  const [searchParams] = useSearchParams();
  const candidateId = searchParams.get("candidate_id");
  const [matches, setMatches] = useState([]);
  const [status, setStatus] = useState("Fetching job matches...");

  useEffect(() => {
    if (candidateId) {
      axios
        .get(`http://localhost:5000/run-shortlist?candidate_id=${candidateId}`)
        .then((res) => {
          setMatches(res.data);
          if (res.data.length === 0) {
            setStatus("No job matches found.");
          } else {
            setStatus("");
          }
        })
        .catch((err) => {
          console.error(err);
          setStatus("Failed to fetch matches.");
        });
    } else {
      setStatus("Missing candidate ID.");
    }
  }, [candidateId]);

  return (
    <div className="container mt-5">
      <h2>Job Match Results</h2>
      <p>{status}</p>
      {matches.length > 0 && (
        <table className="table table-bordered mt-3">
          <thead>
            <tr>
              <th>Job ID</th>
              <th>Match Score (%)</th>
            </tr>
          </thead>
          <tbody>
            {matches.map((match, index) => (
              <tr key={index}>
                <td>{match.job_id}</td>
                <td>{(match.match_score * 100).toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default CandidateDashboard;
