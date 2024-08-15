from langchain_community.llms import VLLMOpenAI
from langchain_community.llms import Ollama
#from langchain_community.llms import VLLM
from langchain_core.prompts import ChatPromptTemplate
# PROMPTS
from app.prompts.NER3 import PROMPT as NER3_PROMPT
from app.prompts.Zero_shot_CoT import PROMPT as Zero_shot_CoT_PROMPT


MODEL_MAP = {
    #"llama3" : NER3_PROMPT,
    #"mistral" : NER3_PROMPT,
    #"gemma"  : NER3_PROMPT,
    #"mixtral"  : NER3_PROMPT,
    "default" : Zero_shot_CoT_PROMPT,
}

VLLM_API_TOKEN = "token-ardia-chat"

class Default_Model:
    def __init__(self,base_url,llm_server_type="VLLM" ,model="llama3"):
        self.base_url = base_url
        self.model = model
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
    
    def extract_json_from_llm_response(self,llm_response_text):
        response_json = None
        try:
            if self.model in ["llama3","gemma"]:
                response_json = llm_response_text.split("```")[1] # LLAMA3, GEMMA
            else:
                #self.model in ["mistral","mixtral"]:
                response_json = llm_response_text # MIXTRAL, MIXTRAL

        except Exception as e:
            print("Error:",e)
            response_json = {"error:",e}
        return response_json

    def invoke_llm(self,user_text):
        chain = self.generate_prompt() | self.llm
        llm_response = chain.invoke({"user_text": user_text})
        extracted_json = self.extract_json_from_llm_response(llm_response)
        return llm_response,extracted_json
