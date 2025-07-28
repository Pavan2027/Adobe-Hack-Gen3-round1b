import fitz
import re
from collections import Counter
import statistics

class OutlineExtractor:
    """
    Extracts a structured outline using a robust, multi-pass heuristic engine
    designed for high precision and accurate multi-line heading detection.
    """

    def _get_line_properties(self, spans: list, page_num: int, page_height: float):
        """Consolidates properties for a line from its constituent spans."""
        text = " ".join(s['text'] for s in spans).strip()
        if not text:
            return None

        bbox = fitz.Rect(spans[0]['bbox'])
        for s in spans[1:]:
            bbox.include_rect(s['bbox'])
        
        font_sizes = [s['size'] for s in spans]
        font_names = [s['font'] for s in spans]
        
        # Determine font properties using the mode (most common value)
        modal_font_name = statistics.mode(font_names) if font_names else ""
        
        return {
            "text": text,
            "bbox": tuple(bbox),
            "page_num": page_num,
            "font_size": statistics.mode(font_sizes) if font_sizes else 0,
            "font_name": modal_font_name,
            "is_bold": "bold" in modal_font_name.lower() or "black" in modal_font_name.lower(),
            "is_header_footer": bbox.y0 < page_height * 0.1 or bbox.y1 > page_height * 0.92
        }

    def _get_all_lines(self, doc: fitz.Document):
        """Extracts and groups all text into consolidated lines for the entire document."""
        all_lines = []
        for page_num, page in enumerate(doc):
            # Extract all spans with text from the page
            spans = []
            for block in page.get_text("dict").get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if span.get("text", "").strip():
                                spans.append(span)
            
            if not spans:
                continue

            # Sort spans primarily by vertical position, then horizontal
            spans.sort(key=lambda s: (s['bbox'][1], s['bbox'][0]))

            # Group spans into lines based on vertical alignment
            grouped_lines_spans = []
            if spans:
                current_line = [spans[0]]
                for i in range(1, len(spans)):
                    prev_span, current_span = current_line[-1], spans[i]
                    # Check if vertical centers are closely aligned
                    if abs(((prev_span['bbox'][1] + prev_span['bbox'][3]) / 2) - 
                           ((current_span['bbox'][1] + current_span['bbox'][3]) / 2)) < 2:
                        current_line.append(current_span)
                    else:
                        grouped_lines_spans.append(sorted(current_line, key=lambda s: s['bbox'][0]))
                        current_line = [current_span]
                grouped_lines_spans.append(sorted(current_line, key=lambda s: s['bbox'][0]))

            page_height = page.rect.height
            for line_spans in grouped_lines_spans:
                line_props = self._get_line_properties(line_spans, page_num, page_height)
                if line_props:
                    all_lines.append(line_props)
        return all_lines

    def extract_outline(self, pdf_path: str):
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            print(f"Error opening or processing PDF file: {e}")
            return None, None

        if doc.page_count > 50:
            print(f"ERROR: Document has {doc.page_count} pages, which exceeds the 50-page limit. Aborting.")
            doc.close()
            return None, None

        all_lines = self._get_all_lines(doc)
        if not all_lines:
            doc.close()
            return "Untitled Document", []

        # Find Title
        first_page_lines = [line for line in all_lines if line['page_num'] == 0 and not line['is_header_footer']]
        title_text = "Untitled Document"
        title_lines = []
        if first_page_lines:
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
        while i < len(headings):
            current_heading = headings[i].copy()
            j = i + 1
            while j < len(headings):
                next_heading = headings[j]
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

        if not merged_headings:
            doc.close()
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

        # Add content under each heading
        sections = []
        num_headings = len(merged_headings)
        heading_texts_set = {h['text'] for h in merged_headings}

        for i in range(num_headings):
            heading = merged_headings[i]
            start_page = heading["page_num"]
            start_y = heading["bbox"][3]

            if i + 1 < num_headings:
                next_heading = merged_headings[i + 1]
                end_page = next_heading["page_num"]
                end_y = next_heading["bbox"][1]
            else:
                end_page = doc.page_count - 1
                end_y = float("inf")

            section_lines = []
            for line in all_lines:
                is_within_bounds = (
                    not line['is_header_footer'] and (
                        (line["page_num"] > start_page and line["page_num"] < end_page) or
                        (line["page_num"] == start_page and line["bbox"][1] > start_y) or
                        (line["page_num"] == end_page and line["bbox"][3] < end_y)
                    )
                )
                if is_within_bounds and line['text'] not in heading_texts_set:
                    section_lines.append(line)

            section_text = " ".join(
                line["text"].strip() for line in sorted(section_lines, key=lambda l: (l["page_num"], l["bbox"][1]))
                if line.get("text", "").strip()
            )
            
            heading["content"] = section_text.strip()
            sections.append(heading)

        # Final cleanup and return
        doc.close()
        return title_text, [h for h in sections if h.get('level', 99) <= 5 and h.get('content')]
