import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/huggingface_transformers";
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { ChatGroq } from "@langchain/groq";
import { MultiQueryRetriever } from "langchain/retrievers/multi_query";
import { createRetrievalChain } from "langchain/chains/retrieval";
import { createStuffDocumentsChain } from "langchain/chains/combine_documents";
import { ChatPromptTemplate, PromptTemplate } from "@langchain/core/prompts";
import { VectorStoreRetriever } from "@langchain/core/vectorstores";
import { AIMessage, HumanMessage } from "@langchain/core/messages";
import { Message } from "~/types/ChatMessages";

const GEN_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct";
const GROQ_KEY = process.env.GROQ_API_KEY;
const EMBED_MODEL_ID = "Xenova/all-MiniLM-L6-v2";
const TOP_K = 30;

class RagService {
  embeddings = new HuggingFaceTransformersEmbeddings({
    model: EMBED_MODEL_ID,
  });

  private vectorstore: Chroma | undefined;

  private retriever: VectorStoreRetriever | undefined;

  private llm = new ChatGroq({
    model: GEN_MODEL_ID,
    temperature: 0.0,
    apiKey: GROQ_KEY,

  });

  private multiRetriever: MultiQueryRetriever | undefined;

  constructor() {
    Chroma.fromExistingCollection(this.embeddings, {
      url: "http://localhost:8000",
      collectionName: "langchain"
    }).then((vectorstore) => {
      this.vectorstore = vectorstore;
      this.retriever = this.vectorstore.asRetriever({ k: TOP_K });
      this.multiRetriever = MultiQueryRetriever.fromLLM({
        retriever: this.retriever,
        llm: this.llm,
        prompt: ChatPromptTemplate.fromTemplate(
          `You are an AI language model assistant. Your task is 
            to generate 3 different versions of the given user 
            question to retrieve relevant documents from a vector  database. 
            By generating multiple perspectives on the user question, 
            your goal is to help the user overcome some of the limitations 
            of distance-based similarity search. Provide these alternative 
            questions separated by newlines. Original question: {question}`
        )
      });
    });
  }


  async invoke(question: string, chat_history: Message[] = []) {

    const prompt = new PromptTemplate({
      template: ` 
      Você é um consultor de valores de LLM da Google e Azure. Use as informações abaixo para responder à pergunta do usuário.

      Se o contexto não for útil ou estiver fora do assunto, responda apenas com base no histórico da conversa.

      === Histórico da conversa ===
      {chat_history}

      === Pergunta do usuário ===
      {input}

      === Contexto recuperado da base de conhecimento ===
      {context}

      === Resposta do assistente ===`,
      inputVariables: ["chat_history", "input", "context"],
    });


    const combineDocsChain = await createStuffDocumentsChain({
      llm: this.llm,
      prompt,
    });


    if (!this.multiRetriever) {
      throw new Error("MultiRetriever is not initialized");
    }

    const ragChain = await createRetrievalChain({
      combineDocsChain: combineDocsChain,
      retriever: this.multiRetriever,
    });

    let chatHistory = chat_history.filter(message => message.success).map((message) => {
      if (message.role === "USER") {
        return new HumanMessage(message.content);
      } else {
        return new AIMessage(message.content);
      }
    })

    const result = await ragChain.invoke({ input: question, chat_history: chatHistory });
    return result

  }
}


export default new RagService()








