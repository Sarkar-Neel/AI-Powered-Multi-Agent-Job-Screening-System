
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from rec_agent_single import run_rec_agent
from shortlist_agent import run_shortlisting_for_candidate
import uuid
import sqlite3
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    file = request.files.get('resume')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = f"{uuid.uuid4().hex}.pdf"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    candidate_id = run_rec_agent(filepath)
    return jsonify({'message': 'Resume processed.', 'candidate_id': candidate_id})

from jd_agent_function import run_jd_agent

@app.route("/post-job", methods=["POST"])
def post_job():
    title = request.form.get("title")
    description = request.form.get("description")
    job_id = run_jd_agent(title, description)
    return jsonify({"message": "Job posted successfully.", "job_id": job_id})
# @app.route('/run-shortlist', methods=['POST'])
# def shortlist_candidate():
#     candidate_id = request.args.get('candidate_id')
#     if not candidate_id:
#         return jsonify({'error': 'Missing candidate_id'}), 400

#     run_shortlisting_for_candidate(candidate_id)
#     return jsonify({'message': 'Shortlisting completed.'})

# @app.route('/shortlists', methods=['GET'])
# def get_shortlists():
#     candidate_id = request.args.get('candidate_id')
#     import sqlite3
#     conn = sqlite3.connect("mydatabase.db")
#     cur = conn.cursor()

#     cur.execute("SELECT job_id, match_score FROM shortlists WHERE candidate_id = ?", (candidate_id,))
#     rows = cur.fetchall()
#     results = [{"job_id": row[0], "match_score": round(row[1], 2)} for row in rows]
#     conn.close()

#     return jsonify(results)


from shortlist_agent import run_shortlisting_for_candidate, run_shortlisting_for_job

@app.route('/run-shortlist', methods=['POST'])
def shortlist_candidate():
    candidate_id = request.args.get('candidate_id')
    if not candidate_id:
        return jsonify({'error': 'Missing candidate_id'}), 400

    run_shortlisting_for_candidate(candidate_id)
    return jsonify({'message': f'Shortlisting completed for candidate {candidate_id}.'})

@app.route('/run-shortlist-job', methods=['GET'])
def shortlist_job():
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "Missing job_id"}), 400

    conn = sqlite3.connect("mydatabase.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT s.candidate_id, c.name, s.match_score, s.status
        FROM shortlists s
        JOIN candidates c ON c.c_id = s.candidate_id
        WHERE s.job_id = ?
    """, (job_id,))
    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {"candidate_id": row[0], "name": row[1], "match_score": row[2], "status": row[3]}
        for row in rows
    ])


if __name__ == "__main__":
    app.run(debug=True)
