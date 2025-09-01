<<<<<<< HEAD
import re

class Sanitizer:
    def __init__(self):
        self.patterns = {
            "cpf": re.compile(r'\b\d{4,11}\b'),  # pega CPFs escritos de forma errada
            "email": re.compile(r'\b[\w.-]+@[\w.-]+\.\w{2,}\b'),
            "phone": re.compile(r'\b\d{2,3}-?\d{4,5}-?\d{4}\b')
        }

    def sanitize(self, text: str) -> str:
        for key, pattern in self.patterns.items():
            text = pattern.sub("***MASKED***", text)
        return text
=======
import re

class Sanitizer:
    def __init__(self):
        self.patterns = {
            "cpf": re.compile(r'\b\d{4,11}\b'),  # pega CPFs escritos de forma errada
            "email": re.compile(r'\b[\w.-]+@[\w.-]+\.\w{2,}\b'),
            "phone": re.compile(r'\b\d{2,3}-?\d{4,5}-?\d{4}\b')
        }

    def sanitize(self, text: str) -> str:
        for key, pattern in self.patterns.items():
            text = pattern.sub("***MASKED***", text)
        return text
>>>>>>> cccf66339631c294e783b616174331c055f49216
