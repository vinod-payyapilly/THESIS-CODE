from langchain_community.llms import VLLMOpenAI
from langchain_community.llms import Ollama
#from langchain_community.llms import VLLM
from langchain_core.prompts import ChatPromptTemplate
# PROMPTS
from app.prompts.NER3 import PROMPT as NER3_PROMPT
from app.prompts.llama3 import PROMPT as LLAMA3_PROMPT
from app.prompts.mistral import PROMPT as MISTRAL_PROMPT

MODEL_MAP = {
    "llama3" : NER3_PROMPT,
    "mistral" : NER3_PROMPT,
    "gemma"  : NER3_PROMPT,
    "default" : NER3_PROMPT,
}

class Default_Model:
    def __init__(self,base_url,llm_server_type="VLLM" ,model="llama3"):
        self.base_url = base_url
        # Choose LLM Server based on
        if llm_server_type == "VLLM":
            self.llm = VLLMOpenAI(
                openai_api_key=VLLM_API_TOKEN,
                openai_api_base=base_url,
                model_name=model
                #model_kwargs={"stop": ["."]},
                )
        else:
            self.llm = Ollama(base_url=base_url,model=model)
        
        #self.PROMPT = MODEL_MAP(model)
        self.PROMPT = MODEL_MAP["default"]

    def get_model(self):
        return self.llm

    def generate_prompt(self):
        #prompt = ChatPromptTemplate.from_template("tell me a joke about {foo}")
        prompt = ChatPromptTemplate.from_template(self.PROMPT)
        return prompt
    
    """
            return llm_response_text.split("```")[1] # LLAMA3
    """    
    def extract_json_from_llm_response(self,llm_response_text):
        start_idx = llm_response_text.find("{")
        end_idx = llm_response_text.rfind("}")
        if start_idx >0 and end_idx > 0:
            return llm_response_text[start_idx:end_idx+1]
        else:
            error_message = f'{"ERROR": {llm_response_text}}'
            return error_message   

    def invoke_llm(self,user_text):
        chain = self.generate_prompt() | self.llm
        llm_response = chain.invoke({"user_text": user_text})
        return self.extract_json_from_llm_response(llm_response)
