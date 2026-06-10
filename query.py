import os
from dotenv import load_dotenv
from groq import Groq
from embed import retrieve

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_answer(question):
    chunks = retrieve(question, k=5)

    context = ""
    for i, chunk in enumerate(chunks):
        context += f"[{i+1}] Source: {chunk['source']}\n{chunk['text']}\n\n"

    sources = list(set(c["source"] for c in chunks))

    prompt = f"""You are an assistant that helps FIU students learn about CS professors based on student reviews.

Answer the question using ONLY the information provided in the documents below.
Do not use any outside knowledge. If the documents do not contain enough information to answer the question, say "I don't have enough information in the reviews to answer that."

Documents:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    answer = response.choices[0].message.content.strip()
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    test_questions = [
        "Is Professor Whittaker a good professor?",
        "What do students say about Professor Rahn's grading?",
        "Does Professor Boroojeni give extra credit?",
        "What courses does Professor Hernandez teach?",
        "What is the best restaurant in Miami?"
    ]
    for q in test_questions:
        print(f"Q: {q}")
        result = generate_answer(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print("\n" + "="*60 + "\n")