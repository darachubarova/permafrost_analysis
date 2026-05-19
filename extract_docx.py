import os
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_docx(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            paragraphs = tree.findall('.//w:p', namespace)
            text_runs = []
            for p in paragraphs:
                texts = p.findall('.//w:t', namespace)
                paragraph_text = "".join([t.text for t in texts if t.text])
                if paragraph_text:
                    text_runs.append(paragraph_text)
            return "\n".join(text_runs)
    except Exception as e:
        return f"Error extracting {docx_path}: {e}"

base_dir = r"NOPik"
output_file = r"NOPik_all_texts_extracted.txt"
docx_files = [f for f in os.listdir(base_dir) if f.endswith(".docx")]

with open(output_file, "w", encoding="utf-8") as f_out:
    for filename in docx_files:
        full_path = os.path.join(base_dir, filename)
        text = extract_text_from_docx(full_path)
        f_out.write(f"=== FILE: {filename} ===\n")
        f_out.write(text)
        f_out.write("\n\n")
        print(f"{filename}: {len(text)} characters")

print(f"\nTotal files processed: {len(docx_files)}")
print(f"Output saved to: {output_file}")
