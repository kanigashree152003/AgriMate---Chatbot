import os

def retrieve_context(query):
    base_path = os.path.dirname(__file__)
    kb_path = os.path.join(base_path, "knowledge_base")

    context = ""
    for file in os.listdir(kb_path):
        with open(os.path.join(kb_path, file), 'r', encoding='utf-8') as f:
            context += f.read().lower()

    results = []
    for line in context.split('\n'):
        if any(word in line for word in query.lower().split()):
            results.append(line)
    return " ".join(results[:5])  # Top 5 matches

