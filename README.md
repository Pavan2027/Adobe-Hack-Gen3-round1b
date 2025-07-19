# PDF Outline Extractor

This project extracts the hierarchical outline (table of contents) from a PDF document. It uses a rule-based approach to identify headings based on font size, style, and other textual features.

## 🌟 Features

* Extracts headings and their hierarchical levels.
* Rule-based, no ML model required.
* Lightweight and fast.
* Dockerized for easy deployment.

## 🛠️ Setup

### Prerequisites

* Docker

### Installation

1.  Clone this repository:
    ```bash
    git clone <your-repo-url>
    cd pdf-outline-extractor
    ```

2.  Build the Docker image:
    ```bash
    docker build -t pdf-outline-extractor .
    ```

## 🏃‍♀️ Running the Extractor

To extract the outline from a PDF file, place your PDF in the `data` directory and run the following command:

```bash
docker run -v $(pwd)/data:/app/data pdf-outline-extractor python main.py data/your_document.pdf