import ScaleLoader from 'react-spinners/ScaleLoader';

const ResponsePanel = ({ showLoading , llmResponse }) => {
  
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
        
        <ScaleLoader color="#36d7b7" loading={showLoading} />
        {
          llmResponse && 
          <span>
            <h2> JSON representation</h2>
            <textarea 
              type="text" readOnly disabled
              rows="16" cols="100"
              value={llmResponse}
              />
          </span>
        }

    </div>
  );
};

export default ResponsePanel;