"""
    pip install spacy
    python -m spacy download en_core_web_lg
    pip install pyjson5
    pip install jsonschema
"""
from helpers.LLM_Response_Evaluation import LLM_Response_Evaluation
import pandas as pd

def get_all_metrics_df_file(llm_response_filepath):
    llm_response_df = pd.read_csv(llm_response_filepath)
    llm_response_list = llm_response_df.to_dict("records")
    print ( "Total Input records : ", len(llm_response_list))
    #print( llm_response_list[0])
    print("-"*81)
    print("Running evaluations...")
    print("-"*81)
    all_metrics = []
    for llm_response in llm_response_list:
        llm_eval  = LLM_Response_Evaluation(llm_response)
        this_run_metrics = llm_eval.run()
        #print(this_run_metrics)
        all_metrics.append(this_run_metrics)

    # Pandas Dataframe for all metrics
    all_metrics_df = pd.DataFrame(all_metrics)
    return all_metrics_df

def get_mean_median_metrics_sorted(df,mean_cols,mean_or_median="MEAN"):
    metrics_df = df.copy()
    #print( "Cols:",len(mean_cols))
    if mean_or_median == "MEAN":
        mean_df = metrics_df[mean_cols].mean().to_frame().reset_index()
    else:
        mean_df = metrics_df[mean_cols].median().to_frame().reset_index()
    mean_df.columns = ["metric","value"]
    mean_df = mean_df.sort_values(by=["metric"]).reset_index(drop=True)
    return mean_df


def get_processed_metrics(all_metrics_df):
    valid_rows = all_metrics_df[ all_metrics_df["status"] == True ]
    #print(valid_rows.shape[0])

    processed_metrics_df = pd.DataFrame()
    processed_metrics_df["filename"] = valid_rows["filename"].copy()
    processed_metrics_df["time_taken_per_word"] = valid_rows["time_taken_seconds"]/valid_rows["word_count_original_text"]

    """
        Entities
    """
    processed_metrics_df["entity_count_detected_pct"] = valid_rows["entity_count_llm_detected"]\
                                    / valid_rows["entity_count_expected"]
    processed_metrics_df["entity_count_correctly_detected_pct"] = valid_rows["entity_count_correctly_detected"]\
                                    / valid_rows["entity_count_expected"]
    processed_metrics_df["entity_count_undetected_pct"] = valid_rows["entity_count_undetected"]\
                                    / valid_rows["entity_count_expected"]
    processed_metrics_df["entity_count_wrongly_detected_pct"] = valid_rows["entity_count_wrongly_detected"]\
                                    / valid_rows["entity_count_llm_detected"]
    
    """
        Relationships
    """
    processed_metrics_df["rel_count_detected_pct"] = valid_rows["rel_count_llm_detected"]\
                                    / valid_rows["rel_count_expected"]
    processed_metrics_df["rel_count_correctly_detected_skip_type_pct"] = valid_rows["rel_count_correctly_detected_skip_type"]\
                                    / valid_rows["rel_count_expected"]
    processed_metrics_df["rel_count_undetected_skip_type_pct"] = valid_rows["rel_count_undetected_skip_type"]\
                                    / valid_rows["rel_count_expected"]
    processed_metrics_df["rel_count_wrongly_detected_skip_type_pct"] = valid_rows["rel_count_wrongly_detected_skip_type"]\
                                    / valid_rows["rel_count_llm_detected"]
    processed_metrics_df["rel_count_entities_correctly_detected_pct"] = valid_rows["rel_count_correctly_detected"]\
                                    / valid_rows["rel_count_expected"]
    processed_metrics_df["rel_count_undetected_pct"] = valid_rows["rel_count_undetected"]\
                                    / valid_rows["rel_count_expected"]
    processed_metrics_df["rel_count_wrongly_detected_pct"] = valid_rows["rel_count_wrongly_detected"]\
                                    / valid_rows["rel_count_llm_detected"]

    return processed_metrics_df


def get_aggregate_metrics(comparable_metrics_df):
    mean_cols = [ 
                    "time_taken_per_word",
                    "entity_count_detected_pct","entity_count_correctly_detected_pct","entity_count_undetected_pct","entity_count_wrongly_detected_pct",
                    "rel_count_detected_pct","rel_count_correctly_detected_skip_type_pct","rel_count_undetected_skip_type_pct",
                    "rel_count_wrongly_detected_skip_type_pct","rel_count_entities_correctly_detected_pct","rel_count_undetected_pct",
                    "rel_count_wrongly_detected_pct"
                 ]

    """
        Mean Metrics
    """
    mean_df = get_mean_median_metrics_sorted(comparable_metrics_df,mean_cols,"MEAN")
    median_df = get_mean_median_metrics_sorted(comparable_metrics_df,mean_cols,"MEDIAN")

    """
        Standard Deviation Metrics
            Calculate the standard devaition of each of the metrics within the group. 
            Then take the mean across all groups
    """ 
    grouped_std_df = comparable_metrics_df.groupby("filename")[mean_cols].std()
    std_df = get_mean_median_metrics_sorted(grouped_std_df,mean_cols,"MEAN")

    """
        Aggregate te metrics by combining
    """
    aggregated_metrics = pd.DataFrame()
    aggregated_metrics["metric"] = mean_df["metric"]
    aggregated_metrics["mean_value"] = mean_df["value"]
    aggregated_metrics["median_value"] = median_df["value"]
    aggregated_metrics["mean_grouped_std_value"] = std_df["value"]

    return aggregated_metrics

