import argparse
import json
import os
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

# Argument parsing
parser = argparse.ArgumentParser(description='Generate Detect-Secrets HTML report.')
parser.add_argument('file_path', type=str, help='Path to detect-secrets JSON file')
parser.add_argument('template_path', type=str, help='Path to HTML template')
args = parser.parse_args()
file_path = args.file_path
template_path = args.template_path

# Image output directory
images_path = './detect_secrets/images/'
os.makedirs(images_path, exist_ok=True)

def get_image_as_data_url(image_path):
    with open(image_path, 'rb') as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

def load_and_parse_detect_secrets(path):
    with open(path, 'r') as f:
        data = json.load(f)

    all_rows = []
    for file_path, findings in data.get("results", {}).items():
        for entry in findings:
            all_rows.append({
                "file": file_path,
                "type": entry.get("type"),
                "line_number": entry.get("line_number"),
                "is_verified": entry.get("is_verified"),
                "hashed_secret": entry.get("hashed_secret")
            })

    df = pd.DataFrame(all_rows)
    print(f"✅ Loaded {len(df)} secrets from {len(data.get('results', {}))} files")
    return df

def generate_secrets_distribution_plot(df, top_n=5):
    file_counts = df['file'].value_counts()
    if len(file_counts) > top_n:
        top_files = file_counts[:top_n]
        others = file_counts[top_n:].sum()
        file_counts = pd.concat([top_files, pd.Series([others], index=['Others'])])

    colors = sns.color_palette("pastel", len(file_counts))
    fig = plt.figure(figsize=(14, 10)) 

    wedges, texts, autotexts = plt.pie(
        file_counts.values,
        labels=file_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        pctdistance=0.75,            
        labeldistance=1.1,           
        textprops=dict(color="black")
    )

    for text, autotext in zip(texts, autotexts):
        text.set(size=14)
        autotext.set(size=14)
        autotext.set_color('black')

    fig.suptitle('Distribution of Secrets Detected Across Files', fontsize=22, y=0.95)
    plt.tight_layout()

    image_path = os.path.join(images_path, 'file_counts_detect_secrets_pie.png')
    plt.savefig(image_path, dpi=300, bbox_inches='tight') 
    return image_path

# Main flow
df = load_and_parse_detect_secrets(file_path)
plot_path = generate_secrets_distribution_plot(df)
plot_data_url = get_image_as_data_url(plot_path)

env = Environment(loader=FileSystemLoader('./'))
template = env.get_template(template_path)

html_content = template.render(
    data=df.to_dict(orient='records'),
    file_plot=plot_data_url
)

output_path = './detect_secrets/detect-secrets-report.html'
with open(output_path, 'w') as f:
    f.write(html_content)

print(f"✅ Report generated: {output_path}")
