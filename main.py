import json
import argparse
import os
from src.outline_extractor import OutlineExtractor # Adjust import if needed

def main():
    """
    Main function to extract, process, and format the PDF outline
    """
    parser = argparse.ArgumentParser(description="Extract a structured outline from a PDF file.")
    parser.add_argument("pdf_path", help="The path to the PDF file.")
    args = parser.parse_args()

    extractor = OutlineExtractor()
    raw_outline = extractor.extract_outline(args.pdf_path)
    title_item = max(
        [item for item in raw_outline if item['page_num'] == 0],
        key=lambda x: x['font_size']
    )
    document_title = title_item['text']

    headings = [
        item for item in raw_outline
        if item != title_item and item["text"].strip()
    ]
    formatted_outline = []
    for item in headings:
        formatted_outline.append({
            "level": f"H{item['level']}",
            "text": item["text"],
            "page": item["page_num"] + 1  
        })
    final_output = {
        "title": document_title,
        "outline": formatted_outline
    }
    # 6. Define output filename and save the result to a JSON file
    base_name = os.path.splitext(args.pdf_path)[0]
    output_filename = f"{base_name}_outline.json"

    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)

    print(f"✅ Outline successfully saved to: {output_filename}")


if __name__ == "__main__":
    main()