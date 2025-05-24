import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain.retrievers.multi_query import MultiQueryRetriever
from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 30

# ========== 4. CRIAR EMBEDDINGS E VETORIZAR ==========
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={'k': TOP_K})


# ========== 4. CRIAR MODEL LLM ==========

llm =  ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    temperature=0.0
    # other params...
)

multi_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever, llm=llm,
)
question ="Qual valor dos modelos o3 mini 2025-01-31 Global e o1 2024-12-17 US/EU – Data Zones?"

docs = multi_retriever.get_relevant_documents(question)
docs2 = retriever.get_relevant_documents(question)
print(len(docs))
print(len(docs2))

# ========== 6. FAZER UMA PERGUNTA ==========
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=multi_retriever,
    return_source_documents=False
)

resultado = rag_chain({"query": question})

# Exibir a resposta gerada baseada exclusivamente nos dados recuperados.
print(resultado["result"])
