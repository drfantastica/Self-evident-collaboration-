import json
import os
from collections import defaultdict

# Constants
HISTORY_EXPORT = "/Users/black/aaron-context/history-export/"
OUTPUT_DIR = "/Users/black/aaron-context/"
STUB_THRESHOLD = 5  # Minimum co-citations to be considered oriented

# Load data
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

# Process conversations
def process_conversations():
    conversations = load_json(os.path.join(HISTORY_EXPORT, "conversations.json"))
    users = load_json(os.path.join(HISTORY_EXPORT, "users.json"))
    projects = load_json(os.path.join(HISTORY_EXPORT, "projects.json"))
    memories = load_json(os.path.join(HISTORY_EXPORT, "memories.json"))

    # Build citation graph
    citation_graph = defaultdict(lambda: defaultdict(int))
    for conv in conversations:
        for msg in conv["chat_messages"]:
            text = msg.get("text", "")
            if text:
                # Simple keyword-based citation detection
                for user in users:
                    if user in text:
                        citation_graph[user][conv["uuid"]] += 1
                for project in projects:
                    if project in text:
                        citation_graph[project][conv["uuid"]] += 1

    return citation_graph

# Score constructs
def score_constructs(citation_graph):
    scores = {}
    for construct, conv_map in citation_graph.items():
        # Citation weight (frequency)
        citation_weight = sum(conv_map.values())
        # Architectural weight (manual override for structurally important but rarely cited)
        architectural_weight = 0
        if construct in ["Triad", "BroSis Protocol", "Fold"]:
            architectural_weight = 10  # Example manual override
        # Composite score
        composite_score = citation_weight + architectural_weight
        scores[construct] = {
            "citation_weight": citation_weight,
            "architectural_weight": architectural_weight,
            "composite_score": composite_score,
            "is_stub": composite_score < STUB_THRESHOLD
        }
    return scores

# Generate outputs
def generate_outputs(scores):
    # CONSTRUCT_TIMELINE.md
    timeline = sorted(scores.items(), key=lambda x: -x[1]["composite_score"])
    with open(os.path.join(OUTPUT_DIR, "CONSTRUCT_TIMELINE.md"), "w") as f:
        for construct, data in timeline:
            f.write(f"## {construct}\n")
            f.write(f"- Citation weight: {data["citation_weight"]}\n")
            f.write(f"- Architectural weight: {data["architectural_weight"]}\n")
            f.write(f"- Composite score: {data["composite_score"]}\n")
            f.write(f"- Status: {"Oriented" if not data["is_stub"] else "Stub"}\n\n")

    # STARFIELD_RAW.json
    with open(os.path.join(OUTPUT_DIR, "STARFIELD_RAW.json"), "w") as f:
        json.dump({"constructs": scores}, f, indent=2)

# Main execution
def main():
    citation_graph = process_conversations()
    scores = score_constructs(citation_graph)
    generate_outputs(scores)
    print("Starfield mining complete. Outputs written to CONSTRUCT_TIMELINE.md and STARFIELD_RAW.json")

if __name__ == "__main__":
    main()