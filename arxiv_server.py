import json
import requests
from openai import OpenAI

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal


openai_client = OpenAI(
    base_url = "https://api.subconscious.dev/v1",
    api_key = "test-key" # get the key from https://subconscious.dev
)


def resp_to_markdown(resp):

    res_json = json.loads(resp.choices[0].message.content)
    res_obj = {}
    res_obj['tasks'] = res_json['reasoning']
    res_ans = res_json['answer']
    
    ans_json = {}
    ans_json['title'] = "Final Answer"
    ans_json['conclusion'] = res_ans

    res_obj['tasks'].append(ans_json)

    res_str = json.dumps(res_obj)

    cur_params = {
        "tool_name": 'JsonToMarkdown',
        "parameters": {
            'json_string': res_str
        },
    }

    url = 'http://mcp-toolbox-server-alb-844138745.us-east-1.elb.amazonaws.com/call_tool'
    response = requests.post(url, json=cur_params)
    res = response.json()
    markdown = res['markdown']

    return markdown


def return_response(research_question):

    sys_msg_list = [
        'You are encouraged to use the following tools:\n',
        '- PaperListTool: Returns a list of paper titles and ids given a date. The date must be in yyyy-mm-dd format',
        '- AbstractTool: Returns the title and abstract of a paper given an id. Use the ids returned from using the PaperListTool. The id is usually in nnnn.nnnnn format'
    ]
    system_prompt = '\n'.join(sys_msg_list)

    resp = openai_client.chat.completions.create(
        model = "tim-large",
        messages = [
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': research_question
            }
        ],
        top_p = 0.95,
        max_completion_tokens = 10000,
        temperature = 0.6,
        tools = [
            {
                "type": "function",
                "name": "PaperListTool",
                "description": "Returns a list of paper titles and ids given a date. The date must be in yyyy-mm-dd format",
                "url": "http://localhost/call_tool",
                "method": "POST",
                "timeout": 10,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "A date in yyyy-mm-dd format"
                        }
                    },
                    "required": [
                        "date"
                    ],
                    "additionalProperties": False
                }
            }, 
            {
                "type": "function",
                "name": "AbstractTool",
                "description": "Returns the title and abstract of a paper given an id. Use the ids returned from using the PaperListTool.",
                "url": "http://localhost/call_tool",
                "method": "POST",
                "timeout": 10,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "paperid": {
                            "type": "string",
                            "description": "A paper id. Usually in nnnn.nnnnn format"
                        }
                    },
                    "required": [
                        "paperid"
                    ],
                    "additionalProperties": False
                }
            }, 
        ]
    )

    return resp_to_markdown(resp)


app = FastAPI()

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]


@app.post("/v1/chat/completions")
def chat_completions(request: ChatRequest):
    user_message = [m.content for m in request.messages if m.role == "user"][-1]
    ans = return_response(user_message)

    return {
        "choices": [
            {
                "message": {"role": "assistant", "content": ans},
            }
        ]
    }


@app.get("/v1/models")
def models():
    return {
        "data": [
            {
            "id": "arxiv",
            }
        ]
    }
