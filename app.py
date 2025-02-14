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
from datetime import datetime
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
        )
        expected = expected.stdout
        with open(file, "w") as f:
            f.write(expected)    
    except subprocess.CalledProcessError as e:
        print(f"Error formatting file: {e.stderr}")
        return False
    
def count_weekdays(input_file: str, output_file: str, weekday: str):
    """
    Count occurrences of a specific weekday in a file and write the count to an output file.
    """
    weekdays = ["Monday", "Tuesday", "Wednesdays", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_index = weekdays.index(weekday)

    # List of all possible date formats in the dataset
    date_formats = [
        "%Y-%m-%d",          # e.g., 2023-02-14
        "%b %d, %Y",         # e.g., Mar 21, 2009
        "%d-%b-%Y",          # e.g., 26-Jan-2020
        "%d/%m/%Y",          # e.g., 14/02/2025
        "%m/%d/%Y",          # e.g., 02/14/2025
        "%d %B %Y",          # e.g., 14 February 2025
        "%B %d, %Y",         # e.g., February 14, 2025
        "%Y/%m/%d %H:%M:%S", # e.g., 2023/06/20 15:18:46
        "%Y/%m/%d",          # e.g., 2023/06/20
        "%d-%m-%Y",          # e.g., 14-02-2025
        "%d/%b/%Y",          # e.g., 14/Feb/2025
        "%d-%B-%Y",          # e.g., 14-February-2025
        "%d-%m-%y",          # e.g., 14-02-25
        "%d/%m/%y",          # e.g., 14/02/25
    ]

    def parse_date(date_str):
        """Try parsing a date string with multiple formats."""
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        # Log unrecognized date formats for debugging
        print(f"Unrecognized date format: {date_str.strip()}")
        return None

    with open(input_file, "r") as file:
        dates = file.readlines()
    count = 0
    for date in dates:
        parsed_date = parse_date(date)
        if parsed_date and parsed_date.weekday() == weekday_index:
            count += 1
    a=f"{count}"
    result=a.strip("")
    print("result",result, type(result))
    with open(output_file, "w") as file:
        file.write(result)  

    return count
  
@app.post("/run")
def task_runner(task: str):
    if 'run' in task.lower():
        try:
            # Parse the task string
            _, script_url, user_email = task.split()
            install_and_run_script(script_url, user_email)
            return {"status": "Script executed successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid task format: {str(e)}")
    elif "format" in task.lower():
        try:
            return a2(file="/data/format.md") 
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to format file: {str(e)}"
            )
    elif "Count" in task:
        try:
            # Extract the input file, output file, and weekday from the task string
            input_file = task.split("`")[1]  # Extract the first file path
            output_file = task.split("`")[3]  # Extract the second file path
            weekday = task.split("number of ")[1].split(" ")[0]  # Extract the weekday
            print("Count executed successfully", input_file, output_file, weekday)
            # Call the function with the extracted parameters
            count_weekdays(input_file, output_file, weekday)
            return {"status": "Count executed successfully"}
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
    response = requests.post(url=url, headers=headers, json=data)
    arguments = response.json()['choices'][0]['message']['tool_calls'][0]['function']['arguments']
    return arguments


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

