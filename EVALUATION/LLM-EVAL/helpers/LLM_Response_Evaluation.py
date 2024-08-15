import json
import numpy as np
import spacy
nlp = spacy.load('en_core_web_lg')
import pyjson5
from helpers.json_checker import Json_Checker

SEMANTIC_MATCH_THRESHOLD = 0.9

class LLM_Response_Evaluation:
    def __init__(self,llm_response_dict):
        self.llm_response_dict = llm_response_dict
        self.metrics = {
            # RUN details
            "MODEL_NAME"          : llm_response_dict["MODEL_NAME"],
            "filename"            : llm_response_dict["filename"],
            "time_taken_seconds"  : llm_response_dict["time_taken_seconds"],
            "word_count_original_text" : len(llm_response_dict["original text"].split()),
            "status"                   : True,
            "error_message"            : None,
            # ENTITY METRICS
            "entity_count_expected"                  : 0,
            "entity_count_llm_detected"              : 0,
            # Count of entities with the wrong entity type
            "entity_type_invalid_count_llm_detected" : 0,
            # Entities correctly detected, wrongly detected & undetected
            "entity_count_correctly_detected"        : 0,
            "entity_count_undetected"                : 0,
            "entity_count_wrongly_detected"          : 0,
            # RMS of all matched entities' semantic similarity
            "entity_matched_semantic_rms"        : None,

            #  RELATIONSHIP METRICS
            "rel_count_expected"                     : 0,
            "rel_count_llm_detected"                 : 0,
            # Count of relationships with the wrong relationship-type
            "rel_type_invalid_count_llm_detected"    : 0,
            # Ignore relationship types
            "rel_count_correctly_detected_skip_type" : 0,
            "rel_count_undetected_skip_type"         : 0,
            "rel_count_wrongly_detected_skip_type"   : 0,
            # Consider relationship types
            "rel_count_correctly_detected"           : 0,
            "rel_count_undetected"                   : 0,
            "rel_count_wrongly_detected"             : 0,

            "rel_count_entities_correctly_detected"  : 0,
        }
        self.expected_relationships = {}
        self.detected_relationships = {}
        self.json_checker = None

    def set_error(self,error_message):
        self.set_metric("status",False)
        self.set_metric("error_message",error_message)

    """
        Extracts the JSON from the Raw Text LLM response
        JSON content within the first "{" and the last "}"
    """
    def correct_json_in_llm_response(self,json_string):
        start_idx = json_string.find("{")
        end_idx = json_string.rfind("}")
        if start_idx >0 and end_idx > 0:
            return True,json_string[start_idx:end_idx+1]
        else:
            error_message = "No '{' character found in JSON, will probably error out"
            self.set_error(error_message)
            return False,""

    """
        Set various variables needed for processsing
        Also, validates the JSON response for entities and relationships
    """
    def process_data(self):
        #print(self.llm_response_dict["llm_json_extracted"])
        run_status,llm_json_extracted_corrected = self.correct_json_in_llm_response(self.llm_response_dict["llm_json_extracted"])
        if not run_status:
            self.set_error("No JSON found in the LLM Response")
            return False

        """
            Validate the LLM Response JSON in Input Dictionary
        """
        self.json_checker = Json_Checker(llm_json_extracted_corrected)
        run_status,error_message = self.json_checker.validate_json_entities_relationships()
        if not run_status:
            #print("Error:",error_message)
            self.set_metric("status",False)
            self.set_metric("error_message",error_message)
            return run_status

        self.expected_json = json.loads(self.llm_response_dict["expected_json"])
        
        """
            JSON schema was also previously validated by the JSON-checker
        """    
        self.llm_response_json = pyjson5.loads(llm_json_extracted_corrected)
        

        self.expected_entities = self._get_entities(self.expected_json)
        self.detected_entities = self._get_entities(self.llm_response_json)
        self.correctly_detected_entities = list( set.intersection(
                                                                  set(self.expected_entities),
                                                                  set(self.detected_entities))
                                                                )
        return True
    
    def set_metric(self,metric_name, value):
        self.metrics[metric_name] = value

    def _get_entities(self, json):
        entity_json = json.get("entities")
        """Name of Entity is the first element in the entities array """
        return { entity[0].lower(): entity for entity in entity_json }

    def check_entities_basic(self):
        expected_entity_count = len(self.expected_entities)
        llm_detected_entity_count = len(self.detected_entities)
        
        """ Entity counts general"""
        self.set_metric("entity_count_expected",expected_entity_count)
        self.set_metric("entity_count_llm_detected",llm_detected_entity_count)
        #print ("expected_entity_count",expected_entity_count)
        #print ("llm_detected_entity_count",llm_detected_entity_count)

        """ Entity Type not as specified ["system","component","person"]"""
        entity_type_invalid_count = 0 
        for entity in self.expected_entities.values():
            entity_type = entity[1]
            if entity_type not in ["system","component","person"]:
                entity_type_invalid_count += 1
        
        self.set_metric("entity_type_invalid_count_llm_detected",entity_type_invalid_count)
        #print ("expected_entity_count",expected_entity_count)

        """ Entity counts correctly,incorrectly matched"""
        undetected_entity_count = len(list( set(self.expected_entities) - set(self.detected_entities)) )
        #wrongly_detected_entity_count = len( list(set(detected_entities) - set(expected_entities)) )
        wrongly_detected_entity_count = len(list(set(self.detected_entities) - set(self.expected_entities)))
        
        self.set_metric("entity_count_correctly_detected",len(self.correctly_detected_entities))
        self.set_metric("entity_count_undetected",undetected_entity_count)
        self.set_metric("entity_count_wrongly_detected",wrongly_detected_entity_count)

    def check_entities_semantically(self):
        """ Entity semantic similarity for correctly matched"""
        semantic_similarity_list = []
        for entity in self.correctly_detected_entities:
            expected_entity_desc = self.expected_entities[entity][2]
            detected_entity_desc = self.detected_entities[entity][2]
            #print(expected_entity_desc,detected_entity_desc)
            semantic_similarity = nlp(expected_entity_desc).similarity(nlp(detected_entity_desc))
            #print( semantic_similarity )
            semantic_similarity_list.append(semantic_similarity)
        #print(semantic_similarity_list)
        """ Root mean Square Similarity """
        
        if semantic_similarity_list:
            sematic_similarity_rms = np.sqrt(np.mean(np.array(semantic_similarity_list)**2))
            self.set_metric("entity_semantic_similarity",np.round(sematic_similarity_rms,3))

    def merge_detected_entities_semantically(self):
        # TODO: use an upto date LLM to detect semantic similarity ? 
        #   or simply handle this in the prompt

        #TODO: Semantic similarity using relationships

        """ Entity semantic similarity for matching unmatched"""
        unmatched_detected_entities = list(set(self.detected_entities) - set(self.correctly_detected_entities))
        #unmatched_original_entities = list(set(self.expected_entities) - set(self.correctly_detected_entities))

        #Semantic similarity of each unmatched detected entity with each unmatched_original entity
        for detected_entity in unmatched_detected_entities:
            #for original_entity in unmatched_original_entities:
            detected_entity_desc = self.detected_entities[detected_entity][2]
            
            ## Match with all expected entities, maybe merge with another entity
            semantic_match_entity = None
            semantic_match_entity_desc = None
            best_semantic_match = 0

            for original_entity in self.expected_entities:
                expected_entity_desc = self.expected_entities[original_entity][2]
                #print(expected_entity_desc,detected_entity_desc)
                semantic_similarity = nlp(expected_entity_desc).similarity(nlp(detected_entity_desc))
                if (semantic_similarity > best_semantic_match) and \
                        semantic_similarity >= SEMANTIC_MATCH_THRESHOLD:
                        semantic_match_entity = original_entity
                        semantic_match_entity_desc = expected_entity_desc
                        best_semantic_match = semantic_similarity

            # Highest match larger than threshold
            if best_semantic_match >= SEMANTIC_MATCH_THRESHOLD:
                print("Semantic similarity above threshold:",best_semantic_match)
                print(f"detected:{detected_entity} & original:{semantic_match_entity}")
                print(f"""Description "{detected_entity_desc}" & "{semantic_match_entity_desc}" """)
                # TODO: Merge when a high similarity is detected

    """ 
        Returns a dictionary object of the relationship, where the key is a tuple (source_entity,target_entity)
        and value the corresponding connection_type
        connection-types "part-of" and "is-called-from" are replaced by "contains" and "calls", and inverting the
        source and target entities
    """
    def _get_relationships(self,json):
        rel_json_orig = json.get("relationships")

        """ Relationship object for comparison """
        rel_dict = {}

        replace_conns = {"part-of":"contains","is-called-from": "calls"}
        for rel in rel_json_orig:
            #print(rel)
            conn_type = rel[1]
            if conn_type in replace_conns.keys():
            # replace all "part-of" relationships to "contains"
                #switch entities
                temp = rel[0]
                rel[0]  = rel[2]
                rel[2]  = temp
                rel[1] = replace_conns[conn_type]
                #print("-----------")
            #print(rel)
            rel_dict[(rel[0],rel[2])] = rel[1]
        
        #print (rel_dict)
        return rel_dict

    """
        Create relationship variables for comparison
    """  
    def process_relationships(self):
        """ Fetch comparable relationship dictionaries"""
        #print("#"*81)
        self.expected_relationships = self._get_relationships(self.expected_json)
        #print(self.expected_relationships)
        #print("#"*81)
        self.detected_relationships = self._get_relationships(self.llm_response_json)
        #print(self.detected_relationships)        

    """
        Compare 2 lists, to identify matches, unmatched on the left, unmatched on the right
    """
    def list_compare(self,list1,list2):
        undetected = list( set(list1) - set(list2))
        corrrectly_detected = list( set(list1) - set(undetected))
        wrongly_detected = list( set(list2) - set(corrrectly_detected))
        return (len(corrrectly_detected),len(undetected),len(wrongly_detected))

    """
        List of tuples of the relationships, each of the form (source_entity,target_entity,connection_type)
    """
    def _get_relationships_with_types(self,relationship_dict):
        return [ tuple(list(k)+ [v]) for k,v in relationship_dict.items()]

    """
        Evaluations involving relationships
    """    
    def check_relationships(self):
        """ Count of reltionships in expected and LLM response """
        self.set_metric("rel_count_expected", len(self.expected_relationships))
        self.set_metric("rel_count_llm_detected", len(self.detected_relationships))

        """ Relationship Type not a specified ["calls","contains","part-of","is-called-from"]"""
        rel_type_invalid_count = 0 
        for rel_type in self.detected_relationships.values():
            if rel_type not in ["calls","contains","part-of","is-called-from"]:
                #print("INVALID RELATIONSHIP Type", rel_type)
                rel_type_invalid_count += 1
        
        self.set_metric("rel_type_invalid_count_llm_detected",rel_type_invalid_count)

        """ Identifying a relationship between 2 entities """
        """ Identifying the right relationship between 2 entities """
        correctly_detected_count,undetected_count,wrongly_detected_count \
                = self.list_compare(self.expected_relationships.keys(), self.detected_relationships.keys())
        self.set_metric("rel_count_correctly_detected_skip_type", correctly_detected_count)
        self.set_metric("rel_count_undetected_skip_type", undetected_count)
        self.set_metric("rel_count_wrongly_detected_skip_type", wrongly_detected_count)

        """ List object to compare entities and relationship types """
        expected_relationships_and_types = self._get_relationships_with_types(self.expected_relationships)
        detected_relationships_and_types = self._get_relationships_with_types(self.detected_relationships)
        #print(expected_relationships_and_types)
        #print(detected_relationships_and_types)

        correctly_detected_count,undetected_count,wrongly_detected_count \
                = self.list_compare(expected_relationships_and_types, detected_relationships_and_types)
        self.set_metric("rel_count_correctly_detected", correctly_detected_count)
        self.set_metric("rel_count_undetected", undetected_count)
        self.set_metric("rel_count_wrongly_detected", wrongly_detected_count)

        """ Wrongly detected relationships """

    def print_metrics(self):
        for metric,value in self.metrics.items():
            print(metric,value)

    def get_metrics(self):
        return self.metrics

    def run(self):
        run_status = self.process_data()
        #print(error_status)
        if run_status:
            """ Entities """
            #self.merge_detected_entities_semantically()
            self.check_entities_basic()
            #self.check_entities_semantically()

            """ Relationships """
            self.process_relationships()
            self.check_relationships()
        
        return self.get_metrics()
