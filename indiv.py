import os
import openai
import pandas as pd
from dotenv import load_dotenv
import string

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = ''.join(c for c in filename if c in valid_chars)
    return cleaned_filename

def safe_print(content):
    print(content.encode('utf-8', 'ignore').decode('utf-8', 'ignore'))

# Load environment variables
load_dotenv()
print("Loaded environment variables.")

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")

def split_into_chunks(document, chunk_size):
    words = document.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def search_xr_usage(chunk):
    current_year = 2023
    prompt = f"Search the following text for references of virtual reality, augmented reality, and mixed reality headsets and associated software names:\n\n{chunk}\n\nProvide a list of device names and a list of software names separately, along with the relevant excerpts, focusing only on the hardware and software used in studies from {current_year} or later. Exclude any references to studies published before {current_year}."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": f"You are an AI assistant that specializes in identifying and listing virtual reality, augmented reality, and mixed reality headsets and associated software names mentioned in a given text, focusing only on studies from {current_year} or later."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        
        result = response.choices[0].message.content.strip()
        
        device_names = []
        software_names = []
        lines = result.split('\n')
        for line in lines:
            if line.startswith('1.') or line.startswith('2.'):
                if 'hardware' in line.lower() or 'device' in line.lower():
                    device_names.append(line[2:].strip())
                elif 'software' in line.lower():
                    software_names.append(line[2:].strip())
        
        return result, ', '.join(device_names), ', '.join(software_names)
    
    except openai.error.OpenAIError as e:
        safe_print(f"OpenAI API Error: {e}")
        return None, None, None

def extract_author_year(filename):
    # Assuming the filename format is "AuthorName_Year_Title.txt"
    parts = filename.split('_')
    if len(parts) >= 3:
        author = parts[0]
        year = parts[1]
        return author, year
    else:
        return "Unknown", "Unknown"

def process_document(document_path):
    with open(document_path, 'r', encoding='utf-8') as file:
        document_content = file.read()
    chunks = split_into_chunks(document_content, chunk_size=500)
    author, year = extract_author_year(os.path.basename(document_path))
    reports_with_metadata = []
    for chunk in chunks:
        report, device_names, software_names = search_xr_usage(chunk)
        if report:
            reports_with_metadata.append({
                'author': author,
                'year': year,
                'report': report,
                'device_names': device_names,
                'software_names': software_names,
                'file_name': os.path.basename(document_path)
            })
    return reports_with_metadata

def main():
    document_folder = os.getenv("DOCUMENT_FOLDER_PATH")
    if not document_folder:
        safe_print("DOCUMENT_FOLDER_PATH environment variable is not set.")
        return

    safe_print(f"Processing documents in: {document_folder}")

    for filename in os.listdir(document_folder):
        sanitized_filename = sanitize_filename(filename)
        if sanitized_filename.endswith(".txt"):
            document_path = os.path.join(document_folder, sanitized_filename)
            safe_print(f"Processing file: {document_path}")
            try:
                reports_with_metadata = process_document(document_path)
                if reports_with_metadata:
                    df = pd.DataFrame(reports_with_metadata)
                    output_filename = f"{os.path.splitext(sanitized_filename)[0]}_report_version.csv"
                    output_path = os.path.join(document_folder, output_filename)
                    df.to_csv(output_path, index=False)
                    safe_print(f"XR usage report saved to {output_path}")
                else:
                    safe_print(f"No XR usage found in {document_path}")
            except FileNotFoundError as e:
                safe_print(f"File not found: {e}")
                continue

if __name__ == "__main__":
    main()