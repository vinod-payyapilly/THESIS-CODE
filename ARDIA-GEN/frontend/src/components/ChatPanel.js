import React, { useState } from 'react';

const ChatPanel = ({ onClick }) => {
  const [userText, setUserText] = useState('');
  const [modelName, setmodelName] = useState(() => "llama3:8b");

  const getResponse = (e) => {
    e.preventDefault();
    //if (userText.trim()) {
    onClick(modelName,userText);
    //}
  };

  const handleChange = event => {
    console.log(event.target.value);
    setmodelName(event.target.value);
  };

  return (
    <div>
        <table>
            <tbody>
              <tr>
                <td className="text-white">
                    LLM : <select value={modelName} onChange={handleChange} name="Model" >
                        <option value="llama3:8b">Llama 3(8B)</option>
                        <option value="mistral:7b">Mistral 7B</option>
                        <option value="gemma:7b">Google Gemma 8B</option>
                    </select> <br/>

                    <textarea 
                            type="text"
                            rows="20" cols="100"
                            value={userText}
                            onChange={(e) => setUserText(e.target.value)}
                            placeholder="Type your userText here..."
                        />
                </td >
                <td className="text-white">
                    <button onClick={getResponse} type="submit">&gt;&gt;</button>
                </td>
              </tr>
          </tbody>
      </table>
    </div>
  );
};

export default ChatPanel;