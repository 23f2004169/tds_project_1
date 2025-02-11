#/// script
#requires-python = ">=3.13"
#dependencies= [
#   "fastapi",
#   "uvicorn",
#   "requests",
#        ]
#///

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json
from fastapi.exceptions import HTTPException
import subprocess

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET','POST'],
    allow_headers=['*']
)
tools=[
    {
        "type":"function",
        "function":{
            "name":"script_runner",
            "description":"Run a script",
            "parameters":{
                    "type":"object",
                    "properties":{
                        "script_url":{
                            "type":"string",
                            "description":"URL of the script to run"
                              }, 
                        "args":{
                            "type":"array",
                            "items":{
                                "type":"string"
                                },
                            "description":"List of Arguments to pass to the script"
                            } ,
                    },
                        "required":["script_url","args"]
                    }           
            }
        }
]

AIPROXY_TOKEN=os.getenv("AIPROXY_TOKEN")
@app.get('/')
def home():
    return {'Hello': 'World'}

@app.get("/read")
def read_file(path:str):
    try:
        with open(path,"r") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail="File does not exist")
    
@app.post("/run")
def task_runner(task:str):
    url="https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers={
        "Content-Type":"application/json",
        "Authorization":f"Bearer {AIPROXY_TOKEN}"
        }
    data={
          "model":"gpt-4o-mini",
          "messages":[
              {
                  "role":"user",
                  "content":task
               },
               {
                   "role":"system",
                   "content":"""
                   Your task is to answer the question based on the context provided.
                   """ 
                }
            ],
            "tools":tools,
            "tool_choice":"auto"
        }
    response=requests.post(url=url, headers=headers, json=data)
    arguments=response.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments']
    return arguments

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)