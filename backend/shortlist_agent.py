
import sqlite3
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

def get_embeddings(data):
    return np.array(pickle.loads(data)).reshape(1, -1)

def run_shortlisting_for_candidate(candidate_id):
    conn = sqlite3.connect("mydatabase.db")
    cur = conn.cursor()
    print(f"**{candidate_id}**")
    cur.execute("SELECT skill_embed, qualifications_embed, experience_embed FROM candidates WHERE c_id = ?", (candidate_id,))
    candidate_row = cur.fetchone()
    if not candidate_row:
        print("Candidate not found.")
        conn.close()
        return

    candidate_embeds = [get_embeddings(x) for x in candidate_row]
    cur.execute("SELECT id, skill_embed, qualification_embed, experience_embed FROM jobs")
    jobs = cur.fetchall()

    for job in jobs:
        job_id, j_skills, j_qual, j_exp = job
        job_embeds = [get_embeddings(j_skills), get_embeddings(j_qual), get_embeddings(j_exp)]
        similarities = [cosine_similarity(c, j)[0][0] for c, j in zip(candidate_embeds, job_embeds)]
        match_score = sum(similarities) / len(similarities)

        cur.execute("INSERT INTO shortlists (candidate_id, job_id, match_score, status) VALUES (?, ?, ?, ?)",
                    (candidate_id, job_id, match_score, 'Shortlisted' if match_score >= 0.7 else 'Not Shortlisted'))

    conn.commit()
    conn.close()
    print(f"Shortlisting complete for candidate {candidate_id}")

def run_shortlisting_for_job(job_id):
    conn = sqlite3.connect("mydatabase.db")
    cur = conn.cursor()

    cur.execute("SELECT skill_embed, qualification_embed, experience_embed FROM jobs WHERE id = ?", (job_id,))
    job_row = cur.fetchone()
    if not job_row:
        print("Job not found.")
        conn.close()
        return

    job_embeds = [get_embeddings(x) for x in job_row]
    cur.execute("SELECT c_id, skill_embed, qualifications_embed, experience_embed FROM candidates")
    candidates = cur.fetchall()

    shortlisted = []
    for candidate in candidates:
        c_id, c_skills, c_qual, c_exp = candidate
        candidate_embeds = [get_embeddings(c_skills), get_embeddings(c_qual), get_embeddings(c_exp)]
        similarities = [cosine_similarity(j, c)[0][0] for j, c in zip(job_embeds, candidate_embeds)]
        match_score = sum(similarities) / len(similarities)

        if match_score >= 0.7:
            shortlisted.append((c_id, match_score))
            cur.execute("INSERT INTO shortlists (candidate_id, job_id, match_score, status) VALUES (?, ?, ?, 'Shortlisted')",
                        (c_id, job_id, match_score))
        else:
            cur.execute("INSERT INTO shortlists (candidate_id, job_id, match_score, status) VALUES (?, ?, ?, 'Not Shortlisted')",
                        (c_id, job_id, match_score))

    conn.commit()
    conn.close()
    print(f"Shortlisting complete for job {job_id}")
