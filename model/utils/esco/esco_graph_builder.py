import csv
import json
import networkx as nx


def load_esco_graph(skills_file, hierarchy_file, relations_file):
    G = nx.DiGraph()

    print("Loading skills...")

    # ----------------------------
    # 1. Load SKILLS (nodes)
    # ----------------------------
    with open(skills_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sid = r["conceptUri"].strip()

            alt = r["altLabels"].split("|") if r["altLabels"] else []

            G.add_node(
                sid,
                name=r["preferredLabel"],
                alt=alt,
                description=r["description"],
                type=r["skillType"]
            )

    print("Skills loaded:", len(G.nodes))

    # ----------------------------
    # 2. Build hierarchy edges
    # ----------------------------
    print("Building hierarchy edges...")

    with open(hierarchy_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            level0 = row["Level 0 URI"].strip()
            level1 = row["Level 1 URI"].strip()
            level2 = row["Level 2 URI"].strip()
            level3 = row["Level 3 URI"].strip()

            # Level 1 → Level 0
            if level1 and level0 and level1 in G.nodes and level0 in G.nodes:
                G.add_edge(level1, level0, relation="is_child_of")

            # Level 2 → Level 1
            if level2 and level1 and level2 in G.nodes and level1 in G.nodes:
                G.add_edge(level2, level1, relation="is_child_of")

            # Level 3 → Level 2
            if level3 and level2 and level3 in G.nodes and level2 in G.nodes:
                G.add_edge(level3, level2, relation="is_child_of")

    print("Hierarchy edges added.")

    # ----------------------------
    # 3. Add RELATED skill relations
    # ----------------------------
    print("Adding related skill edges...")

    with open(relations_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for r in reader:
            a = r["originalSkillUri"].strip()
            b = r["relatedSkillUri"].strip()
            rel = r["relationType"]

            if a in G.nodes and b in G.nodes:
                G.add_edge(a, b, relation=rel)

    print("Related edges added.")

    return G


if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    skills_csv = os.path.join(base_dir, "skills_en.csv")
    hierarchy_csv = os.path.join(base_dir, "skillsHierarchy_en.csv")
    relations_csv = os.path.join(base_dir, "skillSkillRelations_en.csv")

    print("Building ESCO Skill Graph...")

    graph = load_esco_graph(skills_csv, hierarchy_csv, relations_csv)

    print("Total nodes:", len(graph.nodes))
    print("Total edges:", len(graph.edges))

    # Save graph to JSON
    output_path = os.path.join(base_dir, "esco_skill_graph.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nx.node_link_data(graph), f, ensure_ascii=False, indent=2)

    print("Graph saved as esco_skill_graph.json")
