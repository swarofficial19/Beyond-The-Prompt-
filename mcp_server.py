import json

# Try importing FastMCP or MCPServer safely across all MCP versions
try:
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("CorridorIntelligence")
except Exception:
    try:
        from mcp.server.mcpserver import MCPServer
        mcp = MCPServer("CorridorIntelligence")
    except Exception:
        # Fallback dummy decorator so functions can always be imported by Streamlit
        class DummyMCP:
            def tool(self):
                return lambda f: f
            def run(self):
                pass
        mcp = DummyMCP()

def _load_corridor_index():
    records = {}
    import os
    base_path = os.path.join("starter-kit", "usa-corridors-20260906-r2")
    try:
        with open(os.path.join(base_path, "DALLAS_FORT_WORTH_CORRIDORS.full.json"), "r", encoding="utf-8") as f:
            for c in json.load(f).get("corridors", []):
                records[c.get("name", "").lower()] = c
        with open(os.path.join(base_path, "NYC_CORRIDORS.full.json"), "r", encoding="utf-8") as f:
            for c in json.load(f).get("corridors", []):
                records[c.get("name", "").lower()] = c
    except Exception as e:
        print("Error loading data:", e)
    return records

CORRIDOR_DB = _load_corridor_index()

@mcp.tool()
def search_corridor(query: str) -> list:
    """Search for commercial corridors by name or neighborhood keyword."""
    matches = []
    q = query.lower()
    for name, c in CORRIDOR_DB.items():
        if q in name or any(q in n.lower() for n in c.get("neighborhoods", [])):
            matches.append({
                "name": c.get("name"),
                "borough_or_district": c.get("borough") or c.get("district"),
                "character": c.get("character")
            })
    return matches[:5]

@mcp.tool()
def get_corridor_dna(corridor_name: str) -> dict:
    """Get the full demographic and daypart profile for a specific corridor."""
    c = CORRIDOR_DB.get(corridor_name.lower())
    if not c:
        return {"error": f"Corridor '{corridor_name}' not found."}
    
    aud = c.get("audience_scores", {})
    top_audiences = sorted(aud.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "corridor": c.get("name"),
        "character": c.get("character"),
        "top_audiences": dict(top_audiences),
        "daypart_density": c.get("behavior", {}).get("daypart_occasion_density", {}),
        "whitespace_quality": c.get("behavior", {}).get("whitespace_quality", {})
    }

if __name__ == "__main__":
    mcp.run()