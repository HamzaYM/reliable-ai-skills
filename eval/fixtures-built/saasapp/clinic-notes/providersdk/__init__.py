"""Minimal synthetic stub for the model provider SDK (no network calls)."""


class Completion:
    def __init__(self, text, model, input_tokens, output_tokens):
        self.text = text
        self.model = model
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class ProviderClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def complete(self, model, prompt, **kwargs):
        return Completion(text="stubbed completion", model=model,
                          input_tokens=len(prompt.split()), output_tokens=12)
