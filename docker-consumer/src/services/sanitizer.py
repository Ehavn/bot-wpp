import re

class Sanitizer:
    def __init__(self):
        # Padrões de Regex aprimorados para maior precisão
        self.patterns = {
            "cpf": re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'),
            "email": re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'),
            "phone": re.compile(r'\b(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})-?\d{4}\b')
        }

    def sanitize(self, text: str) -> str:
        sanitized_text = text
        for key, pattern in self.patterns.items():
            sanitized_text = pattern.sub(f"***MASKED_{key.upper()}***", sanitized_text)
        return sanitized_text