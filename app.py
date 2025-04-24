import streamlit as st
import requests

# Set up page configuration
st.set_page_config(page_title="AskPolicy Assistant", layout="centered")

st.title("📄 AskPolicy - GN Policy Assistant")
st.subheader("Ask a policy-related question:")

# Input field for question
question = st.text_input("Your question", placeholder="e.g., Can a paramedic suture?")

# Button to send question
if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                # Send question to FastAPI backend through ngrok
                response = requests.post(
                    "https://8811-2001-56a-7146-b00-2154-a076-37f2-6be7.ngrok-free.app/ask",
                    json={"question": question},
                    timeout=30
                )

                # Display result
                if response.status_code == 200:
                    st.success("Answer:")
                    st.write(response.json()["answer"])
                else:
                    st.error(f"Server returned {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
