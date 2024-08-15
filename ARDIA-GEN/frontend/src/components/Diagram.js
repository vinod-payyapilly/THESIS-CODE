import React, { useState } from 'react';

var MermaidSVGDiagram = ({ entityJson }) => {
  const [mermaidDiagramText, setMermaidDiagramText] = useState("");
  const [mermaidSVG, setMermaidSVG] = useState("");

  /*
    Generate the Mermaid Diagram Text from Entity JSON (as text)
  */
    const getMermaidText = () => {
      console.log("Entity JSON:",entityJson);
  
      if (entityJson) {
        setMermaidDiagramText("")
        //setLoading(true)
        console.log(entityJson)
        const body_val = JSON.stringify({entity_json: entityJson})
        //console.log(body_val)

        fetch('/api/mermaid/generate_text', {
            method: 'PUT',
            headers: {
              "Content-Type": "application/json",
            },
            body: body_val 
          })
            .then(response => response.json())
            .then(response => {
              setMermaidDiagramText(response.msg)
                }
              )
      }
      else {
        alert("Please type something first!")
      }
  
    }

  /*
    Generate the Mermaid Diagram Text from Entity JSON (as text)
  */
    const getMermaidSVG = () => {
      //var response = entityJson
      console.log("Entity JSON:",entityJson);
  
      if (entityJson) {
        setMermaidSVG("")
        //setLoading(true)
        console.log(entityJson)
        const body_val = JSON.stringify({entity_json: entityJson})
        //console.log(body_val)

        fetch('/api/mermaid/generate_svg', {
            method: 'PUT',
            headers: {
              "Content-Type": "application/json",
            },
            body: body_val 
          })
            .then(response => response.json())
            .then(response => {
                  setMermaidSVG(response.msg)
                }
              )
      }
      else {
        alert("Please type something first!")
      }
  
    }

/*
  const getMermaidSVG_OLD = () => {
    console.log("getMermaidSVG");

    if (response) {
      //setMermaidSVG("")
      const body_val = `    C4Context
      title System Context diagram for Internet Banking System
      Enterprise_Boundary(b0, "BankBoundary0") {
        Person(customerA, "Banking Customer A", "A customer of the bank, with personal bank accounts.")
        Person(customerB, "Banking Customer B")
        Person_Ext(customerC, "Banking Customer C", "desc")

        Person(customerD, "Banking Customer D", "A customer of the bank, <br/> with personal bank accounts.")

        System(SystemAA, "Internet Banking System", "Allows customers to view information about their bank accounts, and make payments.")

        Enterprise_Boundary(b1, "BankBoundary") {

          SystemDb_Ext(SystemE, "Mainframe Banking System", "Stores all of the core banking information about customers, accounts, transactions, etc.")

          System_Boundary(b2, "BankBoundary2") {
            System(SystemA, "Banking System A")
            System(SystemB, "Banking System B", "A system of the bank, with personal bank accounts. next line.")
          }

          System_Ext(SystemC, "E-mail system", "The internal Microsoft Exchange e-mail system.")
          SystemDb(SystemD, "Banking System D Database", "A system of the bank, with personal bank accounts.")

          Boundary(b3, "BankBoundary3", "boundary") {
            SystemQueue(SystemF, "Banking System F Queue", "A system of the bank.")
            SystemQueue_Ext(SystemG, "Banking System G Queue", "A system of the bank, with personal bank accounts.")
          }
        }
      }

      BiRel(customerA, SystemAA, "Uses")
      BiRel(SystemAA, SystemE, "Uses")
      Rel(SystemAA, SystemC, "Sends e-mails", "SMTP")
      Rel(SystemC, customerA, "Sends e-mails to")

      UpdateElementStyle(customerA, $fontColor="red", $bgColor="grey", $borderColor="red")
      UpdateRelStyle(customerA, SystemAA, $textColor="blue", $lineColor="blue", $offsetX="5")
      UpdateRelStyle(SystemAA, SystemE, $textColor="blue", $lineColor="blue", $offsetY="-10")
      UpdateRelStyle(SystemAA, SystemC, $textColor="blue", $lineColor="blue", $offsetY="-40", $offsetX="-50")
      UpdateRelStyle(SystemC, customerA, $textColor="red", $lineColor="red", $offsetX="-50", $offsetY="20")

      UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")


`
      console.log(body_val)
  
      // Calls the mermaid-server Docker container to fetch the SVG representation of the Diagram-text
      fetch('http://localhost:80/generate', {
          method: 'POST',
          headers: {
            "Content-Type": "text/plain",
          },
          //body: body_val 
          body: response 
        })
        .then(response => response.text())
          .then(response => {
                console.log(response)
                //setMermaidSVG(response)
              }
            )
    }
    else {
      console.log("Please type something first!")
    }

  }
*/

  return  (
      <div>
        <table>
            <tbody>

                <tr>
                  <td>
                      <button onClick={getMermaidText} type="submit">Get Mermaid Code&#8681;</button>
                  </td>
                  <td className="text-white">
                      <span>
                        <h2> Mermaid Diagram representation</h2>
                        <textarea 
                          type="text" readOnly disabled
                          rows="16" cols="100"
                          value={mermaidDiagramText}
                          />
                      </span>
                  </td>
              </tr>

              <tr>
                  <td colSpan="2" className="text-white">
                    Mermaid: <button onClick={getMermaidSVG}>Get SVG</button>

                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                    dangerouslySetInnerHTML={{__html: mermaidSVG}} 
                    />
                  </td>
              </tr>
            </tbody>
        </table>
      </div>
    )
  };

//<MermaidSVGDiagram DiagramSVG={mermaidSVG} />

/*



*/

export default MermaidSVGDiagram;
