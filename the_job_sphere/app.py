from flask import Flask, render_template_string, request
import requests

app = Flask(__name__)

# Replace with your actual Adzuna credentials
ADZUNA_APP_ID = 'e6a06608'
ADZUNA_APP_KEY = 'b7c5080187203f791e584ac80d804820'

def fetch_jobs(query, location='India'):
    url = f'https://api.adzuna.com/v1/api/jobs/in/search/1'
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_APP_KEY,
        'results_per_page': 20,
        'what': query,
        'where': location,
        'content-type': 'application/json'
    }
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

@app.route('/', methods=['GET', 'POST'])
def index():
    jobs = []
    query = ''
    if request.method == 'POST':
        query = request.form['query']
        jobs = fetch_jobs(query)
    return render_template_string(template, jobs=jobs, query=query)

template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Job Search</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f4; }
        h1 { text-align: center; }
        form { text-align: center; margin-bottom: 30px; }
        input[type="text"] { width: 300px; padding: 10px; }
        button { padding: 10px 20px; }
        .job { background-color: #fff; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
        .job h2 { margin: 0; }
        .job p { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Job Search</h1>
    <form method="POST">
        <input type="text" name="query" placeholder="Enter job title" value="{{ query }}" required>
        <button type="submit">Search</button>
    </form>
    {% if jobs %}
        <h2>Results for "{{ query }}":</h2>
        {% for job in jobs %}
            <div class="job">
                <h2><a href="{{ job.url }}" target="_blank">{{ job.title }}</a></h2>
                <p><strong>Company:</strong> {{ job.company }}</p>
                <p><strong>Location:</strong> {{ job.location }}</p>
                <p>{{ job.description[:200] }}...</p>
            </div>
        {% endfor %}
    {% elif query %}
        <p>No jobs found for "{{ query }}". Please try a different keyword.</p>
    {% endif %}
</body>
</html>
'''
if __name__ == '__main__':
    app.run(debug=True)
