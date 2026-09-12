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

# 1. AI Advisor Section
st.header("🤖 AI Advisor")
st.markdown("What can I help you regarding the corridor finder?")
st.caption("Try asking: 'search for St. George' or 'dna of Downtown Brooklyn'")
user_q = st.chat_input("Ask a question about corridors, opportunities, or data...")
if user_q:
    with st.chat_message("user"):
        st.write(user_q)
    with st.chat_message("assistant"):
        try:
            import mcp_server
            # Simple keyword router to simulate LLM function calling
            q_lower = user_q.lower()
            if "search" in q_lower:
                term = q_lower.replace("search for", "").replace("search", "").strip()
                results = mcp_server.search_corridor(term)
                if results:
                    st.write(f"Here is what I found for '{term}':")
                    st.dataframe(pd.DataFrame(results))
                else:
                    st.write(f"I couldn't find any corridors matching '{term}'.")
            elif "dna" in q_lower or "details" in q_lower:
                term = q_lower.replace("dna of", "").replace("details of", "").strip()
                res = mcp_server.get_corridor_dna(term)
                if "error" in res:
                    st.error(res["error"])
                else:
                    st.write(f"**DNA Profile for {res['corridor']}**")
                    st.write(f"*{res['character']}*")
                    st.json(res)
            else:
                st.write("I am the AI Advisor! I am connected to the MCP tools. Try asking me to **search for [name]** or get the **DNA of [name]**.")
        except Exception as e:
            st.error(f"Error communicating with MCP tools: {e}")

st.markdown("---")

# Global Controls
city = st.sidebar.selectbox("Select City", ["New York City", "Dallas-Fort Worth"])
data = load_data(city)

# Extract Data
corridors = {c['corridor_id']: c for c in data.get('corridors', [])}
archetypes = {a['archetype_id']: a for a in data.get('archetypes', [])}
scores = data.get('corridor_archetype_scores', [])
corridor_options = {c_id: c['name'] for c_id, c in corridors.items()}
map_contexts = {m['corridor_id']: m for m in data.get('map', {}).get('corridor_context', [])}

# Create Tabs for the other features
tab1, tab2, tab3 = st.tabs(["📊 4. Opportunity Finder", "🗺️ 2. Map Explorer", "⚖️ 3. Compare Corridors"])

with tab1:
    st.subheader("Opportunity Finder")
    st.write("Rank corridors to find the best fit for a specific business format.")
    if archetypes:
        archetype_options = {a['archetype_id']: f"{a['name']} ({a['category_id']})" for a in archetypes.values()}
        selected_arch_id = st.selectbox(
            "Select Business Format", 
            options=list(archetype_options.keys()), 
            format_func=lambda x: archetype_options[x]
        )

        arch_scores = [s for s in scores if s['archetype_id'] == selected_arch_id]
        results = []
        for s in arch_scores:
            c_id = s['corridor_id']
            if c_id not in corridors:
                continue
            
            c = corridors[c_id]
            category = archetypes[selected_arch_id]['category_id']
            
            existing_supply = 0
            if category in c.get('places', {}).get('semantic_classes', {}):
                existing_supply = c['places']['semantic_classes'][category].get('listing_count', 0)
            
            whitespace = 0.0
            if 'behavior' in c and 'whitespace_quality' in c['behavior']:
                whitespace = c['behavior']['whitespace_quality'].get(category.lower(), 0.0)
            
            fit_score = s.get('score', 0.0)
            opportunity_score = fit_score + whitespace - (existing_supply * 0.01)
            
            results.append({
                "Corridor": c.get('name', 'Unknown'),
                "District": c.get('borough', c.get('district', 'Unknown')),
                "Fit Tier": s.get('tier', 'UNKNOWN'),
                "Fit Score": round(fit_score, 3),
                "Whitespace": round(whitespace, 3),
                "Existing Supply": existing_supply,
                "Opportunity Score": round(opportunity_score, 3)
            })

        if results:
            df = pd.DataFrame(results).sort_values(by="Opportunity Score", ascending=False).reset_index(drop=True)
            cols = st.columns(3)
            for i in range(min(3, len(df))):
                with cols[i]:
                    st.metric(label=f"#{i+1}: {df.iloc[i]['Corridor']}", value=f"Score: {df.iloc[i]['Opportunity Score']}")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No data available for the selected format.")
    else:
        st.warning("Archetype data not found.")

with tab2:
    st.subheader("Explain the location in the map")
    st.write("Visualize the key places that define this corridor.")
    selected_map_corridor = st.selectbox("Select a Corridor", options=list(corridor_options.keys()), format_func=lambda x: corridor_options[x], key='map_sel')
    
    if selected_map_corridor in map_contexts:
        m_ctx = map_contexts[selected_map_corridor]
        points = m_ctx.get('points', [])
        if points:
            st.write(f"Displaying **{len(points)}** key places mapped in {corridor_options[selected_map_corridor]}.")
            map_df = pd.DataFrame(points)
            st.map(map_df, size=15)
            st.write("Sample of mapped places:")
            st.dataframe(map_df[['name', 'category', 'family_label']].head())
        else:
            st.info("No map coordinates found for this corridor.")
    else:
        st.info("Map context is not available for the selected corridor.")

with tab3:
    st.subheader("Compare Corridors")
    st.write("View two corridors side-by-side to understand their differences.")
    colA, colB = st.columns(2)
    with colA:
        c1_id = st.selectbox("Corridor 1", options=list(corridor_options.keys()), format_func=lambda x: corridor_options[x], key='c1')
    with colB:
        c2_id = st.selectbox("Corridor 2", options=list(corridor_options.keys()), format_func=lambda x: corridor_options[x], key='c2')
        
    if c1_id and c2_id:
        c1 = corridors[c1_id]
        c2 = corridors[c2_id]
        
        # Helper to get total places safely
        def get_total_places(c):
            places = c.get('places', {}).get('semantic_classes', {})
            return sum([v.get('listing_count', 0) for v in places.values()])

        comp_data = {
            "Metric": [
                "Borough / District", 
                "Level", 
                "Total Existing Places", 
                "Dominant Audience", 
                "Character Description"
            ],
            c1['name']: [
                c1.get('borough', c1.get('district', 'N/A')),
                c1.get('level', 'N/A'),
                get_total_places(c1),
                c1.get('dominant_audience', 'N/A'),
                (c1.get('character', 'N/A')[:80] + "...") if c1.get('character') else "N/A"
            ],
            c2['name']: [
                c2.get('borough', c2.get('district', 'N/A')),
                c2.get('level', 'N/A'),
                get_total_places(c2),
                c2.get('dominant_audience', 'N/A'),
                (c2.get('character', 'N/A')[:80] + "...") if c2.get('character') else "N/A"
            ]
        }
        st.table(pd.DataFrame(comp_data))
