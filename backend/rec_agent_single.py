import os
import ollama
import pandas as pd
import numpy as np
import re
import sqlite3 as sq
from pypdf import PdfReader
import pickle



import re

def parse_candidate(response_text):
    # Initialize variables for each section
    c_id,name, email, phone, address, skills, qualifications, experience, certifications, achievements, tech_stack = "", "", "", "", "", "", "", "", "", "", ""

    # Extracting single-line sections using re.search()
    try:
        c_id = re.search(r'## ID:\s*(.*)', response_text).group(1).strip()
    except AttributeError:
        pass
    
    try:
        name = re.search(r'## Name:\s*(.*)', response_text).group(1).strip()
    except AttributeError:
        pass

    try:
        email = re.search(r'## Email:\s*(.*)', response_text).group(1).strip()
    except AttributeError:
        pass

    try:
        phone = re.search(r'## Phone Number:\s*(.*)', response_text).group(1).strip()
    except AttributeError:
        pass

    try:
        address = re.search(r'## Address:\s*(.*)', response_text).group(1).strip()
    except AttributeError:
        pass

    # Extracting numbered lists using re.findall()
    try:
        skills_section = re.search(r'## Skills:(.*?)(## Qualifications:|$)', response_text, re.DOTALL).group(1)
        skills_list = re.findall(r'\d+\.\s*(.*)', skills_section)
        skills = ', '.join(skills_list)
    except AttributeError:
        pass

    try:
        qualifications_section = re.search(r'## Qualifications:(.*?)(## Experience:|$)', response_text, re.DOTALL).group(1)
        qualifications_list = re.findall(r'\d+\.\s*(.*)', qualifications_section)
        qualifications = ', '.join(qualifications_list)
    except AttributeError:
        pass

    try:
        experience_section = re.search(r'## Experience:(.*?)(## Certifications:|$)', response_text, re.DOTALL).group(1)
        experience_list = re.findall(r'\d+\.\s*(.*)', experience_section)
        experience = ', '.join(experience_list)
    except AttributeError:
        pass

    try:
        certifications_section = re.search(r'## Certifications:(.*?)(## Achievements:|$)', response_text, re.DOTALL).group(1)
        certifications_list = re.findall(r'\d+\.\s*(.*)', certifications_section)
        certifications = ', '.join(certifications_list)
    except AttributeError:
        pass

    try:
        achievements_section = re.search(r'## Achievements:(.*?)(## Tech Stack:|$)', response_text, re.DOTALL).group(1)
        achievements_list = re.findall(r'\d+\.\s*(.*)', achievements_section)
        achievements = ', '.join(achievements_list)
    except AttributeError:
        pass

    try:
        tech_stack_section = re.search(r'## Tech Stack:(.*?)(##|$)', response_text, re.DOTALL).group(1)
        tech_stack_list = re.findall(r'\d+\.\s*(.*)', tech_stack_section)
        tech_stack = ', '.join(tech_stack_list)
    except AttributeError:
        pass

    # Return parsed data
    return c_id, name, email, phone, address, skills, qualifications, experience, certifications, achievements, tech_stack


dir_path = "DATA/CVs1/"

def run_rec_agent(filepath):
    model_name = "gemma2:2B"
    conn = sq.connect("mydatabase.db")
    cursor = conn.cursor()
    reader = PdfReader(filepath)

    print(len(reader.pages))
    line =""
    for i in range(len(reader.pages)):
        page = reader.pages[i]
        line += page.extract_text()

    # lines = line.split("\n")

    # print(lines)

    prompt = f'''
        CV_text = {line}
        Please read the above extracted text from CV of a Candidate and provide the following information in the exact format shown below:
        ## ID: [Provide the ID of the candidate]
        ## Name: [Provide the name of the candidate]
        ## Email: [Provide the email of the candidate]
        ## Phone Number: [Provide the phone number of the candidate]
        ## Address: [Provide the adress of the candidate of available]
        ## Skills: [Provide a numbered list of skills ]
        ## Qualifications: [Provide a numbered list of qualifications]
        ## Experience: [Provide a numbered list of experience]
        ## Certifications: [Provide a numbered list of certifications]
        ## Achievements: [Provide a numbered list of achievements]
        ## Tech Stack: [Provide a numbered list of Tech stack]
        '''
    try:
        response = ollama.chat(model_name,messages=[{"role":"user","content":prompt}])

        ans = response['message']['content']
        print(ans)
        c_id, name, email, phone, address, skills, qualifications, experience, certifications, achievements, tech_stack = parse_candidate(ans)

        print("C_id :",c_id)

        try:
            response = ollama.embeddings(model="nomic-embed-text", prompt = skills)
            skill_embed = response["embedding"]
            print("skill Embeddings :",skill_embed[:10])
            response = ollama.embeddings(model = "nomic-embed-text", prompt=qualifications)
            qualifications_embed = response["embedding"]
            print("Qualification Embeddings: ", qualifications_embed[:10])
            response = ollama.embeddings(model="nomic-embed-text",prompt=experience)
            experience_embed = response["embedding"]
            print("Experince Embeddings: ", experience_embed[:10])

            # Serialize embeddings using pickle before inserting into the database
            skill_embed_blob = pickle.dumps(skill_embed)
            qualifications_embed_blob = pickle.dumps(qualifications_embed)
            experience_embed_blob = pickle.dumps(experience_embed)
        except Exception as e:
            print(f"Error : {e}")

        cursor.execute( """ 
                            INSERT INTO candidates (c_id,name,email,phone,address,education,experience,skills,certifications,achievements,tech_stack, skill_embed, qualifications_embed, experience_embed)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",(c_id, name, email, phone, address,  qualifications, experience, skills, certifications, achievements, tech_stack, skill_embed_blob, qualifications_embed_blob, experience_embed_blob))

        conn.commit()
        print(f"Successfully Processed and Saved the Resume details for {name}")
    except Exception as e:
        print(f"Error processing CV of {name}. Error : {str(e)}")

    conn.close()    
    return c_id