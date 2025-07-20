import fitz  # PyMuPDF
from .data_structures import TextBlock
from typing import List

class PDFParser:
    """Parses a PDF file and extracts text blocks."""

    def parse(self, pdf_path: str) -> List[TextBlock]:
        """
        Extracts text blocks from each page of a PDF.

        Args:
            pdf_path: The path to the PDF file.

        Returns:
            A list of TextBlock objects.
        """
        doc = fitz.open(pdf_path)
        blocks = []
        for page_num, page in enumerate(doc):
            page_blocks = page.get_text("dict")["blocks"]
            for block_num, block in enumerate(page_blocks):
                if block['type'] == 0:  # Text block
                    for line_num, line in enumerate(block['lines']):
                        for span_num, span in enumerate(line['spans']):
                            blocks.append(TextBlock(
                                text=span['text'].strip(),
                                font_size=span['size'],
                                font_name=span['font'],
                                is_bold='bold' in span['font'].lower(),
                                is_italic='italic' in span['font'].lower(),
                                x0=span['bbox'][0],
                                y0=span['bbox'][1],
                                x1=span['bbox'][2],
                                y1=span['bbox'][3],
                                block_num=block_num,
                                line_num=line_num,
                                span_num=span_num
                            ))
        return blocks