import csv
import os

BASE_PATH = os.path.join("utils", "esco")

files = [
    "skills_en.csv",
    "skillsHierarchy_en.csv",
    "skillSkillRelations_en.csv"
]

for file in files:
    file_path = os.path.join(BASE_PATH, file)
    print("\n---", file, "---")
    
    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        print(header)
