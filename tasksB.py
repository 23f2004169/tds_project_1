# Phase B: LLM-based Automation Agent for DataWorks Solutions

# B1 & B2: Security Checks
import os
def B12(filepath):
    if filepath.startswith('/data'):
        # raise PermissionError("Access outside /data is not allowed.")
        # print("Access outside /data is not allowed.")
        return True
    else:
        return False

# B3: Fetch Data from an API
def B3(url, save_path):
    if not B12(save_path):
        return None
    import requests
    response = requests.get(url)
    with open(save_path, 'w') as file:
        file.write(response.text)

# B4: Clone a Git Repo and Make a Commit
def B4(repo_url, commit_message):
    import subprocess
    import os
    # Ensure the operation is restricted to /data
    repo_path = "/data/repo"
    if not B12(repo_path):
        return None
    # Clone the repository
    subprocess.run(["git", "clone", repo_url, repo_path], check=True)
    # Make a commit
    subprocess.run(["git", "-C", repo_path, "add", "."], check=True)
    subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_message], check=True)
    return f"Repository cloned to {repo_path} and commit made with message: {commit_message}"

# B5: Run SQL Query
def B5(db_path, query, output_filename):
    if not B12(db_path):
        return None
    import sqlite3, duckdb
    conn = sqlite3.connect(db_path) if db_path.endswith('.db') else duckdb.connect(db_path)
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchall()
    conn.close()
    with open(output_filename, 'w') as file:
        file.write(str(result))
    return result

# B6: Web Scraping
def B6(url, output_filename):
    import requests
    result = requests.get(url).text
    with open(output_filename, 'w') as file:
        file.write(str(result))

# B7: Image Processing
def B7(image_path, output_path, resize=None):
    from PIL import Image
    if not B12(image_path):
        return None
    if not B12(output_path):
        return None
    img = Image.open(image_path)
    if resize:
        img = img.resize(resize)
    img.save(output_path)

# B8: Audio Transcription
def B8(audio_path, output_path):
    import openai
    # Ensure the operation is restricted to /data
    if not B12(audio_path):
        return None
    if not B12(output_path):
        return None
    # Transcribe the audio file
    with open(audio_path, 'rb') as audio_file:
        transcription = openai.Audio.transcribe("whisper-1", audio_file)
    # Save the transcription to the output file
    with open(output_path, 'w') as file:
        file.write(transcription['text'])
    return transcription['text']

# B9: Markdown to HTML Conversion
def B9(md_path, output_path):
    import markdown
    if not B12(md_path):
        return None
    if not B12(output_path):
        return None
    with open(md_path, 'r') as file:
        html = markdown.markdown(file.read())
    with open(output_path, 'w') as file:
        file.write(html)

#B10: API Endpoint for CSV Filtering
import csv
import json
#Write an API endpoint that filters a CSV file and returns JSON data
def filter_csv(input_file: str, column: str, value: str, output_file: str):
    results = []
    with open(input_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[column] == value:
                results.append(row)
    with open(output_file, "w") as file:
        json.dump(results, file)

# B10: API Endpoint for CSV Filtering
def B10(input_file, column, value, output_file):
    import csv
    import json
    # Ensure the operation is restricted to /data
    if not B12(input_file):
        return None
    if not B12(output_file):
        return None
    # Filter the CSV file
    results = []
    with open(input_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[column] == value:
                results.append(row)
    # Save the filtered results to the output file
    with open(output_file, "w") as file:
        json.dump(results, file)

    return results