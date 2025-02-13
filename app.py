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
from dotenv import load_dotenv
load_dotenv()
AIPROXY_TOKEN=os.getenv("AIPROXY_TOKEN")


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
            print(f"Reading file: {path}")
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=404, detail="File does not exist")


def task_a2(script_url: str, user_email: str):
    # Check if 'uv' is installed
    try:
        subprocess.run(['uv', '--version'], check=True)
    except subprocess.CalledProcessError:
        # Install 'uv' if not installed
        subprocess.run(['pip', 'install', 'uv'], check=True)

    # Download and run the script
    try:
        response = requests.get(script_url)
        response.raise_for_status()

        # Save the script to a temporary file
        script_path = './datagen.py'
        with open(script_path, 'w') as script_file:
            script_file.write(response.text)
     
        # Run the script with the user's email as an argument
        subprocess.run(['./venv/bin/python3', script_path, user_email], check=True)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to run script: {str(e)}")


@app.post("/run")
def task_runner(task: str):
    print("CURRENT TASK RUNNER", task)
    if task.startswith("run"): 
        try:
            print('Currently running task dategnpy:', task)
            # Parse the task string
            _, script_url, user_email = task.split()
            task_a1(script_url, user_email)
            return {"status": "Script executed successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid task format: {str(e)}")

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
    try:
        response = requests.post(url=url, headers=headers, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the response JSON
        response_data = response.json()

        # Safely extract the arguments from the response
        tool_calls = response_data.get('choices', [])[0].get('message', {}).get('tool_calls', [])
        if not tool_calls:
            raise ValueError("No ability calls found in the response")

        arguments = tool_calls[0].get('function', {}).get('arguments', {})
        return {"status": "success", "message": json.loads(arguments)}
    except requests.exceptions.RequestException as e:
        # Handle HTTP request errors
        raise HTTPException(status_code=500, detail=f"HTTP request failed: {str(e)}")

    except (KeyError, ValueError, json.JSONDecodeError) as e:
        # Handle JSON parsing or missing data errors
        raise HTTPException(status_code=500, detail=f"Failed to parse response: {str(e)}")
    # response = requests.post(url=url, headers=headers, json=data)
    # print(response.json())
    # arguments = response.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments']
    # return {"status": "success", "message": json.loads(arguments)}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

