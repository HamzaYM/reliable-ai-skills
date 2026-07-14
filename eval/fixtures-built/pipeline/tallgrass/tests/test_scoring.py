from pipeline.scoring import score_document


def test_scores_recent_documents():
    for doc_id in ["doc-5", "doc-6", "doc-7"]:
        result = score_document(doc_id, f"body of {doc_id}")
        assert "score" in result
