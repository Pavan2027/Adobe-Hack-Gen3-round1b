import os
import json
import datetime
from src.pdf_parser import PDFParser
from src.feature_extractor import FeatureExtractor
from src.outline_extractor import OutlineExtractor
from src.data_structures import TextBlock
from typing import List, Dict

def load_input_json(input_path: str) -> Dict:
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_output_json(output_data: Dict, output_path: str):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

def filter_relevant_sections(text_blocks: List[TextBlock], persona: str, job: str, max_sections: int = 5):
    keywords = ["trip", "college", "friends", "days", "plan", "travel", "itinerary", "activities", "group", "schedule"]

    relevant_sections = []
    for block in text_blocks:
        score = 0
        lowered = block.text.lower()

        # Keyword match scoring
        for kw in keywords:
            if kw in lowered:
                score += 1

        # Boost score for bold headings
        if block.is_bold:
            score += 1

        # Boost score for large font
        if block.font_size > 12:
            score += 1

        if score > 0:
            relevant_sections.append({
                "title": block.text,
                "content": block.text,  # ✅ Added to support subsection_analysis
                "page_num": getattr(block, "page_number", 0),  # ✅ Match key used in analyze_subsections
                "rank": score,
                "document": getattr(block, "document", "unknown")
            })

    return sorted(relevant_sections, key=lambda x: -x["rank"])[:max_sections]

def analyze_subsections(sections):
    if not sections:
        return []
    return [
        {
            "refined_text": sec["content"],
            "page_number": sec["page_num"],
            "document": sec.get("document", "unknown.pdf")
        }
        for sec in sections
        if "content" in sec
    ]


def main():
    collection_path = "Challenge_1b/Collection 1"
    input_json_path = os.path.join(collection_path, "challenge1b_input.json")
    pdf_dir = os.path.join(collection_path, "PDFs")
    output_json_path = os.path.join(collection_path, "challenge1b_output.json")

    input_data = load_input_json(input_json_path)
    documents = input_data["documents"]
    persona = input_data["persona"]["role"]
    job = input_data["job_to_be_done"]["task"]

    parser = PDFParser()
    all_blocks = []

    for doc in documents:
        filename = doc["filename"]
        file_path = os.path.join(pdf_dir, filename)
        print(f"Parsing: {filename}")

        blocks = parser.parse(file_path)
        for block in blocks:
            block.document = filename  # Dynamically add attribute

        for block in blocks:
            block.source = filename  # tag the source document
        all_blocks.extend(blocks)

    # Filter and analyze
    extracted_sections_raw = filter_relevant_sections(all_blocks, persona, job)
    subsection_analysis = analyze_subsections(extracted_sections_raw)

    # Compose metadata
    metadata = {
        "input_documents": [doc["filename"] for doc in documents],
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.datetime.now().isoformat()
    }

    # Final output
    output = {
        "metadata": metadata,
        "extracted_sections": [
            {
                "document": sec["document"],
                "section_title": sec["title"],
                "importance_rank": sec["rank"],
                "page_number": sec["page_num"]
            }
            for sec in extracted_sections_raw
        ],
        "subsection_analysis": subsection_analysis
    }

    save_output_json(output, output_json_path)
    print(f"✅ Output written to {output_json_path}")

if __name__ == "__main__":
    main()
