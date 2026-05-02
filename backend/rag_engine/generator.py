from rag_engine.retriever import retrieve_context
from transformers import pipeline
from deep_translator import GoogleTranslator

# Initialize model (Flan-T5 is a lightweight, open LLM)
summarizer = pipeline("text2text-generation", model="google/flan-t5-small")

def generate_response(query, user_lang='en'):
    """
    Generates a context-aware response using RAG + translation.
    query: user question (string)
    user_lang: 'en' for English, 'ta' for Tamil
    """

    # 1️⃣ Translate query to English if user asked in Tamil
    if user_lang == 'ta':
        query_en = GoogleTranslator(source='ta', target='en').translate(query)
    else:
        query_en = query

    # 2️⃣ Retrieve relevant text from knowledge base
    context = retrieve_context(query_en)

    # 3️⃣ Generate response using LLM
    input_text = f"Context: {context}\n\nQuestion: {query_en}\nAnswer:"
    output = summarizer(input_text, max_length=120, do_sample=False)
    answer_en = output[0]['generated_text']

    # 4️⃣ Translate back to Tamil if needed
    if user_lang == 'ta':
        answer_ta = GoogleTranslator(source='en', target='ta').translate(answer_en)
        return answer_ta

    return answer_en

