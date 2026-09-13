Project Title:
Corridor IQ: Agentic Commercial Location Intelligence & Site Selection

Project URL  : https://beyond-the-prompt-1.onrender.com/

Problem Statement:
Traditional commercial site selection relies on aggregate, static foot-traffic volumes and median household incomes. These flat metrics hide critical dimensions: when people are present, who makes up the customer base, and whether category demand is already oversaturated.  


Consequently, retail and hospitality brands frequently misallocate capital. They lease spaces in districts that appear bustling on paper but suffer from temporal mismatch (e.g., launching an early-morning commuter cafe in a late-night bar district) or market saturation (entering corridors dominated by established chains). Furthermore, emerging AI real estate tools act as black boxes that hallucinate recommendations without verifiable, ground-truth data evidence.  


Solution:
Corridor IQ is a dual-interface decision platform powered by the Model Context Protocol (MCP) that replaces flat footfall assumptions with multi-dimensional behavioral models.  


By indexing 137 commercial districts across New York City and Dallas–Fort Worth, Corridor IQ combines natural language intent extraction with an explainable, weighted evaluation model:  

Audience Persona Fit (35%): Measures alignment with 55 demographic personas (e.g., hybrid workers, morning commuters, families).  

Business Format Fit (25%): Evaluates category fit scores and opportunity whitespace signals.  


Corridor Momentum (20%): Factors in neighborhood growth trajectory and revitalization velocity.  
JSON

Geography & Safety (10%): Filters by evening perception and neighborhood access constraints.  

Competition Opportunity (10%): Penalizes high chain dominance to prevent supply cannibalization.  
JSON

The system exposes ground-truth tool primitives to LLM agents via MCP while providing human analysts with interactive spatial maps, click-to-view parameter scorecards, and side-by-side comparative rankings.  


Project Description:
Corridor IQ bridges the gap between raw behavioral datasets and real-world commercial investment decisions. Ingesting over 18,000 ground-truth fit scores, 55 audience personas, and 5-part daily activity curves from NYC and DFW metros, the platform enables operators to answer: "Where should I expand, what signals justify it, and what operational window will succeed?"  

The platform features a modern landing hub that leads into a conversational AI Advisor. When an entrepreneur asks, "What business do you want to begin with?", the advisor translates their vision into ground-truth constraints, identifies top candidates, pins the #1 recommendation on an interactive Folium map with full popup parameter scorecards, and displays a comprehensive multi-factor comparison table below.  


Key Features
Conversational AI Advisor (Level 3 MCP Agent): Natural language interface that decodes commercial concepts (e.g., "Specialty Coffee in Dallas") and routes queries through ground-truth tool calling without hallucination.  


Explainable 5-Factor Weighted Scorecard: Eliminates black-box scoring by decomposing every recommendation into exact metrics: Audience Fit (35%), Business Fit (25%), Corridor Score (20%), Geography/Safety (10%), and Competition (10%).  


Temporal Daypart Matching: Visualizes 5-part activity curves (AM, Midday, Evening, Late Night, Weekend) to prevent operating hour mismatches (e.g., Deep Ellum late-night vs. Keller morning commuters).  

Interactive Folium Spatial Mapping: Dynamically centers and pins the top-ranked district on a live map, featuring clickable popup scorecards revealing detailed underlying metrics.  

Side-by-Side Landmark Parameter Comparison: Tabulates candidate districts across individual scoring dimensions for rapid executive benchmarking.  


Commercial Opportunity Finder (Level 1 & 2): Macro-level screening tool that ranks all 137 corridors across category whitespace quality, neighborhood momentum, and customizable evening safety thresholds.  


Multi-Metro Schema Adaptability: Built-in normalization that seamlessly ingests both NYC's canonical H3-10 mapped districts and DFW's behavioral calculus envelopes.  


Technical Overview :

# NYC and Dallas–Fort Worth corridor exports

Portable JSON exports from the active Mongo bundle `usa-corridors-20260906-r2`.
The files are read-only snapshots; applications should not infer a newer release by
directory order. Use `EXPORT_MANIFEST.json` for the pinned release IDs, counts and
SHA-256 checksums.

## Files

- `NYC_CORRIDORS.full.json` — 65 corridor records (60 macro and 5 sub-corridors),
  55 audience segments, 31 café archetypes, 1,860 corridor/archetype scores, 25
  special zones and 60 bounded map-context records.
- `NYC_CORRIDOR_H3_10_OWNERSHIP.json` — all 81,767 exact H3-10 ownership rows plus
  an H3-9 display projection grouped by corridor. H3-10 is the authoritative grain.
- `DALLAS_FORT_WORTH_CORRIDORS.full.json` — 72 corridors, 55 audience segments, 31
  café plus 36 restaurant archetypes, 4,824 corridor/archetype scores, 37 special
  zones, 72 map envelopes and 72 bounded map-context records.
- `EXPORT_MANIFEST.json` — release lineage, record counts, byte sizes and checksums.

## Important geometry distinction

NYC has canonical, non-overlapping H3-10 corridor ownership. Dallas–Fort Worth does
not yet have canonical H3-10 ownership; its exported H3-9 geometry is a named activity
display envelope and must not be treated as a parcel boundary or exact site catchment.

## Rebuilding

Run `v26/scripts/export_corridor_data.py` against the active Mongo bundle. The script
resolves releases through the live bundle pointer and accepts explicit metro IDs; it
does not choose releases from directory order.

