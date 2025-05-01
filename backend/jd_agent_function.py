
import pandas as pd
import numpy as np
import ollama
import sqlite3 as sq
import re
import pickle

model_name = "gemma2:2B"

def parse_jd_response(response_text):
    job_name, job_summary, skills, qualifications, experience = "", "", "", "", ""

    try:
        job_name = re.search(r'## Job Name:\s*(.*?)\n', response_text, re.DOTALL).group(1).strip()
    except AttributeError:
        pass

    try:
        job_summary = re.search(r'## Job Summary:\s*(.*?)(## Skills Required:|$)', response_text, re.DOTALL).group(1).strip()
    except AttributeError:
        pass

    try:
        skills_section = re.search(r'## Skills Required:\s*(.*?)(## Qualifications:|$)', response_text, re.DOTALL)
        if skills_section:
            skills_text = skills_section.group(1).strip()
            skills_list = re.findall(r'\d+\.\s*(.*)', skills_text)
            skills = ', '.join(skills_list)
    except AttributeError:
        pass

    try:
        qualifications_section = re.search(r'## Qualifications:\s*(.*?)(## Experience:|$)', response_text, re.DOTALL)
        if qualifications_section:
            qualifications_text = qualifications_section.group(1).strip()
            qualifications_list = re.findall(r'\d+\.\s*(.*)', qualifications_text)
            qualifications = ', '.join(qualifications_list)
    except AttributeError:
        pass

    try:
        experience_section = re.search(r'## Experience:\s*(.*?)(##|$)', response_text, re.DOTALL)
        if experience_section:
            experience_text = experience_section.group(1).strip()
            experience_list = re.findall(r'\d+\.\s*(.*)', experience_text)
            experience = ', '.join(experience_list)
    except AttributeError:
        pass

    return job_name, job_summary, skills, qualifications, experience

def run_jd_agent(job_title, job_description):
    conn = sq.connect("mydatabase.db")
    cursor = conn.cursor()

    prompt = f"""Job Title: {job_title}
    Job Description: {job_description}
    Please read the above job description and provide the following information in the exact format shown below:
    ## Job Name: [Provide the name of the job]
    ## Job Summary: [Provide a brief summary of the job]
    ## Skills Required: [Provide a numbered list of skills required]
    ## Qualifications: [Provide a numbered list of qualifications required]
    ## Experience: [Provide a numbered list of required experience]
    """

    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    response_text = response["message"]["content"]

    job_name, job_summary, skills, qualifications, experience = parse_jd_response(response_text)

    # Embedding
    skill_embed = ollama.embeddings(model="nomic-embed-text", prompt=skills)["embedding"]
    qualification_embed = ollama.embeddings(model="nomic-embed-text", prompt=qualifications)["embedding"]
    experience_embed = ollama.embeddings(model="nomic-embed-text", prompt=experience)["embedding"]

    skill_embed_blob = pickle.dumps(skill_embed)
    qualification_embed_blob = pickle.dumps(qualification_embed)
    experience_embed_blob = pickle.dumps(experience_embed)

    cursor.execute("""
        INSERT INTO jobs (jb_text, summary, skill, qualifications, experience, skill_embed, qualification_embed, experience_embed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (job_name, job_summary, skills, qualifications, experience, skill_embed_blob, qualification_embed_blob, experience_embed_blob))

    conn.commit()
    job_id = cursor.lastrowid
    conn.close()

    print(f"✔️ Job processed and stored with ID: {job_id}")
    return job_id
