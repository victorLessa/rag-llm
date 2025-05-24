import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from pathlib import Path
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_docling.loader import ExportType
from WebLoader import JSWebLoader
import shutil
from dotenv import load_dotenv


load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
EXPORT_TYPE = ExportType.DOC_CHUNKS

# ========== 1. CONFIGURAR LLM (Groq com LLaMA 3) ==========
llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct")

if Path("./chroma_db").exists():
    shutil.rmtree("./chroma_db")
   
loader = JSWebLoader([
    "https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/",
    "https://cloud.google.com/vertex-ai/generative-ai/pricing?hl=pt-br"
])
docs = loader.load_html_per_docs()


# with open("pagina0.txt", "w", encoding="utf-8") as f:
#     f.write(docs[0].page_content)
# with open("pagina1.txt", "w", encoding="utf-8") as f:
#     f.write(docs[1].page_content)

#========== 3. DIVIDIR EM CHUNKS ==========
splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50)
splits = splitter.split_documents(docs)

# ========== 4. CRIAR EMBEDDINGS E VETORIZAR ==========

embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)


# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(documents=splits, embedding=embedding, persist_directory="./chroma_db")


