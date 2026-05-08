import json
import re
from datetime import datetime

# Configuration
CONSTRUCTS = {
    # Priority 1 - undated
    "TIME × WEIGHT × SPIN": {"priority": 1, "architectural_weight": 0.95},
    "Emergent Pathology": {"priority": 1, "architectural_weight": 0.95},
    "Japanese Whale Hunters v1": {"priority": 1, "architectural_weight": 0.95},
    # Priority 2 - bounded but imprecise
    "MaBell Principle": {"priority": 2, "architectural_weight": 0.8},
    "Cherenkov model of chills": {"priority": 2, "architectural_weight": 0.8},
    "Fold": {"priority": 2, "architectural_weight": 0.8},
    "Fisher-Rao formalization": {"priority": 2, "architectural_weight": 0.8},
    "Resonance Amplifier": {"priority": 2, "architectural_weight": 0.8},
    # Priority 3 - confirm and add context
    "BroSis Protocol": {"priority": 3, "architectural_weight": 0.6},
    "δ decomposition": {"priority": 3, "architectural_weight": 0.6},
}

def parse_conversations(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)
    
    construct_mentions = {c: {"first": None, "count": 0, "co_occurrence": {}} for c in CONSTRUCTS}
    
    for conv in data["conversations"]:
        conv_id = conv["id"]
        conv_title = conv["title"]
        created_at = conv["created_at"]
        
        for msg in conv["messages"]:
            content = msg.get("content", "")
            timestamp = msg.get("created_at", created_at)
            
            mentioned = [c for c in CONSTRUCTS if c in content]
            if mentioned:
                for construct in mentioned:
                    construct_mentions[construct]["count"] += 1
                    
                    # Track first mention
                    if not construct_mentions[construct]["first"] or \
                       datetime.fromisoformat(timestamp) < datetime.fromisoformat(construct_mentions[construct]["first"]["timestamp"]):
                        construct_mentions[construct]["first"] = {
                            "conversation_id": conv_id,
                            "conversation_title": conv_title,
                            "timestamp": timestamp,
                            "excerpt": content
                        }
                
                # Track co-occurrences
                if len(mentioned) > 1:
                    for c1 in mentioned:
                        for c2 in mentioned:
                            if c1 != c2:
                                construct_mentions[c1]["co_occurrence"][c2] = construct_mentions[c1]["co_occurrence"][c2] + 1 if c2 in construct_mentions[c1]["co_occurrence"] else 1
    
    return construct_mentions

def normalize_weights(mentions):
    # Normalize co-occurrence counts to weights (0-1)
    for construct, data in mentions.items():
        total = sum(data["co_occurrence"].values()) if data["co_occurrence"] else 1
        mentions[construct]["edges"] = {
            c: count / total for c, count in data["co_occurrence"].items()
        }
    return mentions

def generate_outputs(mentions):
    # Generate CONSTRUCT_TIMELINE.md
    timeline = "# CONSTRUCT_TIMELINE.md\n\n"
    timeline += "| Construct | First Mentioned | Conversation | Excerpt |\n"
    timeline += "|---|---|---|---|\n"
    
    # Generate STARFIELD_RAW.json
    stars = {}
    metadata = {"last_updated": datetime.now().isoformat(), "total_stars": len(mentions)}
    
    for construct, data in mentions.items():
        first = data["first"]
        timeline += f"| {construct} | {first["timestamp"]} | #{first["conversation_id"]} {first["conversation_title"]} | {first["excerpt"][:50]}... |\n"
        
        stars[construct] = {
            "label": construct,
            "domain": "core_cosmology",
            "constellation": "attractor_geometry",
            "origin_date": first["timestamp"],
            "first_documented": "pre-2026-01-12",
            "magnitude": CONSTRUCTS[construct]["architectural_weight"] * (data["count"] / 100),  # Simple citation factor
            "state": "stable" if data["count"] > 3 else "stub",
            "edges": data["edges"]
        }
    
    with open("CONSTRUCT_TIMELINE.md", "w") as f:
        f.write(timeline)
    
    with open("STARFIELD_RAW.json", "w") as f:
        json.dump({"stars": stars, "metadata": metadata}, f, indent=2)

if __name__ == "__main__":
    mentions = parse_conversations("conversations.json")
    mentions = normalize_weights(mentions)
    generate_outputs(mentions)
    print("Starfield mining complete. Output written to CONSTRUCT_TIMELINE.md and STARFIELD_RAW.json")