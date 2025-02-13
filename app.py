# /// script
# requires-python = ">=3.13"
# dependencies= [
#   "fastapi",
#   "uvicorn",
#   "requests",
#        ]
# ///

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json
from fastapi.exceptions import HTTPException
import subprocess
# from dotenv import load_dotenv

# load_dotenv()

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['GET', 'POST'],
    allow_headers=['*']
)
tools = [
    {
        "type": "function",
        "function": {
            "name": "script_runner",
            "description": "Run a script",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "script_url": {
                            "type": "string",
                            "description": "URL of the script to run"
                        },
                        "args": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of Arguments to pass to the script"
                        },
                    },
                "required": ["script_url", "args"]
            }
        }
    }
]



@app.get('/')
def home():
    return {'Hello': 'World'}


@app.get("/read")
def read_file(path: str):
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail="File does not exist")


def install_and_run_script(script_url: str, user_email: str):
    try:
        subprocess.run(['uv', '--version'], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(['pip', 'install', 'uv'], check=True)
    try:
        response = requests.get(script_url)
        response.raise_for_status()
        script_path = './datagen.py'
        with open(script_path, 'w') as script_file:
            script_file.write(response.text)
        subprocess.run(['./venv/bin/python3', script_path, user_email], check=True)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run script: {str(e)}")

# def task_a2():
#     # Check if 'prettier' is installed
#     try:
#         subprocess.run(['prettier', '--version'], check=True)
#     except FileNotFoundError:
#         # Install 'prettier@3.4.2' if not installed
#         try:
#             subprocess.run(['npm', 'install', '-g', 'prettier@3.4.2'], check=True)
#         except Exception as e:
#             raise HTTPException(
#                 status_code=500, detail=f"Failed to install prettier: {str(e)}"
#             )

#     # Format the file using prettier
#     file_path = '/data/format.md'
#     try:
#         subprocess.run(['prettier', '--write', file_path], check=True)
#         return {"status": "File formatted successfully"}
#     except subprocess.CalledProcessError as e:
#         raise HTTPException(
#             status_code=500, detail=f"Failed to format file: {str(e)}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"An unexpected error occurred: {str(e)}"
#         )
    
import subprocess

def a2(file: str = "/data/format.md"):
    with open(file, "r") as f:
        original = f.read()
    try:
        expected = subprocess.run(
            ["npx", "prettier@3.4.2", "--stdin-filepath", file],
            input=original,
            capture_output=True,
            text=True,
            check=True
            # Ensure npx is picked up from the PATH on Windows
        )
        expected = expected.stdout
        with open(file, "w") as f:
            f.write(expected)    
    except subprocess.CalledProcessError as e:
        print(f"Error formatting file: {e.stderr}")
        return False
    
@app.post("/run")
def task_runner(task: str):
    if task.startswith("run "):
        try:
            # Parse the task string
            _, script_url, user_email = task.split()
            install_and_run_script(script_url, user_email)
            return {"status": "Script executed successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid task format: {str(e)}")
    elif "Format" in task:
        # Call task_a2 to format the file
        try:
            return a2(file="/data/format.md") 
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to format file: {str(e)}"
            )

    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": """
                   Your task is to answer the question based on the context provided.
                   """
            },
            {
                "role": "user",
                "content": task
            }
        ],
        "tools": tools,
        "tool_choice": "auto"
    }
    response = requests.post(url=url, headers=headers, json=data)
    arguments = response.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments']
    return arguments


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

