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
    prompt = f"Search the following text for instances of XR usage in terms of hardware and software:\n\n{chunk}\n\nIf found, provide a brief description and the relevant excerpt."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0125",
            messages=[{"role": "system", "content": "Search for XR usage in the following text."},
                      {"role": "user", "content": chunk}],
            max_tokens=100,
            temperature=0.7,
        )
        result = response['choices'][0]['message']['content'].strip()
        return result if result else None
    except openai.error.OpenAIError as e:
        safe_print(f"OpenAI API Error: {e}")
        return None

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
        report = search_xr_usage(chunk)
        if report:
            reports_with_metadata.append({
                'author': author,
                'year': year,
                'report': report,
                'file_name': os.path.basename(document_path)
            })

    return reports_with_metadata

def main():
    document_folder = os.getenv("DOCUMENT_FOLDER_PATH")
    if not document_folder:
        safe_print("DOCUMENT_FOLDER_PATH environment variable is not set.")
        return
    safe_print(f"Processing documents in: {document_folder}")
    all_reports = []

    for filename in os.listdir(document_folder):
        sanitized_filename = sanitize_filename(filename)
        if sanitized_filename.endswith(".txt"):
            document_path = os.path.join(document_folder, sanitized_filename)
            safe_print(f"Processing file: {document_path}")
            try:
                reports_with_metadata = process_document(document_path)
                all_reports.extend(reports_with_metadata)
            except FileNotFoundError as e:
                safe_print(f"File not found: {e}")
                continue

    if not all_reports:
        safe_print("No XR usage reports generated.")
        return

    df = pd.DataFrame(all_reports)
    output_path = os.path.join(document_folder, "xr_usage_reports.csv")
    df.to_csv(output_path, index=False)
    safe_print(f"XR usage reports saved to {output_path}")

if __name__ == "__main__":
    main()