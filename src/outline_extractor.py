from .pdf_parser import PDFParser
from .feature_extractor import FeatureExtractor
from .heading_detector import HeadingDetector
from .data_structures import Heading
from typing import List

class OutlineExtractor:
    """Extracts the outline from a PDF file."""

    def __init__(self):
        self.parser = PDFParser()
        self.feature_extractor = FeatureExtractor()
        self.heading_detector = HeadingDetector()

    def extract_outline(self, pdf_path: str) -> List[dict]:
        """
        The main method to extract the hierarchical outline.

        Args:
            pdf_path: The path to the PDF file.

        Returns:
            A list of dictionaries representing the outline.
        """
        text_blocks = self.parser.parse(pdf_path)
        features_df = self.feature_extractor.extract_features(text_blocks)
        headings_df = self.heading_detector.detect(features_df)

        outline = []
        for index, row in headings_df[headings_df['is_heading']].iterrows():
            outline.append(Heading(
                text=row['text'],
                level=int(row['heading_level']),
                font_size=row['font_size'],
                font_name='', # You can enhance pdf_parser to get this
                page_num=0 # You can enhance pdf_parser to get this
            ).__dict__)

        return outline