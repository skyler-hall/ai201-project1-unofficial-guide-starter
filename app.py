import gradio as gr
from query import generate_answer

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    result = generate_answer(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="FIU CS Professor Guide") as demo:
    gr.Markdown("# FIU CS Unofficial Professor Guide")
    gr.Markdown("Ask anything about FIU Computer Science professors based on real student reviews.")

    inp = gr.Textbox(label="Your question", placeholder="e.g. Is Professor Whittaker a good professor?")
    btn = gr.Button("Ask")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()