# Arxiv Agent using the TIM model. 
This agent allows the TIM model to use tools to summarize the daily papers on the huggingface daily papers page [https://huggingface.co/papers](url) on a given day. 

# Set up
This agent uses Open WebUI [https://github.com/open-webui/open-webui](url), so python 3.11 is required. 
Set up the agent by installing the requirements:
```
pip install requirements.txt
```
Launch the tools server. The example below uses uvicorn and launches the server on http://localhost:8070
```
uvicorn arxiv_server:app --host 0.0.0.0 --port 8070
```
Launch the arxiv_server server. The example below uses uvicorn and launches the server on http://localhost:8000
```
uvicorn arxiv_server:app --host 0.0.0.0 --port 8000
```
Launch Open WebUI. Below launches Open WebUI on http://localhost:8080
```
open-webui serve
```
On your Open WebUI server, go to Admin Panel -> Settings -> Connections. Under Manage OpenAI API Connections, press Add Connection and type http://localhost:8000/v1 or your.arxiv_server.url/vl. You may optionally go to Admin Panel -> Settings -> Interface and disable all generation, which makes the generation faster. 

# Using the TIM model
You can create your own agent with internal tool use using the TIM model, similar to this one. 
