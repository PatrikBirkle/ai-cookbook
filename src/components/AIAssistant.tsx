import React from 'react';
import styled from 'styled-components';

const AIAssistantContainer = styled.div`
  padding: 20px 30px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h2`
  color: #2c3e50;
  font-size: 20px;
  margin: 0;
`;

const IframeContainer = styled.div`
  width: 100%;
  height: calc(100vh - 120px);
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  overflow: hidden;
`;

const StyledIframe = styled.iframe`
  width: 100%;
  height: 100%;
  border: none;
`;

interface AIAssistantProps {
  streamlitUrl: string;
}

const AIAssistant: React.FC<AIAssistantProps> = ({ streamlitUrl }) => {
  return (
    <AIAssistantContainer>
      <IframeContainer>
        <StyledIframe 
          src={streamlitUrl} 
          title="AI Assistant"
          allow="microphone; camera; autoplay; clipboard-write;"
        />
      </IframeContainer>
    </AIAssistantContainer>
  );
};

export default AIAssistant; 