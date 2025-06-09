from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from werkzeug.utils import secure_filename
import docx2txt
import PyPDF2
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Adzuna API credentials (replace with your own)
ADZUNA_APP_ID = 'e6a06608'
ADZUNA_APP_KEY = 'b7c5080187203f791e584ac80d804820'

def fetch_jobs(query, country='in', location='', job_type='', experience='', remote=False):
    url = f'https://api.adzuna.com/v1/api/jobs/{country}/search/1'
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'results_per_page': 20,
        'what': query,
        'where': location,
        'content-type': 'application/json'
    }
    if job_type.lower() == 'full-time':
        params['full_time'] = 1
    elif job_type.lower() == 'part-time':
        params['part_time'] = 1

    if experience:
        params['experience'] = experience.lower()

    if remote:
        params['telecommute'] = 1

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        jobs = []
        for job in data.get('results', []):
            jobs.append({
                'title': job.get('title'),
                'company': job.get('company', {}).get('display_name'),
                'location': job.get('location', {}).get('display_name'),
                'description': job.get('description'),
                'url': job.get('redirect_url')
            })
        return jobs
    else:
        print(f"Error fetching jobs: {response.status_code}")
        return []

def extract_keywords(text):
    # Simple keyword extraction by finding frequent words (excluding common stopwords)
    stopwords = set([
        'the', 'and', 'to', 'of', 'in', 'a', 'for', 'with', 'on', 'as', 'is',
        'at', 'by', 'an', 'be', 'this', 'that', 'or', 'from', 'are', 'we', 'you',
        'your', 'will', 'can', 'which', 'our', 'have', 'has', 'also', 'but', 'if',
        'not', 'may', 'more', 'such', 'all', 'these', 'they', 'their'
    ])
    words = re.findall(r'\b\w+\b', text.lower())
    freq = {}
    for w in words:
        if w not in stopwords and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    # Return top 10 keywords sorted by frequency
    keywords = sorted(freq, key=freq.get, reverse=True)[:10]
    return keywords

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    query = country = location = job_type = experience = ''
    remote = False

    if request.method == 'POST':
        query = request.form['query']
        country = request.form.get('country', 'in')
        location = request.form.get('location', '')
        job_type = request.form.get('job_type', '')
        experience = request.form.get('experience', '')
        remote = request.form.get('remote') == 'on'
        jobs = fetch_jobs(query, country, location, job_type, experience, remote)

    return render_template("main.html", jobs=jobs, query=query, country=country,
                                  location=location, job_type=job_type,
                                  experience=experience, remote=remote)
@app.route('/more')
def more():
    return render_template('more.html')




@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    jobs = []
    keywords = []
    if request.method == 'POST':
        if 'resume' not in request.files:
            return "No file part"
        file = request.files['resume']
        if file.filename == '':
            return "No selected file"
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract text depending on file type
        text = ''
        if filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ''
        elif filename.endswith('.docx'):
            text = docx2txt.process(filepath)
        else:
            return "Unsupported file type. Please upload PDF or DOCX."

        keywords = extract_keywords(text)
        query = ' '.join(keywords)

        # Fetch jobs based on extracted keywords
        jobs = fetch_jobs(query)

        # If no jobs found, try searching each keyword individually and merge
        if not jobs:
            combined_jobs = []
            for kw in keywords:
                partial_jobs = fetch_jobs(kw)
                combined_jobs.extend(partial_jobs)
            seen = set()
            unique_jobs = []
            for job in combined_jobs:
                if job['url'] not in seen:
                    seen.add(job['url'])
                    unique_jobs.append(job)
            jobs = unique_jobs

    return render_template("resume_upload.html", jobs=jobs, keywords=keywords)

# HTML Templates



if __name__ == '__main__':
    app.run(debug=True)
