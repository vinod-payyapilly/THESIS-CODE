class Settings:
    MODELS:str = {
    "llama"         : "llama3:8b",
    "llama-large"   : "llama3:70b",
    "mistral"       : "mistral:7b",
    "gemma"         : "gemma:7b",
    # NEWER MODELS
    "phi3"          : "phi3",
    "llama3.1"      : "llama3.1",
    "gemma2"        : "gemma2",
    "mistral-nemo"  : "mistral-nemo",
    "falcon2"      : "falcon2"
}
    #CHOSEN_MODELS: str = ["gemma","llama","mistral"]
    #CHOSEN_MODELS: str = ["mistral"]
    #CHOSEN_MODELS: str = ["phi3","llama3.1","gemma2","mistral-nemo","falcon2"]
    #CHOSEN_MODELS: str = ["phi3","llama3.1","gemma2","mistral-nemo"]
    CHOSEN_MODELS: str = ["gemma2"]
    # DO NOT use the URI after BASE URL
    OLLAMA_BASE_URL: str = "https://a9e2e74b51b61.notebookso.jarvislabs.net/"
    NUMBER_OF_RUNS_PER_FILE: int = 10
    
settings = Settings()