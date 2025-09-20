# src/services/pdfManager.py
import os
import pdfplumber
from src.utils.logger import get_logger

logger = get_logger("PDFManager")

class PDFManager:
    def __init__(self, pasta_pdfs: str):
        self.documentos = {}  # {nome_arquivo: texto}
        logger.info(f"Iniciando o carregamento de PDFs da pasta: {pasta_pdfs}")
        self.carregar_pasta(pasta_pdfs)

    def carregar_pasta(self, pasta: str):
        """Carrega todos os PDFs da pasta."""
        if not os.path.exists(pasta) or not os.path.isdir(pasta):
            logger.warning(f"A pasta de PDFs '{pasta}' não foi encontrada ou não é um diretório.")
            return

        arquivos_pdf = [f for f in os.listdir(pasta) if f.lower().endswith(".pdf")]
        if not arquivos_pdf:
            logger.warning(f"Nenhum arquivo PDF encontrado na pasta '{pasta}'.")
            return

        for arquivo in arquivos_pdf:
            caminho_completo = os.path.join(pasta, arquivo)
            self.carregar_pdf(caminho_completo, nome=arquivo)
        
        logger.info(f"{len(self.documentos)} PDF(s) carregados com sucesso.")

    def carregar_pdf(self, caminho_arquivo: str, nome: str = None):
        """Carrega um único PDF e armazena seu texto."""
        try:
            texto = ""
            with pdfplumber.open(caminho_arquivo) as pdf:
                for pagina in pdf.pages:
                    pagina_texto = pagina.extract_text()
                    if pagina_texto:
                        texto += pagina_texto + "\n"
            
            chave = nome or os.path.basename(caminho_arquivo)
            self.documentos[chave] = texto
            logger.debug(f"PDF '{chave}' carregado.")
        except Exception as e:
            logger.error(f"Falha ao carregar o PDF '{caminho_arquivo}': {e}", exc_info=True)

    def get_texto(self, nome: str) -> str:
        """Retorna o texto completo do PDF."""
        return self.documentos.get(nome, "")