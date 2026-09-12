import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from mcp_server import analyze_and_rank_corridors, ALL_CORRIDORS

st.set_page_config(page_title="Corridor Advisor AI", layout="wide", page_icon="🏙️")

st.sidebar.title("🏙️ Navigation")
app_mode = st.sidebar.radio(
    "Select Feature", 
    ["💬 Ask AI Advisor (Chatbot Model)", "🎯 Opportunity Finder"]
)

# -----------------------------------------------------------------------------
# 1. CHATBOT MODEL: ASK AI ADVISOR
# -----------------------------------------------------------------------------
if app_mode == "💬 Ask AI Advisor (Chatbot Model)":
    st.title("🤖 Commercial Corridor AI Advisor")
    st.markdown("Ground-truth intelligence engine powered by Model Context Protocol (MCP) data models.")

    # Initialize chat history and analysis state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome! **What business do you want to begin with?** (e.g., *Specialty Coffee Shop*, *Boutique Fitness Studio*, *Late-Night Gastrobar*, *Family Pizzeria*)"}
        ]
    if "latest_analysis" not in st.session_state:
        st.session_state.latest_analysis = None

    # Render previous text messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User Input
    user_query = st.chat_input("Enter your business concept, target customers, or preferred city...")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # NLP intent extraction
        q_lower = user_query.lower()
        metro = None
        if any(w in q_lower for w in ["nyc", "new york", "brooklyn", "manhattan", "bronx", "queens"]):
            metro = "nyc"
        elif any(w in q_lower for w in ["dallas", "dfw", "fort worth", "texas"]):
            metro = "dallas-fort-worth"

        biz_type = "cafe"
        if any(w in q_lower for w in ["fitness", "gym", "yoga", "pilates"]):
            biz_type = "fitness"
        elif any(w in q_lower for w in ["nightlife", "bar", "pub", "gastrobar", "club"]):
            biz_type = "nightlife"
        elif any(w in q_lower for w in ["beauty", "wellness", "salon", "spa"]):
            biz_type = "beauty_wellness"
        elif any(w in q_lower for w in ["qsr", "fast food", "tacos", "burger"]):
            biz_type = "qsr"
        elif any(w in q_lower for w in ["grocery", "supermarket", "convenience"]):
            biz_type = "grocery_convenience"

        recommendations = analyze_and_rank_corridors(business_type=biz_type, query=user_query, metro_filter=metro, top_n=3)
        st.session_state.latest_analysis = {
            "biz_type": biz_type,
            "metro": metro,
            "recommendations": recommendations
        }
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"**Analysis complete:** Identified top 3 expansion locations for **{biz_type.upper()}**."
        })
        st.rerun()

    # RENDER MAP FOR #1 ONLY, POPUP, AND COMPARISON TABLE
    if st.session_state.latest_analysis:
        analysis = st.session_state.latest_analysis
        recs = analysis["recommendations"]
        biz_type = analysis["biz_type"]
        top = recs[0]  # The #1 Choice

        st.divider()
        st.markdown(f"### 📍 Location Recommendation Analysis for: **{biz_type.upper()}**")
        st.caption("Evaluated against ground-truth demographic fit, daypart rhythm, saturation, and corridor momentum.")

        # INTERACTIVE FOLIUM MAP (ONLY #1 LOCATION DISPLAYED)
        st.markdown(f"#### 🗺️ #1 Recommended Location: {top['name']}")
        st.info("💡 **Click on the map marker pin** to inspect its full ground-truth parameter scorecard.")

        # Center map directly on the #1 location
        m = folium.Map(location=top["coords"], zoom_start=13)

        popup_html = f"""
        <div style='font-family: sans-serif; min-width: 220px;'>
            <h4 style='margin: 0; color: #1E3A8A;'>🏆 Top Choice: {top['name']}</h4>
            <p style='font-size: 12px; color: #555; margin-top: 2px;'><i>{top['district']} ({top['metro']})</i></p>
            <hr style='margin: 6px 0;'/>
            <b style='font-size: 15px; color: #10B981;'>Overall Score: {top['overall_score']} / 100</b><br/><br/>
            <span style='font-size: 12px;'>• Audience Fit (35%): <b>{top['audience_fit']}</b></span><br/>
            <span style='font-size: 12px;'>• Business Fit (25%): <b>{top['business_fit']}</b></span><br/>
            <span style='font-size: 12px;'>• Corridor Score (20%): <b>{top['corridor_score']}</b></span><br/>
            <span style='font-size: 12px;'>• Geography/Safety (10%): <b>{top['geography_fit']}</b></span><br/>
            <span style='font-size: 12px;'>• Competition Score (10%): <b>{top['competition_score']}</b></span>
        </div>
        """

        folium.Marker(
            location=top["coords"],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"🏆 #1 Choice: {top['name']} (Score: {top['overall_score']})",
            icon=folium.Icon(color="green", icon="star")
        ).add_to(m)

        st_folium(m, width=1000, height=450, returned_objects=[])

        # COMPARISON TABLE BELOW MAP
        st.markdown("#### 📊 Side-by-Side Landmark Parameter Comparison")
        comp_rows = []
        for idx, r in enumerate(recs):
            comp_rows.append({
                "Rank": f"#{idx+1}",
                "Landmark / Corridor": r["name"],
                "District": f"{r['district']} ({r['metro']})",
                "Overall Score": f"{r['overall_score']} / 100",
                "Audience Fit (35%)": r["audience_fit"],
                "Business Fit (25%)": r["business_fit"],
                "Corridor Score (20%)": r["corridor_score"],
                "Geography (10%)": r["geography_fit"],
                "Competition (10%)": r["competition_score"]
            })
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

        # TOP CHOICE DETAILS & CHARTS
        st.success(f"🏆 **Top Choice: {top['name']} ({top['district']})** — Total Weighted Score: **{top['overall_score']} / 100**")
        st.markdown(f"*{top['character']}*")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 👥 Top Audience Demographics (Scores 1–9)")
            st.json(top["top_audiences"])
        with col2:
            st.markdown("##### 🕒 Time-of-Day Activity Index")
            if top.get("daypart_curve"):
                df_day = pd.DataFrame(list(top["daypart_curve"].items()), columns=["Daypart", "Density"]).set_index("Daypart")
                st.bar_chart(df_day)

