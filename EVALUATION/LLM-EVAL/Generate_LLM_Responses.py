"""
    ----OLLAMA---
    ollama run llama3:8b
    ollama run gemma:7b
    ollama run mistral:7b

    ---- Untried----
    ollama run llama3.1
    ollama run gemma2
    ollama run mistral-nemo
    ollama run phi3
    ollama run falcon2
"""

from helpers.llm_model import Default_Model
import time
import pandas as pd
import fnmatch
import os
from pathlib import Path
from random import shuffle
import json
from config.settings import settings


MODELS = settings.MODELS
OLLAMA_BASE_URL = settings.OLLAMA_BASE_URL
NUMBER_OF_RUNS_PER_FILE = settings.NUMBER_OF_RUNS_PER_FILE

"""
    Get the Response from LLM using the helper class
"""
def get_llm_response(model_name,text):
    model = Default_Model(
                base_url=OLLAMA_BASE_URL
                ,llm_server_type="OLLAMA"
                ,model=model_name
            )
    #print("Invoking the LLM...")
    full_resp,json_resp = model.invoke_llm(text,)
    return full_resp,json_resp

"""
    Extracts the Dataflow from Azure Description files
    All Lines between the "Components" and "Workflow" 
"""

def get_dataflow_text(text_filepath):
    data_flow_text = []
    start_line = False
    with open(text_filepath) as text:
        for line in text.readlines():
            #print(line)
            if line.strip().startswith("Workflow") or line.strip().startswith("Dataflow"):
                start_line = True
                continue
            if line.strip().startswith("Components"):
                break
            if start_line:
                data_flow_text.append(line)
    return ''.join(data_flow_text)

"""
    Returns the JSON from a JSON file
"""
def get_json_data(json_filepath):
    with open(json_filepath) as json_data_raw:
        json_data = json.load(json_data_raw)
    return json_data

""" get the Dictionary object containing the 
    
        MODEL_NAME
        filename
        original text
        llm_full_response
        llm_json_extracted
        time taken
"""

import string, secrets
def get_random_string():
    letters = string.ascii_lowercase+string.ascii_uppercase+string.digits            
    return ''.join(secrets.choice(letters) for i in range(5))


"""
    Gets the response from LLM for a specific datafile
        and, create a dictionary that contains the filename, content,responses and time
"""
def get_dict_llm_response_parameters(model_name, text_filepath):
    llm_response_parameters_dict = None
    
    """ Original Text """
    #dataflow_text = get_dataflow_text(text_filepath)
    (dataflow_text,expected_json) = FILEPATH_MAP_TEXT_CONTENT_EXPECTED_JSON_DICT[text_filepath]

    """ Get Response from LLM """
    llm_response_json = {}
    try:
        start_time = time.perf_counter ()
        #llm_response_json = get_random_string()
        #llm_response_full = get_random_string()
        llm_response_full,llm_response_json = get_llm_response(model_name,dataflow_text)
        end_time = time.perf_counter ()
        time_taken = end_time - start_time
        #print(end_time - start_time, "seconds")

        llm_response_parameters_dict = {
            "MODEL_NAME"          : model_name,
            "filename"            : text_filepath,
            "original text"       : dataflow_text,
            "expected_json"       : json.dumps(expected_json),
            "llm_full_response"   : llm_response_full,
            "llm_json_extracted"  : llm_response_json,
            "time_taken_seconds"  : time_taken
        }
    except Exception as e:
        #print(traceback.format_exc())
        print("Error:",e)
        #TODO Retry
    
    return llm_response_parameters_dict

"""
    A dictionary that contains the text_file_path as key 
    and values as a tuple tuple of text-content and expected-json-content  
"""
FILEPATH_MAP_TEXT_CONTENT_EXPECTED_JSON_DICT = {
    # text_file_path : (text_context,expected_json)
}

"""
    Sets the FILEPATH_MAP_TEXT_CONTENT_EXPECTED_JSON_DICT as a map between
    the Text-file-path and a tuple of text-content and expected-json-content
"""
def set_filepath_map_dict(text_file_json_file_dict):
    #print(text_file_paths)    
    for text_filepath,json_filepath in text_file_json_file_dict.items():
        """ Original Text """
        dataflow_text = get_dataflow_text(text_filepath)
        json_data = get_json_data(json_filepath)
        #print(text_filepath)
        #print(dataflow_text)

        FILEPATH_MAP_TEXT_CONTENT_EXPECTED_JSON_DICT[text_filepath] = \
            (dataflow_text,json_data)

"""
    Return a list of all .txt files,
        for which a exactly named .json file exists in the same folder
"""
def get_text_file_json_file_map(folder):
    print(f"Detecting files in folder: {folder}")
    all_text_files_json_files_dict = {}

    for root, dirs, files in os.walk(folder):
            for _f in sorted(fnmatch.filter(files, '*.json')):
                json_filepath = os.path.join(root, _f)

                json_path_object = Path(json_filepath)
                text_filename = json_path_object.stem + ".txt"
                """ Text File from JSON """
                text_filepath = os.path.join(root, text_filename)
                text_path_object = Path(text_filepath)
                
                #print("JSON File:",json_filepath)
                if text_path_object.is_file():
                    #print("Text File:",text_filepath)
                    all_text_files_json_files_dict[text_filepath] = json_filepath
                else:
                    print(json_filepath, "No Text File found!!")

    return all_text_files_json_files_dict

if __name__ == "__main__":   
    """ Process Files and initialize global dictionary"""
    text_file_json_file_dict = get_text_file_json_file_map("../IMAGES NEW/")
    text_file_paths = list(text_file_json_file_dict.keys())
    set_filepath_map_dict(text_file_json_file_dict)

    print("MODELS:",settings.CHOSEN_MODELS)
    print("Runs per file:",settings.NUMBER_OF_RUNS_PER_FILE)

    #for model in ["gemma","llama","mistral"]:
    for model in settings.CHOSEN_MODELS:
        MODEL_NAME =  MODELS[model]
        print("#"*81)
        print(f"Processing LLM: {MODEL_NAME}")
        print("#"*81)
        
        llm_response_dict_list = []
        """ RUNS """
        for i in range(0,NUMBER_OF_RUNS_PER_FILE):
            print("-"*37,f"RUN {i+1}","-"*37)
            # Sort the files list randomly
            shuffle(text_file_paths)
            #print(text_file_paths)

            """ Process the files """
            for text_filepath in text_file_paths:
                print(f"Processing: {text_filepath}")
                llm_response_parameters_dict = get_dict_llm_response_parameters(MODEL_NAME, text_filepath)
                #print(llm_response_parameters_dict)
                if llm_response_parameters_dict:
                    llm_response_dict_list.append(llm_response_parameters_dict)

        llm_response_dict_df = pd.DataFrame(llm_response_dict_list)
        print(llm_response_dict_df)


        """
            Save to CSV LLM_RESPONSES_<model>_<DATE_TIME>.csv
        """
        from datetime import datetime,timedelta,timezone
        current_datetime_str = (datetime.now(timezone.utc)+timedelta(hours=2))\
            .strftime("%Y-%m-%d %H-%M")
        filename= f"OUTPUT/LLM_RESPONSES_{model}_{current_datetime_str}.csv"
        llm_response_dict_df.to_csv(filename)
        print(f"Saved to {filename}")

