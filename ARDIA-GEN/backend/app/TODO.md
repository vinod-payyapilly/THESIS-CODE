# Boundary elements cannot be linked to other elements!
## Fix JSON Generator or Diagram Generator ?
* Option 1:*
If an entity has "contains" or something that is "part-of" 
1) Create a new System type Entity with a name as "System : <orginal name>".
2) Create a new "contains" relation between the new Entity and the orginal entity.
3) Move all direct child entities of the original Entity to the new one.

* Option 2*
If an entity has "contains" or something that is "part-of" 
1) Rename the orginal Entity to "System : <orginal name>".
2) Create a new Component type Entity with a name as "<orginal name>".
3) Create a new "contains" relation between the orginal entity and the new Entity.
3) Move all connections of the orginal entity to the new one.

* Option 3*
Knowledge DB Representation on which such rules can be applied?

# C4container Diagram: https://mermaid.js.org/syntax/c4.html
# When erroring, save input data to file
# Define a component as one that has a link, and a system as an entities which have a link(calls or is called-from) 
# Bi-directional relationships