
import json
class Mermaid_Generator:
    def __init__(self,entity_json_text,title=""):
        self.entity_json = json.loads(entity_json_text)
        self.title = title or "\ntitle System Context Diagram"

        self.mermaid_diagram_text = "C4Context"
        self.mermaid_diagram_text += self.title

        self.entity_dict = {}
        self.connections = []
        self.indices = {
            "person"    : 0,
            "system"    : 0,
            #"component" : 0,
            "boundary"    : 0,
        }
        # To reference nodes in diagram using the generated IDs, for connections 
        self.diagram_node_id_dict = {}

    """
        Sets the parent entity of a given entity
    """
    def add_entity_parent(self,entity,parent):
        self.entity_dict[entity]["parent"] = parent

    """
        Adds a new connection(calls or called-from)
    """
    def add_connection(self,source_entity,target_entity):
        self.connections.append(
            {
                "source" : source_entity,
                "target" : target_entity
            }
        )

    """
        Generates the internal datastructure to process entities from the JSON
    """
    def process_entity_json(self):
        """
            Add all entities to a dictionary, include a parent attribute
        """
        for entity in self.entity_json["entities"]:
            entity_name = entity[0]
            entity_type = entity[1]
            entity_desc = entity[2]
            self.entity_dict[entity_name] = {
                "name"   : entity_name,
                "type"   : entity_type,
                "desc"   : entity_desc,
                "parent" : ""
            }

        """
            process parent-child relationships
        """
        for relationship in self.entity_json["relationships"]:
            entity_source     = relationship[0]
            relationship_type = relationship[1]
            entity_target     = relationship[2]

            if relationship_type == "contains":
                self.add_entity_parent(entity_target,entity_source)
            elif relationship_type == "part-of":
                self.add_entity_parent(entity_source,entity_target)
            elif relationship_type == "calls":
                self.add_connection(entity_source,entity_target)
            elif relationship_type == "called-from":
                self.add_connection(entity_target,entity_source)


    """
        Change all the connections(calls or called-from) involved with an entity(source) into target.
            A -> B
            A <- C
        move_connection(A,D) =>
            D -> B
            D <- C
        
    def move_connection(self,source_entity,target_entity):
        count_connections = 0
        for conn in self.connections:
            if conn["source"] == source_entity:
                conn["source"] = target_entity
                count_connections += 1
            if conn["target"] == source_entity:
                conn["target"] = target_entity
                count_connections += 1
        return count_connections
    """

    """
        Move to new parent 
    """
    def move_child_entities_to_new_parent(self,old_parent_name,new_parent_name):
        for entity, entity_val in self.entity_dict.items():
            if (entity_val["parent"] == old_parent_name):
                entity_val["parent"] = new_parent_name
                self.entity_dict[entity] = entity_val

    def count_connections(self,entity_name):
        num_connections = 0
        for conn in self.connections:
            if conn["source"] == entity_name:
                num_connections += 1
            if conn["target"] == entity_name:
                num_connections += 1
        return num_connections

    """
        For parent entities which have links, create a pseudo parent for boundary
    """
    def correct_parent_entities_with_links(self):
        # Loop through all parent entities
        for parent_entity_name  in set( entity["parent"] for entity in self.entity_dict.values()):
            num_connections = self.count_connections(parent_entity_name)
            print(parent_entity_name)
            # if there is a connection to/from them
            if num_connections > 0:
                # Recreate parent with "Boundary: <entity name>" as prefix and change entity-type to system
                parent_entity = self.entity_dict[parent_entity_name].copy()
                new_parent_entity_name = f"Boundary: {parent_entity_name}"

                self.entity_dict[new_parent_entity_name] =   {
                                                        "name"   : new_parent_entity_name,
                                                        "type"   : "system",
                                                        "desc"   : "Boundary: " + parent_entity["desc"],
                                                        "parent" : parent_entity["parent"]
                                                        }

                # Move the old parent child entity under this new parent
                self.add_entity_parent(parent_entity_name,new_parent_entity_name)
                # Set old entity as a component
                parent_entity["type"] = "component"
                parent_entity["parent"] = new_parent_entity_name

                self.entity_dict[parent_entity_name] =  parent_entity 
                
                # Move all children to the new parent
                self.move_child_entities_to_new_parent(parent_entity_name,new_parent_entity_name)


    """
        Returns an arrays of entity dicts, which are direct children of the given entity(as dict)
    """
    def get_direct_children(self,parent_entity):
        entity_name = parent_entity["name"]
        child_entities = []

        for entity in self.entity_dict.values():
            if entity["parent"] == entity_name:
                child_entities.append(entity)
        return child_entities

    """
        Recursive function to generate the Subgraph Text of a given entity( as dict)
    """
    def generate_sub_graph(self,entity,line_intent=4):
        entity_name = entity["name"]
        entity_type = entity["type"]
        entity_desc = entity["desc"]

        intent = " "*line_intent
        # Persons should NOT have any children
        # TODO: verify above
        if entity_type == "person":
            self.indices["person"] += 1
            id = f'Person_{self.indices["person"]}'
            self.diagram_node_id_dict[entity_name] = id

            return intent + f'Person({id}, "{entity_name}", "{entity_desc}")'
        elif entity_type in ["system","component"]:
            self.indices["system"] += 1
            child_entities = self.get_direct_children(entity)
            
            if len(child_entities) == 0:
                """ No children """
                id = f'System_{self.indices["system"]}'
                self.diagram_node_id_dict[entity_name] = id
                return intent + f'System({id}, "{entity_name}", "{entity_desc}")'
            else:
                """ Children exists, start a boundary """
                self.indices["boundary"] += 1
                id = f'B_{self.indices["boundary"]}'
                self.diagram_node_id_dict[entity_name] = id

                subgraph_text = intent + f'System_Boundary({id}, "{entity_name}") '+"{"
                for child_entity in child_entities:
                    child_graph_text = self.generate_sub_graph(child_entity,line_intent+4)
                    subgraph_text  += "\n" + intent + child_graph_text
                subgraph_text += "\n" + intent + "}"
                return subgraph_text
        else:
            return ""

    """
        Adds the Diagram lines corresponding to each Entity Type
    """
    def generate_entities(self):
        for entity in self.entity_dict.values():
            parent = entity["parent"]
            
            # process only top level entities
            # children would automatically be processed, as a part of their parent
            if parent == '':
                entity_graph = self.generate_sub_graph(entity)
                self.mermaid_diagram_text += "\n" + entity_graph

        for conn in self.connections:
            source_diagram_id = self.diagram_node_id_dict[conn["source"]]
            target_diagram_id = self.diagram_node_id_dict[conn["target"]]
            self.mermaid_diagram_text += "\n" + " "*4 + f'Rel({source_diagram_id}, {target_diagram_id}, "")'

    """
        Called from outside to retrieve the C4Graph for the given entity_json
    """
    def get_mermaid_diagram_text(self):
        self.process_entity_json()
        self.correct_parent_entities_with_links()
        self.generate_entities()
        return self.mermaid_diagram_text