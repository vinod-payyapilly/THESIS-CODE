import React, { useState} from 'react';
import ChatPanel from './components/ChatPanel';
import ResponsePanel from './components/ResponsePanel';
import MermaidSVGDiagram from './components/Diagram';

function App() {
  const [response, setResponse] = useState([]);
  const [loading, setLoading] = useState(false);

  /*
    Generate the Entity JSON from User Text with the help of an LLM
  */
  const getLlmResponse = (modelName,userText) => {
    console.log("Message received:",modelName,userText);

    if (userText.trim()) {
      setResponse("")
      setLoading(true)
      const body_val = JSON.stringify({model_name: modelName, user_text: userText})
      //console.log(body_val)
  
      fetch('/api/llm/invoke', {
          method: 'PUT',
          headers: {
            "Content-Type": "application/json",
          },
          body: body_val 
        })
          .then(response => response.json())
          .then(response => {
                setLoading(false)
                setResponse(response.msg)
              }
            )
    }
    else {
      setResponse("Please type something first!")
    }

  }


  return (
    <div className="App">
      <h1>ArDia Chat</h1>

      <table>
            <tbody>
              <tr>
                  <td className="text-white">
                    <ChatPanel onClick={getLlmResponse} />
                  </td >
                  <td className="text-white">
                    <ResponsePanel showLoading={loading} llmResponse={response} />
                  </td>
              </tr>
              <tr>
                  <td colSpan="2" className="text-white">
                    <MermaidSVGDiagram entityJson={response} />
                  </td>
              </tr>
          </tbody>
      </table>
    </div>
  );
}
//<MermaidDiagram showLoading={false} DiagramData={MermaidData} />
export default App;
