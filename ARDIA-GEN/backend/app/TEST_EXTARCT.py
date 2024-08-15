text = ""
with open("app/sample_outputs/erroring.json") as spark_text:
    text= spark_text.read()
    #print(text)
    #json_txt = text.split("```")[1]
    json_txt = text


from endpoints.helpers.mermaid_generator import Mermaid_Generator

# --------------
print("#"*81)
mm = Mermaid_Generator(json_txt)
diagram_text = mm.get_mermaid_diagram_text()
print(diagram_text )
print("#"*81)

# --------------
import requests
url = "http://mermaid-server:80/generate"
headers = {'Content-type': 'text/plain'}
r = requests.post(url, data=diagram_text, headers=headers)
print(r.text)