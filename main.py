# FILE: main.py (FINAL, PRECISION-FOCUSED VERSION)

import json
import argparse
import os
from src.outline_extractor import OutlineExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract a structured outline from a PDF file.")
    parser.add_argument("pdf_path", help="The path to the PDF file.")
    args = parser.parse_args()

    extractor = OutlineExtractor()
    # The extractor now returns a tuple: (document_title, list_of_headings)
    # or (None, None) if there's an error.
    title, headings = extractor.extract_outline(args.pdf_path)

    # If the extractor returned None, it means an error occurred (e.g., page limit).
    if title is None and headings is None:
        return # Stop execution, error was already printed.

    # The outline is already a flat list of dictionaries from the extractor.
    # We just need to format it for the final JSON.
    formatted_outline = []
    for heading in headings:
        formatted_outline.append({
            "level": f"H{heading['level']}",
            "text": heading["text"],
            "page": heading["page_num"] + 1
        })

    final_output = {
        "title": title,
        "outline": formatted_outline
    }

    # Save the output
    output_dir = os.path.dirname(args.pdf_path)
    base_name = os.path.splitext(os.path.basename(args.pdf_path))[0]
    if not output_dir: output_dir = '.'
    output_filename = os.path.join(output_dir, f"{base_name}_outline.json")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=4, ensure_ascii=False)

    print(f"✅ Outline successfully saved to: {output_filename}")

if __name__ == "__main__":
    main()