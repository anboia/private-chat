import { useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { Sidebar } from './components/Sidebar';
import { Chat } from './components/Chat';

function App() {
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');
  const [chatKey, setChatKey] = useState(0); // For forcing chat reset

  const handleNewChat = () => {
    setChatKey(prev => prev + 1);
  };

  const handleModelChange = (model: string) => {
    setSelectedModel(model);
  };

  const handleApiKeyChange = (_apiKey: string) => {
    console.log('API key updated');
  };

  return (
    <ThemeProvider>
      <div className="h-screen bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex">
        <Sidebar
          onNewChat={handleNewChat}
          selectedModel={selectedModel}
          onModelChange={handleModelChange}
          onApiKeyChange={handleApiKeyChange}
        />
        <Chat key={chatKey} selectedModel={selectedModel} />
      </div>
    </ThemeProvider>
  );
}

export default App
