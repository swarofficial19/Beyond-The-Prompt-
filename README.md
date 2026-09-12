# Corridor Opportunity Finder

This project was built for the Beyond the Prompt Hackathon (Day 2). 

## What it does
The **Corridor Opportunity Finder** is a web dashboard that helps businesses find the best corridors to open a new outlet. It ranks commercial corridors based on:
1. **Fit Score:** How well a specific business format fits the corridor.
2. **Whitespace Signal:** The potential room for growth.
3. **Existing Supply:** A penalty for corridors that already have many similar businesses.

## How to run it

### 1. Requirements
- Python 3.x
- Streamlit
- Pandas

### 2. Setup
Install the required Python packages:
```bash
pip install streamlit pandas
```

### 3. Run the App
Start the Streamlit server by running:
```bash
streamlit run app.py
```
The application will open in your browser at `http://localhost:8501`.

## Data Used
The application uses the provided JSON datasets from the starter kit (`NYC_CORRIDORS.full.json` and `DALLAS_FORT_WORTH_CORRIDORS.full.json`) to analyze and rank commercial districts.