# -----------------------------------------------------------------------------
# 2. OPPORTUNITY FINDER
# -----------------------------------------------------------------------------
elif app_mode == "🎯 Opportunity Finder":
    st.header("🎯 Commercial Opportunity Finder")
    st.caption("Scan all corridors across whitespace quality, market momentum, and evening safety.")

    metro_filter = st.selectbox("Select Metro", ["Both Metros", "New York City (NYC)", "Dallas–Fort Worth (DFW)"])
    sector = st.selectbox("Select Target Sector", ["cafe", "fitness", "beauty_wellness", "qsr", "fast_casual", "grocery_convenience"])
    min_safety = st.slider("Minimum Evening Safety Index", 0, 100, 50)

    rows = []
    for c in ALL_CORRIDORS:
        if metro_filter == "New York City (NYC)" and c.get("metro_id") != "nyc":
            continue
        if metro_filter == "Dallas–Fort Worth (DFW)" and c.get("metro_id") != "dallas-fort-worth":
            continue

        b = c.get("behavior", {})
        safety = b.get("crime_safety", {}).get("evening", 60)
        if safety < min_safety:
            continue

        whitespace = b.get("whitespace_quality", {}).get(sector, 50)
        momentum = b.get("neighborhood_momentum", 50)
        opp_index = round((whitespace * 0.4) + (momentum * 0.3) + (safety * 0.3), 1)

        rows.append({
            "Corridor": c.get("name"),
            "Metro": "NYC" if c.get("metro_id") == "nyc" else "DFW",
            "District": c.get("borough") or c.get("district", "N/A"),
            "Opportunity Index": opp_index,
            f"{sector.title()} Whitespace": whitespace,
            "Momentum": momentum,
            "Evening Safety": safety
        })

    df_ranked = pd.DataFrame(rows).sort_values(by="Opportunity Index", ascending=False)
    st.subheader(f"Ranked Corridors for {sector.title()}")
    st.dataframe(df_ranked.head(15), use_container_width=True)
    if not df_ranked.empty:
        st.bar_chart(df_ranked.head(8).set_index("Corridor")["Opportunity Index"])