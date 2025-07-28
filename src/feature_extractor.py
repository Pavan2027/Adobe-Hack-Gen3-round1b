import pandas as pd
from typing import List
from .data_structures import TextBlock

class FeatureExtractor:
    def extract_features(self, text_blocks: List[TextBlock]) -> pd.DataFrame:
        """
        Converts a list of TextBlock objects into a pandas DataFrame with features.

        Args:
            text_blocks: A list of TextBlock objects.

        Returns:
            A pandas DataFrame with features for each text block.
        """
        features = []
        for block in text_blocks:
            features.append({
                'text': block.text,
                'font_size': block.font_size,
                'is_bold': block.is_bold,
                'is_italic': block.is_italic,
                'is_all_caps': block.text.isupper(),
                'ends_with_period': block.text.endswith('.'),
                'word_count': len(block.text.split()),
                'char_count': len(block.text),
            })
        return pd.DataFrame(features)