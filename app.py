import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Opportunity Finder", layout="wide")

@st.cache_data
def load_data(city):
    filename = "NYC_CORRIDORS.full.json" if city == "New York City" else "DALLAS_FORT_WORTH_CORRIDORS.full.json"
    filepath = os.path.join("starter-kit", "usa-corridors-20260906-r2", filename)
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    return data

st.title("Corridor Opportunity Finder 🏪")
st.markdown("Find the best corridors for a new business based on fit, opportunity (whitespace), and existing supply.")

city = st.sidebar.selectbox("Select City", ["New York City", "Dallas-Fort Worth"])
data = load_data(city)

# Extract Data
corridors = {c['corridor_id']: c for c in data['corridors']}
archetypes = {a['archetype_id']: a for a in data['archetypes']}
scores = data['corridor_archetype_scores']

# Get available archetypes for the dropdown
archetype_options = {a['archetype_id']: f"{a['name']} ({a['category_id']})" for a in archetypes.values()}
selected_arch_id = st.sidebar.selectbox(
    "Select Business Format", 
    options=list(archetype_options.keys()), 
    format_func=lambda x: archetype_options[x]
)

# Filter scores for selected archetype
arch_scores = [s for s in scores if s['archetype_id'] == selected_arch_id]

results = []
for s in arch_scores:
    c_id = s['corridor_id']
    if c_id not in corridors:
        continue
    
    c = corridors[c_id]
    
    # Extract existing supply
    category = archetypes[selected_arch_id]['category_id']
    existing_supply = 0
    if category in c.get('places', {}).get('semantic_classes', {}):
        existing_supply = c['places']['semantic_classes'][category].get('listing_count', 0)
    
    # Extract whitespace signal
    whitespace = 0.0
    if 'behavior' in c and 'whitespace_quality' in c['behavior']:
        whitespace = c['behavior']['whitespace_quality'].get(category.lower(), 0.0)
    
    # Opportunity = Fit Score + Whitespace - Penalty for existing supply
    # This is a simple ranking logic as suggested in the guide
    fit_score = s.get('score', 0.0)
    opportunity_score = fit_score + whitespace - (existing_supply * 0.01)
    
    results.append({
        "Corridor": c.get('name', 'Unknown'),
        "Borough/District": c.get('borough', c.get('district', 'Unknown')),
        "Fit Tier": s.get('tier', 'UNKNOWN'),
        "Fit Score": round(fit_score, 3),
        "Whitespace Signal": round(whitespace, 3),
        "Existing Supply": existing_supply,
        "Total Opportunity Score": round(opportunity_score, 3)
    })

if results:
    df = pd.DataFrame(results)
    # Sort by Opportunity Score descending
    df = df.sort_values(by="Total Opportunity Score", ascending=False).reset_index(drop=True)
    
    st.subheader(f"Top Opportunities for '{archetype_options[selected_arch_id]}'")
    
    # Highlight top 3
    cols = st.columns(3)
    for i in range(min(3, len(df))):
        with cols[i]:
            st.metric(label=f"#{i+1}: {df.iloc[i]['Corridor']}", value=f"Score: {df.iloc[i]['Total Opportunity Score']}")
            st.caption(f"Fit: {df.iloc[i]['Fit Score']} | Whitespace: {df.iloc[i]['Whitespace Signal']}")
    
    st.markdown("---")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No data available for the selected business format.")

st.sidebar.markdown("---")
st.sidebar.info("This tool uses the logic suggested in 'Example 01: Corridor Opportunity Finder'. It ranks corridors based on Fit Score + Whitespace - Existing Supply penalty.")
