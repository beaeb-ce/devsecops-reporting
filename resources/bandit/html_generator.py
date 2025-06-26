import argparse
import json
import os
import base64
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textwrap import wrap

# Argument parsing
parser = argparse.ArgumentParser(description='Process the JSON file and HTML template.')
parser.add_argument('file_path', type=str, help='Path to the JSON file')
parser.add_argument('template_path', type=str, help='Path to the HTML template file')
args = parser.parse_args()
file_path = args.file_path
template_path = args.template_path

# Define the path for images
images_path = './bandit/images/'
os.makedirs(images_path, exist_ok=True)  # Create the directory if it doesn't exist

def get_image_as_data_url(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_image}"

# Functions
def parse_json(data):
    results = []
    for item in data['results']:
        item['cwe_id'] = item['issue_cwe']['id']
        results.append(item)
    df = pd.DataFrame(results)
    return df

def load_and_parse(file_path):
    with open(file_path) as f:
        data = json.load(f)
    df = parse_json(data)
    return df

def wrap_text(text, width=30):
    """Wrap text into multiple lines of the given width."""
    return '\n'.join(wrap(text, width))

def generate_severity_plot(df):
    severity_counts = df['issue_severity'].value_counts()
    severity_palette = {
        'LOW': "#FFEB3B",
        'MEDIUM': "#FF9800",
        'HIGH': "#F44336"
    }
    plt.figure(figsize=(20, 12))
    plt.rcParams.update({'font.size': 24})  # Increase the font size
    bars = plt.bar(severity_counts.index, severity_counts.values, color=[severity_palette[severity] for severity in severity_counts.index])
    plt.title('Number of Issues per Severity Level', fontsize=28)
    plt.xlabel('Severity Level', fontsize=24)
    plt.ylabel('Number of Issues', fontsize=24)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.savefig(os.path.join(images_path, 'severity_counts.png'), dpi=300)

def generate_file_plot(df):
    file_counts = df['filename'].value_counts().head(10)
    wrapped_labels = [wrap_text(f"{fname} ({count})", width=40) for fname, count in file_counts.items()]

    plt.figure(figsize=(20, 12))
    plt.rcParams.update({'font.size': 24})  # Increase the font size
    sns.barplot(y=wrapped_labels, x=file_counts.values, palette=sns.color_palette(['#66BB6A', '#1f77b4', '#66bba2', '#ff7f0e']), orient='h')
    plt.title('Number of Issues per File (Top 10)', fontsize=28)
    plt.xlabel('Number of Issues', fontsize=24)
    plt.ylabel('File', fontsize=24)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.tight_layout()
    plt.savefig(os.path.join(images_path, 'file_counts.png'), dpi=300)

def generate_confidence_plot(df):
    confidence_counts = df['issue_confidence'].value_counts()
    plt.figure(figsize=(20, 12))
    sns.barplot(x=confidence_counts.index, y=confidence_counts.values, palette=sns.color_palette(['#66BB6A', '#1f77b4', '#66bba2', '#ff7f0e']))
    plt.title('Number of Issues per Confidence Level')
    plt.xlabel('Confidence Level')
    plt.ylabel('Number of Issues')
    plt.tight_layout()
    plt.savefig(os.path.join(images_path, 'confidence_counts.png'), dpi=300)

def generate_issue_type_plot(df):
    issue_type_counts = df['test_name'].value_counts()
    plt.figure(figsize=(20, 12))
    sns.barplot(y=issue_type_counts.index[:10], x=issue_type_counts.values[:10], palette='viridis', orient='h')
    plt.title('Number of Issues per Type (Top 10)')
    plt.xlabel('Number of Issues')
    plt.ylabel('Issue Type')
    plt.tight_layout()
    plt.savefig(os.path.join(images_path, 'issue_type_counts.png'), dpi=300)

def generate_all_plots(file_path):
    df = load_and_parse(file_path)
    generate_severity_plot(df)
    generate_file_plot(df)
    generate_confidence_plot(df)
    generate_issue_type_plot(df)

# Main
df = load_and_parse(file_path)
generate_all_plots(file_path)

# Convert the images to data URLs
severity_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'severity_counts.png'))
file_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'file_counts.png'))
confidence_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'confidence_counts.png'))
issue_type_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'issue_type_counts.png'))

env = Environment(loader=FileSystemLoader('./'))
template = env.get_template(template_path)

print("Rendering template...")
html_content = template.render(
    data=df,
    severity_plot=severity_plot_data_url,
    file_plot=file_plot_data_url,
    confidence_plot=confidence_plot_data_url,
    issue_type_plot=issue_type_plot_data_url
)

print("Writing HTML content to file...")
with open('./bandit/bandit-report.html', 'w') as f:
    f.write(html_content)

print("Finished writing file.")