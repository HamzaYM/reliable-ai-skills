from pipeline.llm.router import call_with_fallback


def test_success_path_uses_primary():
    out = call_with_fallback({"text": "sample"})
    assert out["vendor"] == "primary"
