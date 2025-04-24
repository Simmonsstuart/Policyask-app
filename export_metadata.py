# export_metadata.py — Export FAISS metadata to CSV

import csv
from collections import defaultdict
from policy_core import load_index

index = load_index("faiss_policy_index")

# Collect metadata grouped by source
grouped = defaultdict(dict)

for doc in index.docstore._dict.values():
    meta = doc.metadata
    filename = meta.get("source", "Unknown")

    grouped[filename].update({
        "Filename": filename,
        "Policy Number": meta.get("policy_number", "Unnumbered"),
        "Policy Name": meta.get("policy_name", "Unknown"),
        "Effective Date": meta.get("effective_date", "Unknown"),
        "Review Due Date": meta.get("review_due_date", "Unknown"),
        "Document Type": meta.get("document_type", "Unknown"),
    })

# Write to CSV
with open("policy_metadata_export.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Filename", "Policy Number", "Policy Name", "Effective Date", "Review Due Date", "Document Type"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for record in grouped.values():
        writer.writerow(record)

print("✅ Export complete: policy_metadata_export.csv")
