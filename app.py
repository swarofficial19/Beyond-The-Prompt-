import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Corridor Scout AI", layout="wide", page_icon="🏙️")

@st.cache_data
def load_corridors(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("corridors", [])

# Sidebar Configuration
st.sidebar.title("🏙️ Corridor Scout")
metro_choice = st.sidebar.selectbox("Select Metro Region", ["New York City (NYC)", "Dallas–Fort Worth (DFW)"])
data_file = "NYC_CORRIDORS.full.json" if "NYC" in metro_choice else "DALLAS_FORT_WORTH_CORRIDORS.full.json"

try:
    corridors = load_corridors(data_file)
except Exception as e:
    st.error(f"Error loading {data_file}: {e}")
    st.stop()

# THIS DEFINES 'mode' - MUST BE ABOVE ALL 'if mode ==' STATEMENTS
mode = st.sidebar.radio("Product Mode", [
    "🎯 Opportunity Finder (Level 1)", 
    "🧬 Corridor DNA Card & Map (Level 2)", 
    "👥 Persona → Place Matcher (Level 2)",
    "💬 Ask Corridor AI / MCP (Level 3)"
])

# -----------------------------------------------------------------------------
# MODE 1: OPPORTUNITY FINDER (Level 1)
# -----------------------------------------------------------------------------
if mode == "🎯 Opportunity Finder (Level 1)":
    st.header(f"🎯 Expansion Opportunity Finder — {metro_choice}")
    st.caption("Score and rank commercial districts using whitespace quality, market momentum, and evening safety.")

    col1, col2 = st.columns(2)
    with col1:
        target_sector = st.selectbox(
            "Target Sector", 
            ["cafe", "fitness", "beauty_wellness", "qsr", "fast_casual", "grocery_convenience"]
        )
    with col2:
        min_safety = st.slider("Minimum Evening Safety Index", 0, 100, 50)

    rows = []
    for c in corridors:
        b = c.get("behavior", {})
        safety = b.get("crime_safety", {}).get("evening", 60)
        if safety < min_safety:
            continue

        whitespace = b.get("whitespace_quality", {}).get(target_sector, 50)
        momentum = b.get("neighborhood_momentum", 50)
        
        # Opportunity Index: 40% Whitespace + 30% Momentum + 30% Safety
        opp_index = round((whitespace * 0.4) + (momentum * 0.3) + (safety * 0.3), 1)

        rows.append({
            "Corridor": c.get("name"),
            "District": c.get("borough") or c.get("district", "N/A"),
            "Form": c.get("form", "N/A"),
            "Opportunity Index": opp_index,
            f"{target_sector.title()} Whitespace": whitespace,
            "Momentum": momentum,
            "Safety (Evening)": safety
        })

    df_ranked = pd.DataFrame(rows).sort_values(by="Opportunity Index", ascending=False)
    
    st.subheader(f"Top Recommended Districts for {target_sector.title()}")
    st.dataframe(df_ranked.head(10), use_container_width=True)

    if not df_ranked.empty:
        st.bar_chart(df_ranked.head(7).set_index("Corridor")["Opportunity Index"])

# -----------------------------------------------------------------------------
# MODE 2: CORRIDOR DNA OVERVIEW & MAP (Level 2)
# -----------------------------------------------------------------------------
elif mode == "🧬 Corridor DNA Card & Map (Level 2)":
    st.header(f"🧬 Corridor DNA Overview — {metro_choice}")
    st.caption("Inspect district character, daypart activity density, spatial location, and demographics at a glance.")

    corridor_names = [c.get("name") for c in corridors]
    selected_name = st.selectbox("Select Corridor to Profile", corridor_names)
    c = next(item for item in corridors if item.get("name") == selected_name)

    colA, colB = st.columns([3, 1])
    with colA:
        st.subheader(c.get("name"))
        st.markdown(f"**District:** {c.get('borough') or c.get('district', 'N/A')} | **Form:** `{c.get('form', 'N/A')}`")
        st.info(f"**Character:** {c.get('character')}")
    with colB:
        st.metric(label="Neighborhood Momentum", value=f"{c.get('behavior', {}).get('neighborhood_momentum', 'N/A')}/100")
        st.metric(label="Transit vs Car", value=f"{c.get('behavior', {}).get('transit_car_orientation', 'N/A')}% Transit")

    st.divider()

    # Visual Map Component
    st.markdown("#### 🗺️ Geographic Location")
    coords_dict = {
        "Manhattan": [40.7831, -73.9712],
        "Brooklyn": [40.6782, -73.9442],
        "Bronx": [40.8448, -73.8648],
        "Queens": [40.7282, -73.7949],
        "Staten Island": [40.5795, -74.1502],
        "Dallas Core": [32.7767, -96.7970],
        "Collin County": [33.1972, -96.6398],
        "Denton County": [33.2148, -97.1331],
        "Tarrant East": [32.7555, -97.3308],
        "Alliance-North FW": [32.9343, -97.2295],
        "Southern": [32.5421, -97.3208],
        "Fort Worth West": [32.7601, -97.4589]
    }
    coords_dfw = {
        "Deep Ellum": [32.7831, -96.7844],
        "McKinney–Historic Downtown": [33.1972, -96.6153],
        "The Colony–Grandscape": [33.0766, -96.8837],
        "Little Elm": [33.1626, -96.9375],
        "Keller–Old Town Keller": [32.9343, -97.2295],
        "Burleson–Old Town": [32.5421, -97.3208],
        "East Fort Worth–Woodhaven": [32.7667, -97.2344],
        "Lakewood–Casa Linda": [32.8168, -96.7197],
        "West Fort Worth–White Settlement": [32.7601, -97.4589]
    }

    if c.get("name") in coords_dfw:
        lat, lon = coords_dfw[c.get("name")]
    else:
        district_key = c.get("borough") or c.get("district", "Manhattan")
        lat, lon = coords_dict.get(district_key, [40.7128, -74.0060])

    map_df = pd.DataFrame([{"lat": lat, "lon": lon, "name": c.get("name")}])
    st.map(map_df, zoom=12)

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown("#### 🕒 Daypart Activity Density")
        dayparts = c.get("behavior", {}).get("daypart_occasion_density", {})
        if dayparts:
            df_day = pd.DataFrame(list(dayparts.items()), columns=["Daypart", "Activity Level"])
            st.bar_chart(df_day.set_index("Daypart"))

    with col_right:
        st.markdown("#### 👥 Top 8 Audience Personas (Score 1–9)")
        aud = c.get("audience_scores", {})
        if aud:
            df_aud = pd.DataFrame(list(aud.items()), columns=["Persona", "Score"]).sort_values(by="Score", ascending=False).head(8)
            st.dataframe(df_aud, use_container_width=True)

    anchors = c.get("anchors")
    if anchors:
        st.markdown("#### 📍 Core Landmarks & Activity Anchors")
        anchor_list = [f"**{a.get('name')}** ({a.get('class', 'Landmark')})" for a in anchors if a.get("name")]
        st.write(" • ".join(anchor_list))

# -----------------------------------------------------------------------------
# MODE 3: PERSONA -> PLACE MATCHING (Level 2)
# -----------------------------------------------------------------------------
elif mode == "👥 Persona → Place Matcher (Level 2)":
    st.header(f"👥 Persona → Place Matcher — {metro_choice}")
    st.caption("Select a customer demographic to discover districts where they are most concentrated.")

    sample_aud = corridors[0].get("audience_scores", {})
    available_personas = sorted(list(sample_aud.keys()))
    
    default_idx = available_personas.index("family_household") if "family_household" in available_personas else 0
    chosen_persona = st.selectbox("Select Target Demographic Persona", available_personas, index=default_idx)

    recs = []
    for c in corridors:
        score = c.get("audience_scores", {}).get(chosen_persona, 0)
        recs.append({
            "Corridor": c.get("name"),
            "District": c.get("borough") or c.get("district", "N/A"),
            "Audience Relevance (1–9)": score,
            "Weekend Density": c.get("behavior", {}).get("daypart_occasion_density", {}).get("weekend_day", "N/A"),
            "Evening Density": c.get("behavior", {}).get("daypart_occasion_density", {}).get("weekday_evening", "N/A")
        })

    df_recs = pd.DataFrame(recs).sort_values(by="Audience Relevance (1–9)", ascending=False)
    st.subheader(f"Top Corridors for: {chosen_persona.replace('_', ' ').title()}")
    st.dataframe(df_recs.head(10), use_container_width=True)

# -----------------------------------------------------------------------------
# MODE 4: ASK CORRIDOR AI / MCP (Level 3)
# -----------------------------------------------------------------------------
elif mode == "💬 Ask Corridor AI / MCP (Level 3)":
    st.header("💬 Ask Corridor AI (Natural Language Tool Calling)")
    st.caption("Ask questions in plain English. The agent parses intent and calls MCP tool primitives across ground-truth datasets.")

    user_query = st.text_input(
        "Ask a question about commercial corridors:", 
        placeholder="e.g., I want to open a premium cafe for professionals in New York"
    )

    if user_query:
        from mcp_server import search_corridor, get_corridor_dna, CORRIDOR_DB
        
        q_lower = user_query.lower()
        st.markdown("##### ⚙️ MCP Agent Execution Trace:")

        # Step 1: Detect Metro intent
        filter_metro = None
        if any(term in q_lower for term in ["new york", "nyc", "manhattan", "brooklyn", "bronx", "queens"]):
            filter_metro = "nyc"
            st.write("🔍 *Intent detected:* Target Metro = **New York City**")
        elif any(term in q_lower for term in ["dallas", "dfw", "fort worth", "texas"]):
            filter_metro = "dallas-fort-worth"
            st.write("🔍 *Intent detected:* Target Metro = **Dallas–Fort Worth**")

        # Step 2: Check for specific named corridor match
        found = search_corridor(user_query)
        
        candidates = list(CORRIDOR_DB.values())
        if filter_metro:
            candidates = [c for c in candidates if c.get("metro_id") == filter_metro]

        if found and len(found) == 1:
            target_name = found[0]["name"]
            st.write(f"🔧 *Agent selected MCP tool:* `get_corridor_dna(corridor_name='{target_name}')`")
            dna_result = get_corridor_dna(target_name)
            
            st.success(f"**Analysis for {target_name}:**")
            st.write(f"*{dna_result.get('character')}*")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Top Demographic Personas:**")
                st.json(dna_result.get("top_audiences", {}))
            with c2:
                st.markdown("**Daypart Density:**")
                st.json(dna_result.get("daypart_density", {}))

        else:
            # Step 3: Multi-corridor ranking across ground-truth signals
            st.write("🔧 *Agent executing MCP multi-corridor ranking across ground-truth signals...*")
            
            scored_matches = []
            for c in candidates:
                score = 0
                reasons = []
                b = c.get("behavior", {})
                aud = c.get("audience_scores", {})
                
                # Check Cafe / Coffee intent
                if "cafe" in q_lower or "coffee" in q_lower:
                    cafe_ws = b.get("whitespace_quality", {}).get("cafe", 50)
                    score += cafe_ws * 0.4
                    reasons.append(f"Café whitespace: {cafe_ws}")
                    
                # Check Professional / Work / Remote intent
                if any(w in q_lower for w in ["professional", "office", "work", "remote", "laptop"]):
                    work_score = aud.get("hybrid_remote", 0) + aud.get("office_routine", 0)
                    score += work_score * 8
                    reasons.append(f"Work/Remote audience: {work_score}/18")
                    
                # Check Premium / Upscale intent
                if any(w in q_lower for w in ["premium", "luxury", "upscale"]):
                    prem_score = aud.get("resident_premium", 0) + aud.get("premium_shoppers", 0)
                    score += prem_score * 6
                    reasons.append(f"Premium demographic: {prem_score}/18")
                    
                # Check Nightlife / Evening intent
                if any(w in q_lower for w in ["night", "nightlife", "bar", "evening"]):
                    night_score = aud.get("late_night_social", 0) + (b.get("daypart_occasion_density", {}).get("late_night", 0) / 10)
                    score += night_score * 5
                    reasons.append(f"Nightlife score: {night_score:.1f}")

                # Check Family / Suburban intent
                if any(w in q_lower for w in ["family", "suburb", "school", "kids"]):
                    fam_score = aud.get("family_household", 0)
                    score += fam_score * 8
                    reasons.append(f"Family household score: {fam_score}/9")

                if score > 0:
                    scored_matches.append({
                        "name": c.get("name"),
                        "district": c.get("borough") or c.get("district", "N/A"),
                        "character": c.get("character"),
                        "score": round(score, 1),
                        "evidence": " • ".join(reasons[:2])
                    })

            if scored_matches:
                scored_matches.sort(key=lambda x: x["score"], reverse=True)
                top_match = scored_matches[0]
                
                # Fetch full DNA via MCP function
                top_dna = get_corridor_dna(top_match["name"])
                
                st.success(f"**Top Recommended District: {top_match['name']} ({top_match['district']})**")
                st.write(f"*{top_match['character']}*")
                
                st.markdown(f"**Key Supporting Signals:** {top_match['evidence']}")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Top Demographic Audiences:**")
                    st.json(top_dna.get("top_audiences", {}))
                with c2:
                    st.markdown("**Time-of-Day Activity Index:**")
                    st.json(top_dna.get("daypart_density", {}))

                st.divider()
                st.markdown("##### Alternative Recommended Matches:")
                st.dataframe(pd.DataFrame(scored_matches[1:5])[["name", "district", "score", "evidence"]])
            else:
                st.warning("Could not identify specific intent patterns. Try asking with keywords like 'cafe', 'professionals', 'nightlife', or 'families'.")