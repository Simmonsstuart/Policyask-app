from policy_ai_setup import load_index, ask_question
from datetime import datetime

# Load the index
index = load_index("faiss_policy_index")

# Ask a question
question = input("Ask your question about a policy: ")
response = ask_question(index, question)

# Show the answer
print("\nAnswer:")
print(response["result"])

# Show the sources
print("\nSources:")
for doc in response["source_documents"]:
    meta = doc.metadata
    title = meta.get("doc_title", "Unknown")
    pages = meta.get("pages", "?")
    version = meta.get("version_date", "Unknown")
    review_due = meta.get("review_due", "").strip()

    # Determine review status
    if review_due:
        try:
            review_date = datetime.strptime(review_due, "%Y-%m-%d").date()
            if review_date < datetime.today().date():
                review_note = f"❗ {review_due} (OVERDUE)"
            else:
                review_note = f"✔️ {review_due}"
        except ValueError:
            review_note = f"⚠️ Invalid format ({review_due})"
    else:
        review_note = "⚠️ Not Set"

    # Display the source info
    print(f"- {title} – pages {pages}")
    print(f"  Published: {version}")
    print(f"  Review: {review_note}")
