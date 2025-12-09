# domain_verb_builder.py
"""
Domain Verb Builder
-------------------
Usage:
    python domain_verb_builder.py            # builds 1000 verbs per domain by default
    python domain_verb_builder.py 1500       # build 1500 verbs per domain

Requirements:
- linguistic_engine.py in same folder (it must implement build_linguistic_resources())
- NLTK WordNet and VerbNet downloaded:
    python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('verbnet')"

Output:
- <domain>_verbs.json files (one per domain) in current directory.
"""

import json
import math
import sys
from collections import defaultdict, OrderedDict
from nltk.corpus import wordnet as wn
from linguistic_engine import build_linguistic_resources

# -----------------------
# Domain seeds (curated)
# -----------------------
DOMAIN_SEEDS = OrderedDict([
    ("tech", [
        "code", "develop", "deploy", "debug", "optimize", "train", "model", "compile",
        "integrate", "automate", "orchestrate", "scale", "engineer", "refactor", "test",
        "monitor", "provision", "provision", "containerize", "benchmark", "profile"
    ]),
    ("business", [
        "lead", "manage", "plan", "strategize", "coordinate", "organize", "forecast",
        "drive", "grow", "negotiate", "implement", "prioritize", "budget", "align", "execute"
    ]),
    ("marketing", [
        "promote", "advertise", "brand", "launch", "engage", "optimize", "segment",
        "convert", "target", "position", "campaign", "measure", "amplify", "curate"
    ]),
    ("finance", [
        "audit", "budget", "forecast", "reconcile", "price", "value", "hedge", "invest",
        "invoice", "account", "calculate", "report", "project", "fund"
    ]),
    ("operations", [
        "streamline", "procure", "schedule", "optimize", "supply", "logistics", "control",
        "operate", "maintain", "inspect", "dispatch", "standardize", "improve", "execute"
    ]),
    ("hr", [
        "recruit", "onboard", "train", "hire", "coach", "mentor", "evaluate", "assess",
        "screen", "interview", "facilitate", "retain", "compensate", "reward"
    ]),
    ("design", [
        "design", "prototype", "sketch", "mockup", "wireframe", "visualize", "illustrate",
        "iterate", "compose", "render", "refine", "layout", "style", "test"
    ])
])

# -----------------------
# Helper functions
# -----------------------
def wn_best_similarity(verb, seed_synsets):
    """
    Compute best path_similarity score between any synset of `verb`
    and any synset in seed_synsets (list of synsets).
    Returns a float in [0,1] or 0 if no similarity.
    """
    best = 0.0
    try:
        v_syns = wn.synsets(verb, pos=wn.VERB)
    except Exception:
        v_syns = []
    if not v_syns:
        return 0.0
    for vs in v_syns:
        for s in seed_synsets:
            try:
                sim = vs.path_similarity(s)
            except Exception:
                sim = None
            if sim:
                if sim > best:
                    best = sim
    return best or 0.0

def prepare_seed_synsets(seeds):
    """Return list of WordNet synsets (verbs) for seed words."""
    synsets = []
    for s in seeds:
        ss = wn.synsets(s, pos=wn.VERB)
        if ss:
            synsets.extend(ss)
    return synsets

def score_verb_for_domain(verb, domain_seeds_synsets, seed_tokens):
    """
    Scoring heuristic (deterministic):
      - substring match (seed in verb) -> +1.0
      - exact seed equality -> +1.2
      - WordNet best similarity scaled (0..1) -> up to +2.0
      - small bonus if verb shares prefix/suffix form -> +0.2
    Higher score = more relevant.
    """
    v = verb.lower()
    score = 0.0

    # exact equality to any seed
    if v in seed_tokens:
        score += 1.2

    # substring match: seed appears in verb (e.g., 'deploy' in 're-deploy')
    for tok in seed_tokens:
        if tok in v and len(tok) >= 3:
            score += 1.0
            break

    # semantic similarity using WordNet path_similarity
    wn_sim = wn_best_similarity(v, domain_seeds_synsets)
    # scale semantic sim to up to 2.0
    score += wn_sim * 2.0

    # morphological heuristic: common verb prefixes/suffixes
    prefixes = ("re","un","de","co","in","inter","pre","post","auto","multi")
    suffixes = ("ize","ise","ed","ing")
    for p in prefixes:
        if v.startswith(p) and len(v) > len(p) + 2:
            score += 0.05
            break
    for sfx in suffixes:
        if v.endswith(sfx) and len(v) > len(sfx) + 2:
            score += 0.03
            break

    return round(score, 6)


# -----------------------
# Main builder
# -----------------------
def build_domain_verb_banks(target_per_domain=1000, verbose=True):
    data = build_linguistic_resources()
    all_verbs = data["verbs"]  # merged verbs from linguistic_engine
    all_verbs = [v for v in all_verbs if v.isalpha()]  # only alpha tokens

    # Precompute VerbNet membership map (classids -> lemmas)
    # We use membership as a tiny relevance signal: if a domain seed word appears in VerbNet class lemmas, give tiny bump.
    try:
        from nltk.corpus import verbnet as vn
        vn_class_map = {}
        for cid in vn.classids():
            lemmas = [m.lower() for m in vn.lemmas(cid)]
            for lm in lemmas:
                vn_class_map.setdefault(lm, set()).add(cid)
    except Exception:
        vn_class_map = {}

    # Prepare domain seed synsets and seed token set
    domain_seed_synsets = {}
    domain_seed_tokens = {}
    for d, seeds in DOMAIN_SEEDS.items():
        domain_seed_synsets[d] = prepare_seed_synsets(seeds)
        domain_seed_tokens[d] = set(s.lower() for s in seeds)

    # Score every verb for every domain
    domain_scores = {d: [] for d in DOMAIN_SEEDS}
    # deterministic iteration order
    for verb in all_verbs:
        for d in DOMAIN_SEEDS:
            score = score_verb_for_domain(verb, domain_seed_synsets[d], domain_seed_tokens[d])
            # tiny bonus if verb exists in VerbNet lemmas map (implies professional action verb)
            if verb in vn_class_map:
                score += 0.15
            domain_scores[d].append((verb, score))

    # For each domain, sort verbs by score desc then alphabetically to keep deterministic tie-break
    domain_selected = {}
    for d, scored_list in domain_scores.items():
        # filter out near-zero scores first (keep only > 0)
        filtered = [t for t in scored_list if t[1] > 0.0]
        # If filtered is empty fallback to whole list
        if not filtered:
            filtered = scored_list[:]
        # sort (score desc, verb asc)
        filtered.sort(key=lambda x: (-x[1], x[0]))
        # pick top N (or pad deterministically with alphabetic verbs if needed)
        top = [v for v, s in filtered[:target_per_domain]]
        if len(top) < target_per_domain:
            # deterministic padding: use alphabetic order of remaining verbs not already chosen
            remaining = [v for v in all_verbs if v not in top]
            remaining.sort()
            needed = target_per_domain - len(top)
            top.extend(remaining[:needed])
        domain_selected[d] = top

    # Save per-domain JSON files
    for d, verbs in domain_selected.items():
        fname = f"{d}_verbs.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(verbs, f, indent=2, ensure_ascii=False)
        if verbose:
            print(f"Saved {len(verbs)} verbs to {fname}")

    return domain_selected


if __name__ == "__main__":
    target = 1000
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except:
            pass
    print("Building domain verb banks; target per domain:", target)
    banks = build_domain_verb_banks(target_per_domain=target, verbose=True)
    print("Done.")
