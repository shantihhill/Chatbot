# Chatbot

Chatbot repository for the ODIN project. Contains knowledge base, embedding model, vector store, and server.

## Installation and Usage

Install git

Install python 3.10

Install langserve for both server and client: pip install "langserve[all]"

Install langchain CLI: pip install -U langchain-cli

Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
Pull models, for example for qwen2:1.5b: ollama pull qwen2:1.5b

Install poetry

The source code for both the server and the plugin can be found on Gitlab. Use git clone with your personal access token to import both of the projects.
Server: Alex Hill / Chatbot · GitLab (valkyrie.com) (api_first_add branch)
Client: Alex Hill / ClientChatbot · GitLab (valkyrie.com) (development_branch)

Install dependencies, in the server directory run: poetry install

Repository comes with sample pdfs in knowledgeBase/. To update this, add or remove files from knowledgeBase/, remove the db/ directory that has the vectore database, and run the preprocessing file in app/preprocessing.py. This will remake the db/ directory and fill it.

Embedding models are in models/ directory. To change model, add it to the directory and change the path in the server.py file.

To run the server: poetry run langchain serve --port=8100
Chosen port is 8100. If this should be changed, make sure to also change it in the Moodle plugin at openai_chat/classes/completion/chat.php around line 92.

Copy the openai_chat/ directory to your Moodle server pathToMoodle/blocks

Open the Moodle instance, go to site administration, plugins, and follow the installation process for openai chat. Go with the default values and put any non-empty string in the API box (it will not be used).

To add it to a course go in Edit Mode, open the right block area, and add it with the desired title.