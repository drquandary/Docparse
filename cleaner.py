import os
import string
from pathlib import Path

def sanitize_filename(filename):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = ''.join(c for c in filename if c in valid_chars)
    return cleaned_filename

def clean_filenames(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            sanitized_filename = sanitize_filename(filename)
            if sanitized_filename != filename:
                original_path = Path(root) / filename
                new_path = Path(root) / sanitized_filename
                os.rename(original_path, new_path)

# Set the document folder path directly
document_folder = r"C:\Users\jeffr\Documents\VR2023\Exported Items\files\txt\2"

# Call the clean_filenames function with the new path
clean_filenames(document_folder)