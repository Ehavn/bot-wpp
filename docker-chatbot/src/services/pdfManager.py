import os
import pdfplumber

class PDFManager:
    def __init__(self, pasta_pdfs: str):
        self.documentos = {}  # {nome_arquivo: texto}
        self.carregar_pasta(pasta_pdfs)

    def carregar_pasta(self, pasta: str):
        """Carrega todos os PDFs da pasta."""
        if not os.path.exists(pasta):
            raise ValueError(f"Pasta não encontrada: {pasta}")
        
        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]
        if not arquivos:
            print("⚠️ Nenhum PDF encontrado na pasta.")
            return

        for arquivo in arquivos:
            caminho_completo = os.path.join(pasta, arquivo)
            self.carregar_pdf(caminho_completo, nome=arquivo)

    def carregar_pdf(self, caminho_arquivo: str, nome: str = None):
        """Carrega PDF e armazena o texto."""
        texto = ""
        with pdfplumber.open(caminho_arquivo) as pdf:
            for pagina in pdf.pages:
                pagina_texto = pagina.extract_text()
                if pagina_texto:
                    texto += pagina_texto + "\n"
        chave = nome or caminho_arquivo
        self.documentos[chave] = texto

    def get_texto(self, nome: str):
        """Retorna o texto completo do PDF."""
        return self.documentos.get(nome, "")

    def get_resumo(self, nome: str, max_chars=3000):
        """Retorna apenas os primeiros N caracteres do PDF."""
        texto = self.get_texto(nome)
        return texto[:max_chars]