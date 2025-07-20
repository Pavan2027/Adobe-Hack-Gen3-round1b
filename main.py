import argparse
import json
from src.outline_extractor import OutlineExtractor

def main():
    parser = argparse.ArgumentParser(description="Extract outline from a PDF file.")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    args = parser.parse_args()

    extractor = OutlineExtractor()
    raw_outline = extractor.extract_outline(args.pdf_path)
    outline = [item for item in raw_outline if item["text"].strip()]
    output_path = args.pdf_path.replace(".pdf", "_outline.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(outline, f, indent=4, ensure_ascii=False)

    print(f"Outline extracted and saved to {output_path}")

if __name__ == "__main__":
    main()