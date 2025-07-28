import os
import json
import datetime
from src.outline_extractor import OutlineExtractor # Use the powerful extractor
from typing import List, Dict

def load_input_json(input_path: str) -> Dict:
    """Loads the input JSON file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_output_json(output_data: Dict, output_path: str):
    """Saves the final output data to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)

def filter_relevant_sections(all_sections: List[Dict], persona: str, job: str, max_sections: int = 5) -> List[Dict]:
    """
    Filters and ranks sections extracted by OutlineExtractor based on relevance.
    """
    # Keywords derived from the persona and job description
    keywords = ["trip", "college", "friends", "days", "plan", "travel", "itinerary", "activities", "group", "schedule", "guide", "tips", "things to do", "restaurants", "hotels"]
    
    # Add keywords from the job description itself
    keywords.extend(job.lower().split())
    keywords = list(set(keywords)) # Remove duplicates

    ranked_sections = []
    for section in all_sections:
        score = 0
        # Check for keywords in both the heading and the content
        heading_text = section.get('text', '').lower()
        content_text = section.get('content', '').lower()

        for kw in keywords:
            if kw in heading_text:
                score += 2 # Give more weight to matches in the heading
            if kw in content_text:
                score += 1

        # Boost score for bold headings (a good indicator of importance)
        if section.get('is_bold', False):
            score += 1
        
        # Add the section if it has a relevance score
        if score > 0:
            section['rank'] = score
            ranked_sections.append(section)

    # Sort by rank and return the top sections
    return sorted(ranked_sections, key=lambda x: -x["rank"])[:max_sections]

def analyze_subsections(sections: List[Dict]) -> List[Dict]:
    """
    Formats the filtered sections for the 'subsection_analysis' part of the output.
    """
    if not sections:
        return []
    
    # The 'content' field from OutlineExtractor already has the refined text.
    return [
        {
            "refined_text": sec.get("content", ""),
            "page_number": sec.get("page_num", 0),
            "document": sec.get("document", "unknown.pdf")
        }
        for sec in sections
    ]

def main():
    # Define paths
    collection_path = "collections"
    input_json_path = os.path.join(collection_path, "challenge1b_input.json")
    output_json_path = os.path.join(collection_path, "challenge1b_output.json")

    # Load input data
    input_data = load_input_json(input_json_path)
    
    # Correctly access keys based on the likely input file structure
    documents_data = input_data.get("documents", [])
    documents = [doc["filename"] for doc in documents_data if "filename" in doc]
    persona = input_data.get("persona", {}).get("role", "No Persona")
    job = input_data.get("job_to_be_done", {}).get("task", "No Job")

    # Instantiate the extractor
    extractor = OutlineExtractor()
    all_extracted_sections = []

    print("--- Starting PDF Processing with OutlineExtractor ---")
    for doc_filename in documents:
        # FIX: The line below now correctly uses 'collection_path'
        file_path = os.path.join(collection_path, doc_filename)
        if not os.path.exists(file_path):
            print(f"⚠️  Warning: File not found, skipping: {file_path}")
            continue

        print(f"Processing: {doc_filename}")
        # Use the OutlineExtractor to get titles and content-rich sections
        title, sections = extractor.extract_outline(file_path)
        
        # Tag each section with its source document filename
        for section in sections:
            section['document'] = doc_filename
        
        all_extracted_sections.extend(sections)
    print("--- Finished PDF Processing ---")

    # Filter and analyze the content-rich sections
    filtered_sections = filter_relevant_sections(all_extracted_sections, persona, job)
    subsection_analysis_data = analyze_subsections(filtered_sections)

    # Compose metadata for the output
    metadata = {
        "input_documents": documents,
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.datetime.now().isoformat()
    }

    # Final output structure
    output = {
        "metadata": metadata,
        "extracted_sections": [
            {
                "document": sec["document"],
                "section_title": sec["text"], # Use 'text' for the heading title
                "importance_rank": sec["rank"],
                "page_number": sec["page_num"]
            }
            for sec in filtered_sections
        ],
        "subsection_analysis": subsection_analysis_data
    }

    save_output_json(output, output_json_path)
    print(f"✅ Output successfully written to {output_json_path}")

if __name__ == "__main__":
    main()