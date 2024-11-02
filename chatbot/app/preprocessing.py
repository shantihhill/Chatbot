from constants import *
from langchain.indexes import SQLRecordManager, index
from langchain_community.document_loaders import DirectoryLoader, UnstructuredPDFLoader
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document as LangchainDocument
from transformers import AutoTokenizer
import random

CHUNK_SIZE = 384
CHUNK_OVERLAP = 100

#getting the embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"},
    #model_kwargs={"device": "cpu", "trust_remote_code": True}
)

#tokenizer and model from sentence transformers
tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)

#print(embedding_model)
#print('between')
#print(tokenizer)

#setting up vector database
collection_name = "jtls-go_index"
vectordb = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embedding_model)

#setting up record manager to track indexes of documents
namespace = f"chroma/{collection_name}"
record_manager = SQLRecordManager(
    namespace, db_url="sqlite:///record_manager_cache.sql"
)

record_manager.create_schema()

#clears all the indexes from the record manager
def _clear():
    index([], record_manager, vectordb, cleanup="full", source_id_key="source")

#indexes all the documents in the knowledge base
def indexAll():
    _clear()

    #loading the documents with specified extensions
    documentLoader = DirectoryLoader(
        KNOWLEDGE_PATH,
        loader_cls=UnstructuredPDFLoader,
        loader_kwargs={"mode": 'elements'}, 
        #glob=['**/*.pdf', '**/*.txt', '**/*.html', '**/*.css', '**/*.js', '**/*.xml', '**/*.dot'],
        glob=['**/*.pdf'],
        #glob=['**/player_guide.pdf'],
        #glob=['**/executive_overview.pdf', '**/TUP.THRESHOLD.WIPED.OUT.pdf', '**/player_guide.pdf', '**/analyst_guide.pdf'],
        show_progress=True
    )
    documents = documentLoader.load()

    #building documents based on loader elements excluding headers
    documentContent = {}
    for i, doc in enumerate(documents):
        category = documents[i].metadata['category']
        source = doc.metadata['source']
        if documentContent.get(source) == None:
            documentContent[source] = ""
        if category != 'Header':
            documentContent[source] += doc.page_content + '\n'

    #build the documents from the contents by source
    documents = []
    for key, value in documentContent.items():
        doc = LangchainDocument(
            page_content=value,
            metadata={"source": key}
        )
        documents.append(doc)
    
    print("number of documents: ", len(documents))
    print("tokens: ", len(tokenizer.tokenize(documents[0].page_content)))

    text_splitter = RecursiveCharacterTextSplitter(
        length_function=lambda x: len(tokenizer.tokenize(x)),
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""], #default
        #separators=[".", "\n", " ", ""],
        #is_separator_regex=True,
        keep_separator='end'
    )
    texts = text_splitter.split_documents(documents)

    texts = [text for text in texts if len(tokenizer.tokenize(text.page_content)) >= CHUNK_OVERLAP and len(text.page_content) >= CHUNK_SIZE and text.page_content.count('.') <= 50]

    #printing chunk data
    list = []
    for i, text in enumerate(texts):
        num = len(tokenizer.tokenize(text.page_content))
        length = len(text.page_content)
        list.append((num, length, text.page_content.count('.')))
        if num <= CHUNK_OVERLAP:
            print('chunk: ', num, len(text.page_content))
            print(text.page_content)

    #print some random chunks
    #for _ in range(5):
        #num = random.randint(1, len(texts)) - 1
        #print(num, len(texts[num].page_content), len(tokenizer.tokenize(texts[num].page_content)))
        #print(texts[num])

    list.sort(reverse=True)
    print('top')
    print(list[:10])
    print('bottom')
    print(list[-10:])
    print("number of chunks: ", len(texts))

    #indexing the chunks and placing into vector database
    print("starting indexing")
    index (
        texts,
        record_manager,
        vectordb,
        cleanup="incremental",
        source_id_key="source"
    )

indexAll()

#older used method to preprocess knowledge base
def preprocessing():
    print('started preprocessing')

    #loading the documents from a directory
    loader = DirectoryLoader(
        KNOWLEDGE_PATH,
        glob=['**/*.pdf', '**/*.txt', '**/*.html', '**/*.css', '**/*.js', '**/*.xml', '**/*.dot'],
        show_progress=True
    )
    documents = loader.load()
    print("number of documents: ", len(documents))

    #splitting the documents(pages) into chunks(# of characters)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    print("number of chunks: ", len(texts))

    #print('making and storing embeddings\n')
    #embedding and storing in database
    #vectordb = Chroma.from_documents(documents=texts, embedding=instructor_embeddings, persist_directory=PERSIST_DIRECTORY)
    #vectordb = None

    print('ended preprocessing')

#preprocessing()