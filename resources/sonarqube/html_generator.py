import argparse
import json
import os
import base64
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textwrap import wrap

# Argument parsing for SonarQube report generation
parser = argparse.ArgumentParser(description='Process the JSON files for SonarQube and HTML template.')
parser.add_argument('issues_file_path', type=str, help='Path to the SonarQube issues JSON file')
parser.add_argument('hotspots_file_path', type=str, help='Path to the SonarQube hotspots JSON file')
parser.add_argument('template_path', type=str, help='Path to the HTML template file')
args = parser.parse_args()
issues_file_path = args.issues_file_path
hotspots_file_path = args.hotspots_file_path
template_path = args.template_path

# Define the path for images
images_path = 'sonarqube/images/'
os.makedirs(images_path, exist_ok=True)

def get_image_as_data_url(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_image}"

def load_json(file_path, key):
    with open(file_path) as f:
        data = json.load(f)
    return pd.json_normalize(data[key])

def generate_no_data_image(image_path, title):
    plt.figure(figsize=(20, 12))
    plt.text(0.5, 0.6, title, horizontalalignment='center', verticalalignment='center', fontsize=28, color='black')
    plt.text(0.5, 0.4, 'No Data Found', horizontalalignment='center', verticalalignment='center', fontsize=28, color='red')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(image_path)

def wrap_text(text, width=55):
    """Wrap text into multiple lines of the given width."""
    return '\n'.join(wrap(text, width=width))

def generate_severity_plot(df):
    if 'severity' not in df.columns:
        generate_no_data_image(os.path.join(images_path, 'severity_counts.png'), 'Number of Issues per Severity Level')
        return

    severity_counts = df['severity'].value_counts()
    colors = {
        'CRITICAL': '#f72d2a',  # red
        'MAJOR': '#ff7f0e',    # orange
        'MINOR': '#e3de44'     # Muted yellow
    }
    bar_colors = [colors.get(severity, '#808080') for severity in severity_counts.index]  # default to grey if severity not found
    
    plt.figure(figsize=(20, 12))
    bars = plt.bar(severity_counts.index, severity_counts.values, color=bar_colors)
    plt.title('Number of Issues per Severity Level', fontsize=28)
    plt.xlabel('Severity Level', fontsize=22)
    plt.ylabel('Number of Issues', fontsize=22)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig(os.path.join(images_path, 'severity_counts.png'))

def generate_file_plot(df):
    file_counts = df['component'].value_counts().head(10)
    wrapped_labels = [wrap_text(label) for label in file_counts.index]

    plt.figure(figsize=(20, 12))
    bars = plt.barh(wrapped_labels, file_counts.values, color=sns.color_palette(['#66BB6A', '#1f77b4', '#66bba2', '#ff7f0e'], 10))
    plt.title('Top 10 Components with Most Issues', fontsize=28)
    plt.xlabel('Number of Issues', fontsize=22)
    plt.ylabel('Components', fontsize=22)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig(os.path.join(images_path, 'file_counts.png'))

def generate_issue_type_plot(df):
    issue_type_counts = df['type'].value_counts()
    plt.figure(figsize=(20, 12))
    issue_type_counts.plot.pie(autopct="%.1f%%", colors=sns.color_palette(['#66BB6A', '#1f77b4', '#66bba2'], len(issue_type_counts)), startangle=90, fontsize=22, textprops={'fontsize': 20})
    plt.title('Distribution of Issue Types', fontsize=28)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig(os.path.join(images_path, 'issue_type_counts.png'))

def generate_category_plot(df):
    category_counts = df['securityCategory'].value_counts()
    plt.figure(figsize=(20, 12))
    category_counts.plot.pie(autopct="%.1f%%", colors=sns.color_palette(['#66BB6A', '#1f77b4', '#ff7f0e', '#66bba2'], len(category_counts)), startangle=90, fontsize=22, textprops={'fontsize': 20})
    plt.title('Number of Hotspots per Security Category', fontsize=28)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig(os.path.join(images_path, 'category_counts.png'))

