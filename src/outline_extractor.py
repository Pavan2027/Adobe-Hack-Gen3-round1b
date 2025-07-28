# FILE: src/outline_extractor.py (FINAL, PRECISION-FOCUSED VERSION)

import fitz
import re
from collections import Counter
import statistics

class OutlineExtractor:
    """
    Extracts a structured outline using a robust, multi-pass heuristic engine
    designed for high precision and accurate multi-line heading detection.
    """

    def extract_outline(self, pdf_path: str):
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening or processing PDF file: {e}")
            return None, None

        if doc.page_count > 50:
            print(f"ERROR: Document has {doc.page_count} pages, which exceeds the 50-page limit. Aborting.")
            return None, None

        all_lines = self._get_all_lines(doc)
        if not all_lines:
            return "Untitled Document", []

        # Find Title
        first_page_lines = [line for line in all_lines if line['page_num'] == 0 and not line['is_header_footer']]
        title_text = "Untitled Document"
        title_lines = []
        if first_page_lines:
            # Avoid error on pages with no text
            font_sizes_on_page = [line['font_size'] for line in first_page_lines if line.get('font_size')]
            if font_sizes_on_page:
                max_font_size = max(font_sizes_on_page)
                title_lines = [line for line in first_page_lines if line['font_size'] >= max_font_size * 0.9]
                title_text = " ".join(line['text'] for line in sorted(title_lines, key=lambda l: l['bbox'][1]))

        # Calculate median font size for body text
        font_sizes = [line['font_size'] for line in all_lines if not line['is_header_footer'] and line not in title_lines]
        median_font_size = statistics.median(font_sizes) if font_sizes else 12

        # Identify heading candidates
        headings = []
        numbering_pattern = re.compile(r'^\s*(\d+(\.\d+)*|[A-Z]\.|\([a-z]\)|[IVXLCDM]+\.)\s*')
        for i, line in enumerate(all_lines):
            if line in title_lines or line['is_header_footer']:
                continue

            size_ratio = line['font_size'] / median_font_size if median_font_size > 0 else 1
            is_numbered = numbering_pattern.match(line['text'])

            if line['is_bold'] or is_numbered or size_ratio > 1.2:
                headings.append(line)

        # Merge multi-line headings
        merged_headings = []
        i = 0
        # FIX 1: The merging logic now correctly populates the list before it's used.
        while i < len(headings):
            current_heading = headings[i].copy()
            j = i + 1
            while j < len(headings):
                next_heading = headings[j]
                # Check for proximity and similar style to merge lines into a single heading
                if (abs(next_heading['font_size'] - current_heading['font_size']) < 1 and
                        next_heading['is_bold'] == current_heading['is_bold'] and
                        (next_heading['bbox'][1] - current_heading['bbox'][3]) < current_heading['font_size'] * 0.5):
                    current_heading['text'] += " " + next_heading['text']
                    current_heading['bbox'] = tuple(fitz.Rect(current_heading['bbox']).include_rect(next_heading['bbox']))
                    j += 1
                else:
                    break
            merged_headings.append(current_heading)
            i = j
        
        print(f"[DEBUG] Total merged headings found: {len(merged_headings)}")
        for h in merged_headings[:5]: # Print first 5 for brevity
            print(f"  - Sample Heading: '{h['text'][:60]}' on page {h['page_num']}")

        if not merged_headings:
            return title_text, []

        # Cluster headings by style to assign levels
        styles = {}
        for h in merged_headings:
            style_key = (round(h["font_size"]), h["is_bold"])
            if style_key not in styles:
                styles[style_key] = []
            styles[style_key].append(h)

        sorted_styles = sorted(styles.keys(), key=lambda x: (x[0], x[1]), reverse=True)
        level_map = {style: i + 1 for i, style in enumerate(sorted_styles)}

        for h in merged_headings:
            style_key = (round(h["font_size"]), h["is_bold"])
            h['level'] = level_map.get(style_key, 99)

        # 🔽 Add content under each heading
        sections = []
        num_headings = len(merged_headings)
        
        # Create a set of heading texts for faster lookup
        heading_texts_set = {h['text'] for h in merged_headings}

        for i in range(num_headings):
            heading = merged_headings[i]
            start_page = heading["page_num"]
            start_y = heading["bbox"][3]  # Bottom of the current heading's box

            # Determine the end boundary (the start of the next heading)
            if i + 1 < num_headings:
                next_heading = merged_headings[i + 1]
                end_page = next_heading["page_num"]
                end_y = next_heading["bbox"][1] # Top of the next heading's box
            else:
                end_page = doc.page_count -1 # Use the actual last page
                end_y = float("inf") # Go to the end of the document

            section_lines = []
            for line in all_lines:
                # Basic conditions: not a header/footer, and within the page/y-position boundaries
                is_within_bounds = (
                    not line['is_header_footer'] and (
                        (line["page_num"] > start_page and line["page_num"] < end_page) or
                        (line["page_num"] == start_page and line["bbox"][1] > start_y) or
                        (line["page_num"] == end_page and line["bbox"][3] < end_y)
                    )
                )
                
                # FIX 2: Ensure the line is not another heading.
                if is_within_bounds and line['text'] not in heading_texts_set:
                    section_lines.append(line)

            section_text = " ".join(
                line["text"].strip() for line in sorted(section_lines, key=lambda l: (l["page_num"], l["bbox"][1]))
                if line.get("text", "").strip()
            )
            
            heading["content"] = section_text.strip()
            sections.append(heading)
            
        print(f"[INFO] Content extraction complete. Processed {len(sections)} sections.")
        
        # Final cleanup and return
        doc.close()
        return title_text, [h for h in sections if h.get('level', 99) <= 5 and h.get('content')]
