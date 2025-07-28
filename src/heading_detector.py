import pandas as pd

class HeadingDetector:
    """Detects headings from a DataFrame of text features."""

    def detect(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies rules to identify headings and their levels.

        Args:
            features_df: DataFrame with text block features.

        Returns:
            A DataFrame with an added 'is_heading' and 'heading_level' column.
        """
        font_size_threshold = features_df['font_size'].quantile(0.90) 
        features_df['is_heading'] = (features_df['font_size'] >= font_size_threshold) & \
                                     (features_df['word_count'] < 20) & \
                                     (~features_df['ends_with_period'])

        headings = features_df[features_df['is_heading']].copy()
        unique_font_sizes = sorted(headings['font_size'].unique(), reverse=True)
        size_to_level = {size: i + 1 for i, size in enumerate(unique_font_sizes)}
        features_df['heading_level'] = features_df['font_size'].map(size_to_level).fillna(0)

        return features_df