def get_all_models_aggregated_metrics(model_name_list,aggregated_metrics_list):
    all_models_aggregated_metrics = pd.DataFrame()

    all_models_aggregated_metrics["metric"] = aggregated_metrics_list[0]["metric"]
    for model_name,aggregated_metric in zip(model_name_list,aggregated_metrics_list):
        all_models_aggregated_metrics[f"{model_name}-mean_value"] = aggregated_metric["mean_value"]
        all_models_aggregated_metrics[f"{model_name}-median_value"] = aggregated_metric["median_value"]
        all_models_aggregated_metrics[f"{model_name}-mean_grouped_std_value"] = aggregated_metric["mean_grouped_std_value"]

    return all_models_aggregated_metrics

def print_all_metrics(all_metrics_df):
    print("#"*81)
    print ( "Total Output records : ", all_metrics_df.shape[0])
    print("#"*81)
    if all_metrics_df.shape[0] > 0:
        #pd.set_option('display.max_columns', 500)
        #pd.set_option('display.width', 200)
        pd.set_option('max_colwidth', 10)
        pd.set_option('display.expand_frame_repr', False)

        print(all_metrics_df[[
                "status",
                "entity_count_expected",
                "entity_count_llm_detected",
                "entity_count_correctly_detected",
                "entity_count_undetected",
                "entity_count_wrongly_detected",
                "entity_type_invalid_count_llm_detected",
                #"error_message"
            ]
            ])

if __name__ == "__main__":
    
    """ Process the LLm Response file """
    # TODO: Structure check for LLAMA responses
    #llm_response_filepath = "OUTPUT/LLM_RESPONSES_gemma_2024-07-25 01-20.csv"
    #llm_response_filepath = "OUTPUT/LLM_RESPONSES_llama_2024-07-25 01-28.csv"
    #llm_response_filepath = "OUTPUT-OLLAMA/LLM_RESPONSES_mistral_2024-07-25 02-51.csv"

    model_name_filepath_dict = {
        #"phi3"          : "OUTPUT NEW/LLM_RESPONSES_phi3_2024-07-28 20-16.csv",
        #"llama3.1"      : "OUTPUT NEW/LLM_RESPONSES_llama3.1_2024-07-28 20-27.csv",
        "gemma2"        : "OUTPUT/LLM_RESPONSES_gemma2_2024-07-31 02-00.csv",
        #"mistral-nemo"  : "OUTPUT NEW/LLM_RESPONSES_mistral-nemo_2024-07-28 20-59.csv",        
    }

    """
        Loop over model file and create the aggregated metrics for each model
    """
    aggregated_metrics_list = []
    for model_name, llm_response_filepath in model_name_filepath_dict.items():
        print("-"*35,model_name,"-"*35)
        all_metrics_df = get_all_metrics_df_file(llm_response_filepath)
        #print(all_metrics_df["error_message"])
        record_count = all_metrics_df.shape[0]
        invalid_record_count = all_metrics_df[all_metrics_df["status"] == False].shape[0]
        
        if invalid_record_count > 0:
            print("#"*81)
            if invalid_record_count >= record_count/2:
                print(f"ERROR: More than 50% records has errors: {invalid_record_count}/record_count")
            else:
                print(f"WARNING: Some records has errors:: {invalid_record_count}/record_count")
            print("#"*81)

        processed_metrics_df = get_processed_metrics(all_metrics_df)
        
        aggregate_metrics_df = get_aggregate_metrics(processed_metrics_df)

        #print(aggregate_metrics_df)
        aggregated_metrics_list.append(aggregate_metrics_df)

    """
        Get the aggregation across all models
    """
    all_models_aggregated_metrics= get_all_models_aggregated_metrics(
                        model_name_filepath_dict.keys()
                        ,aggregated_metrics_list
                    )
    print(all_models_aggregated_metrics)
    all_models_aggregated_metrics.to_csv("OUTPUT NEW/MODEL-METRICS-COMPARISON.csv")

    