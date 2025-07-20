from dataclasses import dataclass
from typing import List

@dataclass
class TextBlock:
    """Represents a block of text extracted from a PDF."""
    text: str
    font_size: float
    font_name: str
    is_bold: bool
    is_italic: bool
    x0: float
    y0: float
    x1: float
    y1: float
    block_num: int
    line_num: int
    span_num: int

@dataclass
class Heading:
    """Represents a detected heading."""
    text: str
    level: int
    font_size: float
    font_name: str
    page_num: int