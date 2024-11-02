from app.constants import *
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, format_document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap, RunnablePassthrough
from langserve.pydantic_v1 import BaseModel, Field
from operator import itemgetter
from typing import List, Tuple

#uncomment to see prompt and answer generation
import langchain
langchain.debug = True

#embedding model from local source
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"},
)

#prompt templates for organizing documents, context, and sources
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(REPHRASE_TEMPLATE)

ANSWER_PROMPT = PromptTemplate.from_template(ANSWER_TEMPLATE)

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

#setting up vectorstorage, retriever, and llm
vectordb = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model)
#setting up the retriever with specified number of sources to get
retriever = vectordb.as_retriever(search_kwargs={"k": NUM_SOURCES})

#creating the model with the given model name and maximum context length
llmInstruct = OllamaLLM(model=MODEL_NAME, temperature=0.8)
llmInstructRephrase = OllamaLLM(model=REPHRASE_MODEL_NAME, temperature=0)

#method to format documents, sources, and chunks
def _combine_documents(
    docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"
):
    """Combine documents into a single string."""
    print("\n\n\ngot the documents\n\n\n")
    print(docs)
    print("done\n")
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    sources = [doc.metadata['source'] for doc in docs]
    context = document_separator.join(doc_strings)
    return {"context": context, "sources": sources, "chunks": doc_strings}

#method to format the chat history from user input
def _format_chat_history(chat_history: List[Tuple]) -> str:
    """Format chat history into a string."""
    buffer = ""
    for dialogue_turn in chat_history:
        human = "Human: " + dialogue_turn[0]
        ai = "Assistant: " + dialogue_turn[1]
        buffer += "\n" + "\n".join([human, ai])
    return buffer

#class for user input for chain
class ChatHistory(BaseModel):
    """Chat history with the bot."""
    chat_history: List[Tuple[str, str]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "question"}},
    )
    question: str

#runnable to rephrase question based on chat history
_inputs = RunnableMap(
    standalone_question=RunnablePassthrough.assign(
        chat_history=lambda x: _format_chat_history(x["chat_history"])
    )
    | CONDENSE_QUESTION_PROMPT
    | llmInstructRephrase
    | StrOutputParser(),
)

_simple_inputs = RunnableMap(
    standalone_question=lambda x: x["question"],
)

#gets knowledge and question
_context = {
    "knowledge": itemgetter("standalone_question") | retriever | _combine_documents,
    "question": itemgetter("standalone_question"),
}

#splits knowledge in its components
_sources = {
    "context": lambda x: x["knowledge"]["context"],
    "sources": lambda x: x["knowledge"]["sources"],
    "chunks": lambda x: x["knowledge"]["chunks"],
    "question": lambda x: x["question"],
}

#calls llm with complete prompt passing sources and chunks
_final = {
    "answer": ANSWER_PROMPT | llmInstruct | StrOutputParser(),
    "sources": lambda x: x["sources"],
    "chunks": lambda x: x["chunks"],
}

#conversational chain definition
conversational_qa_chain = (
    _inputs | _context | _sources | _final
)

conversational_qa_chain = conversational_qa_chain.with_types(input_type=ChatHistory)

#simple chain definition
simple_qa_chain = (
    _simple_inputs | _context | _sources | _final
)

simple_qa_chain = simple_qa_chain.with_types(input_type=ChatHistory)