# linguistic_engine.py
# Clean final version using WordNet + VerbNet

from nltk.corpus import wordnet as wn
from nltk.corpus import verbnet


def get_wordnet_verbs():
    verbs = set()
    for syn in wn.all_synsets(pos=wn.VERB):
        for lemma in syn.lemmas():
            word = lemma.name().replace("_", " ").lower()
            if word.isalpha():
                verbs.add(word)
    return sorted(verbs)


def get_wordnet_nouns():
    nouns = set()
    for syn in wn.all_synsets(pos=wn.NOUN):
        for lemma in syn.lemmas():
            word = lemma.name().replace("_", " ").lower()
            if word.isalpha():
                nouns.add(word)
    return sorted(nouns)


def get_verbnet_verbs():
    verbs = set()
    for cls in verbnet.classids():
        members = verbnet.lemmas(cls)
        for v in members:
            v = v.lower()
            if v.isalpha():
                verbs.add(v)
    return sorted(verbs)


def build_linguistic_resources():
    print("Loading WordNet verbs...")
    wn_verbs = get_wordnet_verbs()

    print("Loading VerbNet verbs...")
    vn_verbs = get_verbnet_verbs()

    print("Loading WordNet nouns...")
    wn_nouns = get_wordnet_nouns()

    print("\nMerging resources...")

    all_verbs = sorted(set(wn_verbs + vn_verbs))
    all_nouns = wn_nouns  # nouns only from WordNet

    print("\n--- Summary ---")
    print("WordNet verbs:", len(wn_verbs))
    print("VerbNet verbs:", len(vn_verbs))
    print("Merged verbs:", len(all_verbs))
    print("Total nouns:", len(all_nouns))

    return {
        "verbs": all_verbs,
        "nouns": all_nouns
    }


if __name__ == "__main__":
    data = build_linguistic_resources()
