import React from "react";
import { useNavigate } from "react-router-dom";
import './UserRole.css'
function UserRole() {
    const navigate = useNavigate();

    return (
        <div className="page-container ">
            <div className>
                <div >
                    <div className="role-card recruiter-card">
                        <h2 >Recruiter</h2>
                        <p>Post your job description to find the most eligible candidates</p>
                        <button onClick={() => navigate("/recruiter")}> Login</button>
                    </div>
                </div>
                <div >
                    <div className="role-card candidate-card">
                        <h2>Candidate</h2>
                        <p>are you here to find jobs</p>
                        <button onClick={() => navigate("/candidate")}>Login</button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default UserRole;