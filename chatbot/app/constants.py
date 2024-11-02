#Module for constants across application

bad = """
JTLS-GO 6.3.0.0\nxiii\nSoftware Maintenance Manual\n28.5.9 Update Command ...........................................................................................28-12"""

bad2= """
...................................................................."""

bad3="""
.................................................................................................."""

bad4="""
..............................................."""

ALL_MINILM_L6_V2_PATH = "./models/all-MiniLM-L6-v2/"
STELLA_EN_400M_V5 = "./models/stella_en_400M_v5/"
ALL_MPNET_BASE_V1 = "./models/all-mpnet-base-v1"
ALL_MPNET_BASE_V2 = "./models/all-mpnet-base-v2"
GTR_T5_LARGE = "./models/gtr-t5-large"

EMBEDDING_MODEL_NAME = ALL_MPNET_BASE_V2
#EMBEDDING_MODEL_PATH = "./models/" + EMBEDDING_MODEL_NAME
TOKENIZER_MODEL_PATH = "sentence-transformers/all-MiniLM-L6-v2"

NUM_SOURCES = 5
PERSIST_DIRECTORY = './db'
KNOWLEDGE_PATH = "./knowledgeBase/"
FLAGS_DATABASE_URL = "sqlite:///./flags.db"

SYSTEM_ANSWER_MESSAGE = """1. You are a chatbot helping users learn and understand JTLS-GO (JOINT THEATER LEVEL SIMULATION - GLOBAL OPERATIONS), version 6.3.0.0.
2. Your task is to answer the user's question at the end with factual and useful information.
3. Use only the context provided and nothing else to answer the question.
4. Do not provide false information, if you don't know the answer say so and explain why.
5. Make your answer crisp and limited to 3 or 4 sentences."""

USER_ANSWER_MESSAGE = """Context: {context}

Question: {question}
"""

SYSTEM_REPHRASE_MESSAGE = """1. Rephrase the Input Question into a Standalone Question based on the Chat history.
2. Make only small modifications and formulate the Standalone Question to be understood without needing the Chat History.
3. Keep all names and terms from the Input Question in the Standalone Question unmodified, even if they appear to be wrong.
4. Use only the knowledge from the Chat History and Input Question, add no external terms, facts, or information.
5. If you are unsure how to rephrase it, make the Standalone Question identical to the Input Question.
6. Do NOT answer the Input Question.

Below are a couple examples to guide you:
Example One:
Chat History: Human: What is C ++?
Assistant: C ++ is a high-level, general-purpose programming language created by Danish computer scientist Bjarne Stroustrup.

Input Question: What is it good for and why did he build it?

Standalone Question: What is C ++ good for and why did Danish computer scientist Bjarne Stroustrup build it?
Example Two:
Chat History: Human: Explain how rainbows are formed.
Assistant: A rainbow is formed when sunlight is scattered from raindrops into the eyes of an observer.

Input Question: Ecsplain in mor det ail.

Standalone Question: Ecsplain in mor det ail the formation of rainbows.
Example Three:
Chat History: Human: Tell me about mathematical optimizations?
Assistant: Mathematical optimization or mathematical programming is the selection of a best element, with regard to some criterion, from some set of available alternatives.

Input Question: What about setting up tents?

Standalone Question: Tell me about setting up tents?"""

USER_REPHRASE_MESSAGE = """Chat History: {chat_history}

Input Question: {question}

Standalone question: """

QWEN2_REPHRASE_TEMPLATE = ("<|im_start|>system\n" + SYSTEM_REPHRASE_MESSAGE + "<|im_end|>\n<|im_start|>user\n"
                            + USER_REPHRASE_MESSAGE + "<|im_end|>\n<|im_start|>assistant\n")
QWEN2_ANSWER_TEMPLATE = ("<|im_start|>system\n" + SYSTEM_ANSWER_MESSAGE + "<|im_end|>\n<|im_start|>user\n"
                        + USER_ANSWER_MESSAGE + "<|im_end|>\n<|im_start|>assistant\n")

GEMMA2_REPHRASE_TEMPLATE = ("<start_of_turn>system\n" + SYSTEM_REPHRASE_MESSAGE + "<end_of_turn>\n<start_of_turn>user\n"
                            + USER_REPHRASE_MESSAGE + "<end_of_turn>\n<start_of_turn>model")
GEMMA2_ANSWER_TEMPLATE = ("<start_of_turn>system\n" + SYSTEM_ANSWER_MESSAGE + "<end_of_turn>\n<start_of_turn>user\n"
                        + USER_ANSWER_MESSAGE + "<end_of_turn>\n<start_of_turn>model")

LLAMA3_QA_REPHRASE_TEMPLATE = ("System: " + SYSTEM_REPHRASE_MESSAGE + "\nUser: "
                            + USER_REPHRASE_MESSAGE + "\nAssistant: <|begin_of_text|>")
LLAMA3_QA_ANSWER_TEMPLATE = ("System:" + SYSTEM_ANSWER_MESSAGE + "\nUser: "
                            + USER_ANSWER_MESSAGE + "\nAssistant: <|begin_of_text|>")

PHI_3_5_REPHRASE_TEMPLATE = ("<|system|>\n" + SYSTEM_REPHRASE_MESSAGE + "<|end|>\n<|user|>\n"
                            + USER_REPHRASE_MESSAGE + "<|end|>\n<|assistant|>\n")
PHI_3_5_ANSWER_TEMPLATE = ("<|system|>\n" + SYSTEM_ANSWER_MESSAGE + "<|end|>\n<|user|>\n"
                            + USER_ANSWER_MESSAGE + "<|end|>\n<|assistant|>\n")

SMOLLM_REPHRASE_TEMPLATE = ("<|im_start|>system\n" + SYSTEM_REPHRASE_MESSAGE + "<|im_end|>\n<|im_start|>user\n"
                            + USER_REPHRASE_MESSAGE + "<|im_end|>\n<|im_start|>assistant\n")
SMOLLM_ANSWER_TEMPLATE = ("<|im_start|>system\n" + SYSTEM_ANSWER_MESSAGE + "<|im_end|>\n<|im_start|>user\n"
                        + USER_ANSWER_MESSAGE + "<|im_end|>\n<|im_start|>assistant\n")

QWEN2_1_5 = "qwen2:1.5b"
QWEN2_1_5_INSTRUCT = "qwen2:1.5b-instruct"
QWEN2_0_5_INSTRUCT = "qwen2:0.5b-instruct-q4_0"
PHI_3_5_INSTRUCT = "phi3.5:3.8b-mini-instruct-q4_0"
SMOLLM_1_7 = "smollm:1.7b-instruct-v0.2-q4_0"
GEMMA2_2 = "gemma2:2b-instruct-q4_0"
LLAMA3_QA_8 = "llama3-chatqa:8b-v1.5-q4_0"

MODEL_NAME = GEMMA2_2
REPHRASE_MODEL_NAME = GEMMA2_2

REPHRASE_TEMPLATE = GEMMA2_REPHRASE_TEMPLATE
ANSWER_TEMPLATE = GEMMA2_ANSWER_TEMPLATE