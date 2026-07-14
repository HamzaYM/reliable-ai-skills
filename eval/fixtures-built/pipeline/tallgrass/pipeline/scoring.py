"""Document scoring."""
from pipeline import model_client


def score_document(doc_id, text):
    prompt = f"Score this document for completeness: {text}"
    return model_client.complete(prompt, doc_id=doc_id)
