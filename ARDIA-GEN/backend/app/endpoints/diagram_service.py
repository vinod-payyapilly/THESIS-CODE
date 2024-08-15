from fastapi import APIRouter
from pydantic import BaseModel
from app.config.settings import settings
from app.endpoints.helpers.mermaid_generator import Mermaid_Generator
import requests

"""
    APIs for Mermaid Diagram Generation
"""

router = APIRouter(
    prefix="/mermaid",
    tags=["mermaid"],
    responses={404: {"description": "Not found"}},
)

class Request_Body(BaseModel):
    entity_json: str

MERMAID_SERVER_API_URL = "http://mermaid-server:80/generate"


"""
    Dummy Response 
"""
@router.put("/test")
async def invoke(body: Request_Body ):
    print("Received Message",str(body))
    print("Entity JSON:",body.entity_json)
    return {
        "msg": f"you sent:{body.entity_json}"
    }

"""
    Returns the generated Mermaid Diagram text from Input Entity JSON, using a custom Parser
"""
@router.put("/generate_text")
async def invoke(body: Request_Body ):
    print("API: generate_text called")
    print("Entity JSON:",body.entity_json)

    mm = Mermaid_Generator(body.entity_json)
    mermaid_diagram_text =  mm.get_mermaid_diagram_text()

    return {
        "msg": mermaid_diagram_text
    }

"""
    Returns the Mermaid Diagram SVG, after parsing the Input text
"""
@router.put("/generate_svg")
async def invoke(body: Request_Body ):
    print("API: generate_text called")
    print("Entity JSON:",body.entity_json)

    mm = Mermaid_Generator(body.entity_json)
    mermaid_diagram_text =  mm.get_mermaid_diagram_text()

    headers = {'Content-type': 'text/plain'}
    r = requests.post(MERMAID_SERVER_API_URL, data=mermaid_diagram_text, headers=headers)
    #print(r.text)

    return {
        "msg": r.text
    }