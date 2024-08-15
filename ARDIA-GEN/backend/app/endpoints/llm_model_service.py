from fastapi import APIRouter
from pydantic import BaseModel
from app.config.settings import settings
import json
from .helpers.llm_model import Default_Model

"""
    APIs for Ollama LLM interactions
"""

router = APIRouter(
    prefix="/llm",
    tags=["llm"],
    responses={404: {"description": "Not found"}},
)

class Request_Body(BaseModel):
    model_name: str
    user_text: str

"""
    Dummy Ollama response 
"""
@router.put("/test")
async def invoke(body: Request_Body ):
    print("Received Message",str(body))
    print("LLM:",body.model_name)
    return {
        "msg": f"you want model:{body.model_name}"
    }

def get_Llm_response(model_name,user_text):
    model = Default_Model(
             base_url=settings.OLLAMA_URL
            ,llm_server_type="OLLAMA"
            ,model=model_name
            )
    print("Invoking the LLM...")
    json_resp = model.invoke_llm(user_text,)
    return json_resp


"""
    Handles Architecture Description as User Input, and returns the response from a remote OLLAMA Service, and chosen LLM
    using a helper class  
"""
@router.put("/invoke")
async def invoke(body: Request_Body ):
    print("Received Message",str(body))
    print("LLM:",body.model_name)
    json_resp = get_Llm_response(body.model_name,body.user_text)

    return {
        "msg": json_resp
    }

"""
    Returns a hardcoded response simulating that from a remote OLLAMA Service, and chosen LLM
    
"""
@router.put("/simulate")
async def invoke(body: Request_Body ):
    print("Received Message",str(body))
    print("LLM:",body.model_name)

    hardcoded_entity_json =         {
            "entities": [
                ["Spark Core", "system", "The foundation of the entire Spark framework."],
                ["Apache Spark", "system", "The framework that includes Spark Core."],
                ["RDD (Resilient Distributed Dataset)", "component", "Provides basic functionality for in-memory data processing."],
                ["Spark SQL", "component", "A module for structured data processing in Spark."],
                ["DataFrame and Dataset APIs", "component", "APIs provided by Spark SQL for querying structured data."],
                ["Spark Streaming", "system", "A real-time processing module in Spark that enables scalable, high- throughput, fault-tolerant stream processing of live data streams."],
                ["Kafka", "component", "One of the sources of data for Spark Streaming."],
                ["Flume", "component", "One of the sources of data for Spark Streaming."],
                ["Kinesis", "component", "One of the sources of data for Spark Streaming."],
                ["TCP sockets", "component", "One of the sources of data for Spark Streaming."],
                ["Spark MLlib", "system", "A scalable machine learning library built on top of Spark Core."],
                ["Spark GraphX", "system", "A distributed graph processing library built on top of Spark Core."],
                ["SparkR", "component", "An R package that provides an R interface for Spark."]
            ],
            "relationships": [
                ["Apache Spark", "contains", "Spark Core"],
                ["Spark Core", "part-of", "Apache Spark"],
                ["Spark SQL", "part-of", "Apache Spark"],
                ["DataFrame and Dataset APIs", "part-of", "Spark SQL"],
                ["Spark Streaming", "part-of", "Apache Spark"],
                ["Kafka", "calls", "Spark Streaming"],
                ["Flume", "calls", "Spark Streaming"],
                ["Kinesis", "calls", "Spark Streaming"],
                ["TCP sockets", "calls", "Spark Streaming"],
                ["Spark MLlib", "part-of", "Apache Spark"],
                ["Spark GraphX", "part-of", "Apache Spark"],
                ["SparkR", "part-of", "Apache Spark"]
            ]
        }
    json_resp = json.dumps(hardcoded_entity_json)

    return {
        "msg": json_resp
    }