def generate_vulnerability_prob_plot(df):
    vulnerability_prob_counts = df['vulnerabilityProbability'].value_counts()
    plt.figure(figsize=(20, 12))
    bars = plt.bar(vulnerability_prob_counts.index, vulnerability_prob_counts.values, color=sns.color_palette(['#ff7f0e', '#f72d2a', '#d1ca6f'], len(vulnerability_prob_counts)))
    plt.title('Distribution of Hotspots by Vulnerability Probability', fontsize=28)
    plt.xlabel('Vulnerability Probability', fontsize=22)
    plt.ylabel('Number of Hotspots', fontsize=22)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig(os.path.join(images_path, 'vulnerability_prob_counts.png'))

def generate_hotspot_file_plot(df):
    hotspot_file_counts = df['component'].value_counts().head(10)
    wrapped_labels = [wrap_text(label) for label in hotspot_file_counts.index]

    plt.figure(figsize=(20, 12))
    bars = plt.barh(wrapped_labels, hotspot_file_counts.values, color=sns.color_palette(['#66BB6A', '#1f77b4', '#66bba2'], 10))
    plt.title('Top 10 Components with Most Hotspots', fontsize=28)
    plt.xlabel('Number of Hotspots', fontsize=22)
    plt.ylabel('Components', fontsize=22)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)
    plt.savefig(os.path.join(images_path, 'hotspot_file_counts.png'))

def segment_data_by_column(df, column_name):
    """Segment data by unique values in a column."""
    levels = df[column_name].unique()
    return {level: df[df[column_name] == level] for level in levels}

# Main
df_issues = load_json(issues_file_path, 'issues')
df_hotspots = load_json(hotspots_file_path, 'hotspots')

# Segment the data
issues_segmented = segment_data_by_column(df_issues, 'severity') if 'severity' in df_issues.columns else {}
hotspots_segmented = segment_data_by_column(df_hotspots, 'vulnerabilityProbability')

# Check if there are issues and generate corresponding plots
if not df_issues.empty:
    generate_severity_plot(df_issues)
    generate_file_plot(df_issues)
    generate_issue_type_plot(df_issues)
else:
    generate_no_data_image(os.path.join(images_path, 'severity_counts.png'), 'Number of Issues per Severity Level')
    generate_no_data_image(os.path.join(images_path, 'file_counts.png'), 'Top 10 Components with Most Issues')
    generate_no_data_image(os.path.join(images_path, 'issue_type_counts.png'), 'Distribution of Issue Types')

# Check if there are hotspots and generate corresponding plots
if not df_hotspots.empty:
    generate_category_plot(df_hotspots)
    generate_vulnerability_prob_plot(df_hotspots)
    generate_hotspot_file_plot(df_hotspots)
else:
    generate_no_data_image(os.path.join(images_path, 'category_counts.png'), 'Number of Hotspots per Security Category')
    generate_no_data_image(os.path.join(images_path, 'vulnerability_prob_counts.png'), 'Distribution of Hotspots by Vulnerability Probability')
    generate_no_data_image(os.path.join(images_path, 'hotspot_file_counts.png'), 'Top 10 Components with Most Hotspots')

# Convert the images to data URLs
severity_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'severity_counts.png'))
file_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'file_counts.png'))
issue_type_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'issue_type_counts.png'))
category_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'category_counts.png'))
vulnerability_prob_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'vulnerability_prob_counts.png'))
hotspot_file_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'hotspot_file_counts.png'))

# Render the HTML template
env = Environment(loader=FileSystemLoader('./'))
template = env.get_template(template_path)
html_content = template.render(
    issues_data_segmented=issues_segmented,
    hotspots_data_segmented=hotspots_segmented,
    severity_plot=severity_plot_data_url,
    file_plot=file_plot_data_url,
    issue_type_plot=issue_type_plot_data_url,
    category_plot=category_plot_data_url,
    vulnerability_prob_plot=vulnerability_prob_plot_data_url,
    hotspot_file_plot=hotspot_file_plot_data_url
)

# Save the rendered content to an HTML file
with open('sonarqube/sonarqube-report.html', 'w') as f:
    f.write(html_content)

print("Finished writing file.")
