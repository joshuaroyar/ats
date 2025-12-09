# domain_noun_builder.py
"""
Builds domain-specific noun banks (1000 nouns per domain)
using WordNet noun list + semantic similarity + seed nouns.
"""

import json
import sys
from collections import OrderedDict
from nltk.corpus import wordnet as wn
from linguistic_engine import build_linguistic_resources


# -----------------------
# DOMAIN SEED NOUNS
# -----------------------
DOMAIN_NOUN_SEEDS = OrderedDict([
    ("tech", [
        "algorithm", "model", "dataset", "pipeline", "api", "framework", "server", "database",
        "architecture", "codebase", "inference", "accuracy", "latency", "feature"
    ]),
    ("business", [
        "strategy", "stakeholder", "kpi", "revenue", "client", "market", "plan", "team",
        "performance", "objective", "initiative", "management"
    ]),
    ("marketing", [
        "campaign", "brand", "audience", "content", "engagement", "traffic", "conversion",
        "impression", "reach", "lead"
    ]),
    ("finance", [
        "budget", "audit", "tax", "forecast", "valuation", "ledger", "expense", "invoice",
        "asset", "liability", "revenue", "profit"
    ]),
    ("operations", [
        "logistics", "inventory", "workflow", "supply", "process", "efficiency",
        "procurement", "compliance", "quality"
    ]),
    ("hr", [
        "employee", "recruitment", "onboarding", "talent", "training", "candidate",
        "payroll", "interview", "assessment"
    ]),
    ("design", [
        "prototype", "wireframe", "mockup", "layout", "interface", "typography",
        "illustration", "animation", "palette"
    ])
])


# -----------------------
# Helpers
# -----------------------
def wn_similarity(n1, seed_synsets):
    best = 0.0
    syns = wn.synsets(n1, pos=wn.NOUN)
    if not syns:
        return 0.0
    for s1 in syns:
        for s2 in seed_synsets:
            try:
                sim = s1.path_similarity(s2)
            except:
                sim = None
            if sim and sim > best:
                best = sim
    return best or 0.0


def prepare_seed_synsets(seed_list):
    all_syns = []
    for w in seed_list:
        syns = wn.synsets(w, pos=wn.NOUN)
        all_syns.extend(syns)
    return all_syns


# -----------------------
# Main function
# -----------------------
def build_domain_noun_banks(target_per_domain=1000):

    print("Loading linguistic resources...")
    data = build_linguistic_resources()
    all_nouns = [n for n in data["nouns"] if n.isalpha()]

    domain_seed_synsets = {
        d: prepare_seed_synsets(seeds)
        for d, seeds in DOMAIN_NOUN_SEEDS.items()
    }

    # scoring
    domain_scores = {d: [] for d in DOMAIN_NOUN_SEEDS}

    print("Scoring nouns per domain...")
    for noun in all_nouns:
        for d, seeds in DOMAIN_NOUN_SEEDS.items():

            score = 0.0

            # substring match bonus
            for s in seeds:
                if s in noun and len(s) >= 4:
                    score += 1.0
                    break

            # semantic similarity score (0-1 scaled to 0-2)
            wn_sim = wn_similarity(noun, domain_seed_synsets[d])
            score += (wn_sim * 2.0)

            # prefix/suffix small signals
            suffixes = ["ion", "ity", "ment"]
            if any(noun.endswith(sfx) for sfx in suffixes):
                score += 0.1

            domain_scores[d].append((noun, score))

    # selecting top nouns per domain
    domain_selected = {}
    for d, lst in domain_scores.items():
        lst.sort(key=lambda x: (-x[1], x[0]))
        selected = [n for n, s in lst[:target_per_domain]]
        domain_selected[d] = selected

        # save JSON
        fname = f"{d}_nouns.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(selected, f, indent=2)
        print(f"Saved {len(selected)} nouns → {fname}")

    print("Done building noun banks.")
    return domain_selected


if __name__ == "__main__":
    target = 1000
    if len(sys.argv) > 1:
        target = int(sys.argv[1])
    build_domain_noun_banks(target)
