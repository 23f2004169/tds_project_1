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

#TASK A1
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
 
#TASK A2
def format(file: str = "/data/format.md"):
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
    
#TASK A3    
def count_weekdays(input_file: str, output_file: str, weekday: str):
    """
    Count occurrences of a specific weekday in a file and write the count to an output file.
    """
    weekdays = ["Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays", "Sundays"]
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
  
#TASK A4
import json

# def sort_contacts(input_file: str, output_file: str):
#     with open(input_file, "r") as file:
#         contacts = json.load(file)
#     # Sort the contacts by last_name, then first_name 
#     contacts.sort(key=lambda c: (c["last_name"], c["first_name"]))
#     contacts_repr = repr(contacts)
#     with open(output_file, "w") as file:
#         file.write(contacts_repr)
#     return contacts

import json

def sort_contacts(input_file: str, output_file: str):
    """
    Reads contacts from the input file, sorts them by last_name and first_name,
    and writes the sorted contacts to the output file as valid JSON.
    """
    # Read the contacts from the input file
    with open(input_file, "r") as file:
        contacts = json.load(file)

    # Sort the contacts by last_name, then first_name
    contacts.sort(key=lambda c: (c["last_name"], c["first_name"]))

    # Write the sorted contacts to the output file as valid JSON
    with open(output_file, "w") as file:
        json.dump(contacts, file, indent=4, sort_keys=True)  # Correctly write JSON to the file

    return contacts
# def sort_contacts(input_file: str, output_file: str):
#     input_file = f".{input_file}"
#     if not os.path.exists(input_file):
#         raise ValueError(f"File {input_file} does not exist.")
#     with open(input_file, "r") as f:
#         contacts = json.load(f)
#     sorted_contacts = sorted(contacts, key=lambda c: (c.get("last_name", ""), c.get("first_name", "")))
#     output_file = output_file[5:]
#     with open(f"./data/{output_file}", "w") as f:
#         json.dump(sorted_contacts, f)
#     return f"A4 Completed: Sorted contacts stored in {output_file}"

#TASK 5 : Write the first line of the 10 most recent .log file in /data/logs/ to /data/logs-recent.txt, most recent first
#TASK 6
import os
import json

def markdown(inputfile, outputfile):
    """
    Creates an index JSON file mapping Markdown filenames to their first H1 titles.

    Args:
        inputfile (str): The base directory containing Markdown files.
        outputfile (str): The path to the output JSON file.
    """
    # Initialize the index dictionary
    index = {}
    # Walk through the directory to find all .md files
    for root, _, files in os.walk(inputfile):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, inputfile)
                # Read the file and extract the first H1
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("# "):  # Check for H1
                            title = line[2:].strip()  # Remove "# " and strip whitespace
                            index[relative_path] = title
                            break
    # Write the index to the output JSON file
    with open(outputfile, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)
    print(f"Index file created at {outputfile}")
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
            return format(file="/data/format.md") 
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to format file: {str(e)}"
            )
    elif "count" in task.lower():
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
    elif "contacts" in task.lower():
        try:
            # Find the input and output file paths
            input_file = task.split("`")[1]  # Extract the first file path
            output_file = task.split("`")[7] 
            #strip the backticks in file paths
            # Debug: Log the extracted file paths
            print("Extracted file paths:", input_file, output_file)
            sort_contacts(input_file, output_file)
            return {"status": "Contacts sorted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid task format: {str(e)}")
    elif "logs" in task.lower():
        pass
    elif "markdown" in task.lower():
        try:
            # Extract the input file and output file paths
            inputfile = task.split("`")[1]  # Extract the first file path
            outputfile = task.split("`")[3]  # Extract the second file path
            # Call the function with the extracted parameters
            markdown(inputfile, outputfile)
            return {"status": "Markdown files indexed successfully"}
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

