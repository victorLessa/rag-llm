from playwright.sync_api import sync_playwright
from langchain.schema import Document
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
import json
from unstructured.partition.html import partition_html
from docling.datamodel.document import InputDocument
from io import BytesIO
from docling.datamodel.base_models import InputFormat
from docling.backend.html_backend import HTMLDocumentBackend
from langchain_community.document_loaders.base import BaseLoader

class JSWebLoader(BaseLoader):
    def __init__(self, urls: list[str]):
        self.urls = urls


    def extract_table_html(self, html):
      soup = BeautifulSoup(html, "html.parser")
      
      # Extração opcional de tabelas estruturadas
      tables = soup.find_all("table")
      
      table_texts = []


      for table in tables:
        df = pd.read_html(StringIO(str(table)))[0]
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        json_data = df.to_json(orient='records', force_ascii=False)
        
        lines = []
        for record in json.loads(json_data):
            line = []
            for key, value in record.items():
                line.append(f"{key}: {value}")
            lines.append(", ".join(line))
            
        table_texts.append(";\n".join(lines))
      return ";\n".join(table_texts)

    def load_unstructured(self) -> list[Document]:
        docs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            for url in self.urls:
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state("networkidle")  # Aguarda todos os requests
                html = page.content()
                
                readeable_text = self.extract_table_html(html)
                docs = [*docs, *self.html_to_node_unstructured(readeable_text)]

            browser.close()
        return docs
    
    def html_to_node_unstructured(self, html_text) -> list[Document]:
        global count_element
        elements = partition_html(text=html_text)

        # 2. Converter os elementos para objetos Document do LangChain
        docs = []
        for el in elements:
            text = el.text.strip()
            if text:
                count_element += 1
                metadata = {"type": el.category}
                docs.append(Document(page_content=text, metadata=metadata))
        
        return docs
    def load_tables_per_docs(self) -> list[Document]:
        docs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            for url in self.urls:
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state("networkidle")  # Aguarda todos os requests
                html = page.content()
                
                readeable_text = self.extract_table_html(html)

                doc = self.html_convert_html_to_doc(readeable_text)
                docs.append(doc)
            browser.close()
        return docs
    
    def html_convert_html_to_doc(self, html_text) -> Document:
        in_doc = InputDocument(
            path_or_stream=BytesIO(html_text.encode("utf-8")),
            format=InputFormat.HTML,
            backend=HTMLDocumentBackend,
            filename="duck.html",
        )
        backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=BytesIO(html_text.encode("utf-8")))
        dl_doc = backend.convert()

        return Document(page_content=dl_doc.export_to_markdown(), metadata={"source": 'docling'})

    def load_html_per_docs(self) -> list[Document]:
        docs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            texts = []
            for url in self.urls:
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state("networkidle")  # Aguarda todos os requests
                html = page.content()
                
                readeable_text = self.extract_table_html(html)
                texts.append(readeable_text)
            doc = Document(page_content=";\n".join(texts), metadata={"source": 'docling'})
            docs.append(doc)
            browser.close()
        return docs

    def extract_tables_to_doc(self, html) -> Document:
      soup = BeautifulSoup(html, "html.parser")

      # Extração opcional de tabelas estruturadas
      tables = soup.find_all("table")
      doc_tables = []
      for table in tables:
              doc_table = self.html_convert_html_to_doc(str(table))
              doc_tables.append(doc_table)
        
      return doc_tables

    def load_table_per_docs(self) -> list[Document]:
        docs = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            for url in self.urls:
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state("networkidle")  # Aguarda todos os requests
                html = page.content()
                docs = [*docs, *self.extract_tables_to_doc(html)]
                
            browser.close()
        return docs