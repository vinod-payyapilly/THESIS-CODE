import pyjson5
from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

EXPECTED_JSON_SCHEMA = {
    "$defs": {
        "entities_array": {
          "type": "array",
          "prefixItems": [
              {"type" : "string","minLength": 1},
              #{"type" : "string","minLength": 1,"enum": ["system","component","person"] },
              {"type" : "string","minLength": 1},
              {"type" : "string"}
            ],
          "minItems": 2,
        },

        "relationship_array": {
          "type": "array",
          #"items": {"type" : "string"},
          "prefixItems": [
              {"type" : "string","minLength": 1},
              #{"type" : "string","minLength": 1,"enum": ["calls","contains","part-of","is-called-from"] },
              {"type" : "string","minLength": 1},
              {"type" : "string","minLength": 2}
            ],
          "minItems": 3,
        },

    },
    "type": "object",
    "properties": {
        "entities": {"type": "array","items": { "$ref": "#/$defs/entities_array" } },
        "relationships": {"type": "array","items": { "$ref": "#/$defs/relationship_array" } },
    },
    "required": ["entities","relationships"],
}

class Json_Checker:
    def __init__(self,json_data_string):
       self.json_data_string = json_data_string
       self.json_data = None
       self.error_message = None

    def get_schema_validation_error(self,best_match_error):
        #print (best_match_error.message)
        error_deque = best_match_error.path
        error_deque_str = list(error_deque)
        #print(error_deque)
        """ Errors at high level, don't include the value """
        #print(error_deque)
        error_context =  None
        if len(error_deque) <= 2:
            error_context = ""
        else:
            error_value = self.json_data.copy()
            while True:
                try:
                    idx_val = error_deque.popleft()
                    current_error_value = error_value[idx_val]
                    if len(error_deque) == 0:
                        if type(current_error_value) in ["string","number","boolean"] \
                                or current_error_value == "":
                            error_context = error_value
                            break
                        else:
                            error_context =  None
                            break
                    error_value = current_error_value
                except IndexError as e:
                    val = None
                    break
    
        return f"JSON-SCHEMA-ERROR: {best_match_error.message}, JSON-Path: {error_deque_str}, Context : {error_context}."

    def json_schema_validation(self):
        """ The response is a dictionary """
        """ There is an "entities" and "relationships" elements """
        """ Both elements are lists """
        """ Each of the lists contains a list containing only string type element"""
        try:
            self.json_data = pyjson5.loads(self.json_data_string)
            #print(self.json_data)
            json_validator = Draft202012Validator(EXPECTED_JSON_SCHEMA).iter_errors(self.json_data)
            best_match_error = best_match(json_validator)
            if best_match_error:
                return False,self.get_schema_validation_error(best_match_error)
            else:
                return True,""
        except Exception as e:
            return False,f"invalid JSON5:{e}"
 
    def check_entity(self):
        entity_json = self.json_data.get("entities")
        error_message = None

        for entity in entity_json:
            """Length of Entity array should be 3"""
            if 3 != len(entity):
                error_message = f"Entity does NOT have 3 elements in array: {entity}"
                return False,error_message
            
            if error_message:
                #print(error_message)
                return False,error_message
            else:
                return True, None

    """
    def check_relationships(self):
        error_message = None
        entity_json = self.json_data.get("entities")
        entities = [ entity[0] for entity in entity_json]
        #print (entities)
        relationships = self.json_data.get("relationships")

        for rel in relationships:
            #TODO: change prompt to ensure that relationships have descriptions

            for ent_idx in [0,2]:
                entity_name = rel[ent_idx]

                if entity_name not in entities:
                    error_message = f"Entity name \"{entity_name}\" unknown in relationship:{rel}"
                    break

        if error_message:
            #print(error_message)
            return False,error_message
        else:
            return True, None
    """

    """
        performs a JSON schema check, additional entity and relationship checks
    """
    def validate_json_entities_relationships(self):
        status,error_message = self.json_schema_validation()
        #print(status,error_message)
        if not status:
            return status,f"JSON-SCHEMA-ERROR: {error_message}"

        status,error_message = self.check_entity()
        if not status:
            return status,f"JSON-VALIDATION-ERROR: {error_message}"
        
        #status,error_message = self.check_relationships()
        #if not status:
        #    return status,f"JSON-VALIDATION-ERROR: {error_message}"
        return status,""

