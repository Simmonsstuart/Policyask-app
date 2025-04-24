# cli_assistant.py — Ask policy questions in terminal

from policy_core import load_index, ask_question
from datetime import datetime

# Load the policy index
index = load_index("faiss_policy_index")

# Ask your question
question = input("Ask your question about a policy:\n> ")
response = ask_question(index, question)

# Show the AI's answer
print("\n🔍 Answer:")
print(response["result"])

# Show sources used
print("\n📄 Sources:")
for doc in response["source_documents"]:
    meta = doc.metadata
    title = meta.get("policy_name", "Unknown")
    number = meta.get("policy_number", "Unnumbered")
    review_due = meta.get("review_due_date", "").strip()

    try:
        review_date = datetime.strptime(review_due, "%B %d, %Y").date()
        overdue = review_date < datetime.today().date()
        review_note = f"❗ {review_due} (OVERDUE)" if overdue else f"✔️ {review_due}"
    except:
        review_note = f"⚠️ {review_due or 'Not Set'}"

    print(f"- {number} | {title}")
    print(f"  Review: {review_note}")
