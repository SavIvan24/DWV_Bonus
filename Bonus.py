# Job Market Analysis Dashboard
import requests
import csv
import time
from collections import defaultdict
from plotly.offline import plot
import plotly.graph_objects as go

def scrape_hh_jobs():
    """Scrape job data from HH.ru API"""
    base_url = "https://api.hh.ru/vacancies"
    params = {
        "text": "DATA ANALYST",  # Change to desired job title
        "area": 1,               # 1 = Moscow
        "per_page": 100,
        "page": 0
    }
    
    skills = defaultdict(int)
    experience = defaultdict(int)
    education = defaultdict(int)
    
    print("Starting data collection from HH.ru...")
    
    with open('jobs.csv', 'w', newline='', encoding='utf-8-sig') as f:  # utf-8-sig for Excel compatibility
        writer = csv.writer(f)
        writer.writerow(['Title', 'Skills', 'Experience', 'Education'])
        
        for page in range(10):  # 10 pages × 100 = ~1000 vacancies
            params["page"] = page
            print(f"Processing page {page + 1}...")
            
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for item in data['items']:
                    try:
                        vacancy = requests.get(f'https://api.hh.ru/vacancies/{item["id"]}').json()
                        time.sleep(0.5)  # Respect API rate limits
                        
                        # Extract and clean data
                        vac_skills = [str(skill['name']) for skill in vacancy.get('key_skills', [])]
                        exp = str(vacancy.get('experience', {}).get('name', 'Not specified'))
                        educ = str(vacancy.get('education', {}).get('name', 'Not specified'))
                        
                        # Write to CSV with proper encoding
                        writer.writerow([
                            str(vacancy.get('name', '')),
                            ', '.join(vac_skills),
                            exp,
                            educ
                        ])
                        
                        # Update counters
                        for skill in vac_skills:
                            skills[skill] += 1
                        experience[exp] += 1
                        education[educ] += 1
                        
                    except Exception as e:
                        print(f"  Error processing vacancy {item.get('id')}: {str(e)}")
                        continue
                
                time.sleep(1)  # Additional delay between pages
                
            except Exception as e:
                print(f"Error fetching page {page}: {str(e)}")
                break
    
    print(f"Collected data on {sum(skills.values())} skill mentions")
    return skills, experience, education

def process_data(skills, experience, education):
    """Process raw data into visualization-ready formats"""
    print("Processing collected data...")
    
    # Clean and sort data
    top_skills = dict(sorted(
        {k: v for k, v in skills.items() if k.strip()}.items(),
        key=lambda x: x[1], 
        reverse=True
    )[:10])
    
    exp_data = dict(sorted(
        {k if k else 'Not specified': v for k, v in experience.items()}.items(),
        key=lambda x: x[1], 
        reverse=True
    ))
    
    educ_data = dict(sorted(
        {k if k else 'Not specified': v for k, v in education.items()}.items(),
        key=lambda x: x[1], 
        reverse=True
    ))
    
    return top_skills, exp_data, educ_data

def create_dashboard(top_skills, exp_data, educ_data):
    """Create interactive HTML dashboard"""
    print("Generating visualization dashboard...")
    
    # Common styling
    font_settings = dict(family="Arial", size=12, color='#333333')
    margin_settings = dict(l=50, r=50, b=100, t=50, pad=10)
    
    # Chart 1: Top Skills (Vertical Bar Chart)
    skills_fig = go.Figure(data=[go.Bar(
        x=list(top_skills.keys()),
        y=list(top_skills.values()),
        marker_color='#1f77b4',
        text=list(top_skills.values()),
        textposition='auto'
    )])
    skills_fig.update_layout(
        title='<b>Top 10 Required Skills</b>',
        xaxis_title='',
        yaxis_title='Frequency',
        margin=margin_settings,
        xaxis_tickangle=-45,
        font=font_settings,
        plot_bgcolor='rgba(0,0,0,0)',
        height=500
    )
    skills_plot = plot(skills_fig, output_type='div', include_plotlyjs=False)
    
    # Chart 2: Experience Distribution (Pie Chart)
    exp_fig = go.Figure(data=[go.Pie(
        labels=[str(k) for k in exp_data.keys()],
        values=list(exp_data.values()),
        hole=0.3,
        textinfo='percent+label',
        insidetextorientation='radial',
        marker=dict(colors=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    )])
    exp_fig.update_layout(
        title='<b>Experience Requirements</b>',
        font=font_settings,
        margin=margin_settings,
        height=500
    )
    exp_plot = plot(exp_fig, output_type='div', include_plotlyjs=False)
    
    # Chart 3: Education Requirements (Vertical Bar Chart)
    educ_fig = go.Figure(data=[go.Bar(
        x=[str(k) for k in educ_data.keys()],
        y=list(educ_data.values()),
        marker_color='#2ca02c',
        text=list(educ_data.values()),
        textposition='auto'
    )])

    educ_fig.update_layout(
        title='<b>Education Requirements</b>',
        xaxis_title='Education Level',
        yaxis_title='Frequency',
        margin=dict(l=50, r=50, b=150, t=50, pad=10),  # Adjusted for x-axis labels
        font=font_settings,
        height=500,
        xaxis_tickangle=-45  # Rotate labels for better readability
    )
    educ_plot = plot(educ_fig, output_type='div', include_plotlyjs=False)
    
    # HTML Template with proper encoding and responsive design
    html_template = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Market Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f9f9f9;
                color: #333;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin: 0;
            }}
            .container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 20px;
                max-width: 1400px;
                margin: 0 auto;
            }}
            .chart {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                font-size: 0.9em;
                color: #666;
            }}
            @media (max-width: 600px) {{
                .container {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Job Market Analysis Dashboard</h1>
            <p>Visualization of job requirements from HH.ru</p>
        </div>
        
        <div class="container">
            <div class="chart">{skills_plot}</div>
            <div class="chart">{exp_plot}</div>
            <div class="chart">{educ_plot}</div>
        </div>
        
        <div class="footer">
            <p>Generated on {date} | Data source: HH.ru API</p>
        </div>
    </body>
    </html>
    """.format(
        skills_plot=skills_plot,
        exp_plot=exp_plot,
        educ_plot=educ_plot,
        date=time.strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # Save HTML file with proper encoding
    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Dashboard successfully generated as dashboard.html")

if __name__ == "__main__":
    try:
        # Data Collection
        skills, exp, educ = scrape_hh_jobs()
        
        # Data Processing
        top_skills, exp_data, educ_data = process_data(skills, exp, educ)
        
        # Visualization
        create_dashboard(top_skills, exp_data, educ_data)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your internet connection and try again.")