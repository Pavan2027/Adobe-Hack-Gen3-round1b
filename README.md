# 📘 Persona-Driven Document Intelligence – Round 1B

This project is a solution for **Round 1B** of the Adobe India Hackathon – _"Connecting the Dots"_. It processes a collection of PDFs and returns the most relevant sections based on a user persona and their job-to-be-done.

It uses a rule-based outline extraction pipeline (from Round 1A) and augments it with filtering logic to score and rank document sections by semantic relevance.

---

## 🌟 Features

- ✅ Extracts and ranks sections by relevance to a given persona and job.
- ✅ Uses keyword and formatting-based heuristics (no internet or GPU required).
- ✅ Outputs structured JSON with:
  - Extracted sections
  - Importance ranks
  - Sub-section insights
- ✅ Fully dockerized and runs offline.


---

## 🛠️ Setup

### 🔧 Prerequisites

- Docker (ensure support for `linux/amd64` platform)

### 🧱 Build the Docker Image

From the root of the project:

```bash
docker build --platform linux/amd64 -t round1b:latest .
```

### 🏃‍♀️ Running the Main File

To run the solution, place your PDF in the `collections` directory with the input json file and run the following command:

```bash
docker run --rm -v "$(pwd)/collections:/app/collections" --network none round1b:latest
```
