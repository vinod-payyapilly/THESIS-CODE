import fnmatch
import os
import json
from pprint import pprint


JSON_folders = ["../DATASET/Azure"]

def check_entity(json_data):
    entity_json = json_data.get("entities")
    if not entity_json:
        print("No Entities found")
        return False
    
    #print(entity_json)
    for entity in entity_json:
        #print(entity)
        """Length of Entity array should be 3"""
        if 3 != len(entity):
            print("Entity does NOT have 3 elements in array")
            return False
    
        """Entity Name not empty"""
        entity_name = entity[0]
        if not entity_name:
            print("Entity name empty")
            return False

        """Entity Type not empty"""
        entity_type = entity[1]
        if not entity_type:
            print("Entity type empty")
            return False

        if entity_type not in ["system","component","person"]:
            print("Entity type invalid:", entity_type)
            return False
        
        return True
                 
def check_relationships(json_data):
    entity_json = json_data.get("entities")
    entities = [ entity[0] for entity in entity_json]
    #print (entities)
    relationships = entity_json = json_data.get("relationships")


    #print(entity_json)
    for rel in relationships:
        #print(entity)
        """Length of Entity array should be 3"""
        if 4 != len(rel):
            print("Relationship does NOT have 4 elements in array")
            return False

        """Entity Name empty"""
        for ent_idx in [0,2]:
            entity_name = rel[ent_idx]
            if not entity_name:
                print("Entity name empty:",rel )
                return False

            if entity_name not in entities:
                print(f"Entity name \"{entity_name}\" unknown in relationship:", rel )
                return False

        """Relationship Type not empty"""
        rel_type = rel[1]
        if not rel_type:
            print("Relationship Typ empty")
            return False

        if rel_type not in ["calls","contains","part-of","is-called-from"]:
            print("Relationship Type invalid:", rel_type)
            return False


def check_json_file(filepath):
    print(f"checking {filepath}")
    with open(filepath) as json_data_raw:
        json_data = json.load(json_data_raw)
        #print()
        check_entity(json_data)
        #pprint(d)
        check_relationships(json_data)

if __name__ == "__main__":
    for folder in JSON_folders:
        print(f"----------------------{folder}-----------------")
        print("#"*80)
        for root, dirs, files in os.walk(folder):
                for _f in sorted(fnmatch.filter(files, '*.json')):
                    filepath = os.path.join(root, _f)
                    #print(filepath)
                    check_json_file(filepath)
    print("#"*80)
