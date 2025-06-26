import argparse
import json
import os
import base64
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

# Argument parsing
parser = argparse.ArgumentParser(description='Process the JSON file and HTML template for Trufflehog.')
parser.add_argument('file_path', type=str, help='Path to the JSON file')
parser.add_argument('template_path', type=str, help='Path to the HTML template file')
args = parser.parse_args()
file_path = args.file_path
template_path = args.template_path

# Define the path for images
images_path = './trufflehog/images/'
os.makedirs(images_path, exist_ok=True)  # Create the directory if it doesn't exist

def get_image_as_data_url(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_image}"

def load_and_parse_trufflehog(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    return df

def generate_file_plot_trufflehog_pie(df, top_n=5): 
    file_counts = df['path'].value_counts()
    if len(file_counts) > top_n:
        top_files = file_counts[:top_n]
        others_count = file_counts[top_n:].sum()
        file_counts = pd.concat([top_files, pd.Series([others_count], index=['Others'])])
    colors = sns.color_palette("pastel", len(file_counts))
    fig = plt.figure(figsize=(20, 15))
    wedges, texts, autotexts = plt.pie(file_counts.values, labels=file_counts.index, autopct='%1.1f%%', startangle=140, colors=colors, pctdistance=0.85, textprops=dict(color="black"))
    for text, autotext in zip(texts, autotexts):
        text.set(size=24)  # Adjusted size to 24
        autotext.set(size=24)  # Adjusted size to 24
        autotext.set_color('black')
    
    # Using suptitle to center the title based on the figure width
    fig.suptitle('Distribution of Secrets Detected Across Files', fontsize=28, y=0.92)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_path, 'file_counts_trufflehog_pie_professional.png'), dpi=300)

# Main logic
df = load_and_parse_trufflehog(file_path)
generate_file_plot_trufflehog_pie(df)

# Convert the image to data URL
file_plot_data_url = get_image_as_data_url(os.path.join(images_path, 'file_counts_trufflehog_pie_professional.png'))

env = Environment(loader=FileSystemLoader('./'))
template = env.get_template(template_path)

print("Rendering template...")
html_content = template.render(
    data=df,
    file_plot=file_plot_data_url
)

print("Writing HTML content to file...")
with open('./trufflehog/trufflehog-report.html', 'w') as f:
    f.write(html_content)

print("Finished writing file.")