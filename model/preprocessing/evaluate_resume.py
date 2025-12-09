import json
from utils.pdf_reader import extract_text_from_pdf
from utils.extraction.skill_extractor import extract_candidates
from core.ontology.map_to_ontology import map_to_esco


def evaluate_resume(pdf_path):

    # STEP 0: extract text from PDF
    text = extract_text_from_pdf(pdf_path)

    # STEP 1: deterministic skill phrase extraction
    candidates = extract_candidates(text)

    mapped = []
    for c in candidates:
        m = map_to_esco(c)
        if m:
            mapped.append(m)

    return mapped


if __name__ == "__main__":
    pdf_path = "resume.pdf"    # change to your actual PDF

    result = evaluate_resume(pdf_path)

    print(json.dumps(result, indent=2))
