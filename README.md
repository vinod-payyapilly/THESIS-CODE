
# Structure

## ARDIA-GEN
This folder contains the source-code for the ARDIA-GEN System.

It consists of the following subcomponents:
### backend
Contains the backend source-code
### frontend
Contains the frontend source-code
### diagram-generator
Contains the Docker runs scripts for diagram-generator

## EVALUATION
This folder contains the data and source-code used in evaluating LLMs.

It contains the following sub-modules:
 
### DATASET
Contains the self-created dataset to evaluate the LLMS
 
### LLM-EVAL
Contains the source-code to:
#### Generate_LLM_Responses.py
Generates LLM Responses as CSV-files for models specified in the settings
#### Generate_LLM_Evaluations.py
Creates the Consolidated Metrics as CSV-file from model CSV files 
#### LLM_Comparison.ipynb
Creates the Comparison Report for the models from the evaluation CSV-file

### ### LLM-EVAL
Contains the source-code to verify the JSON-schema of the manually created Expected JSON files in the Dataset
