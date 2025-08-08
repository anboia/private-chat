import React, { useState, useEffect } from 'react';
import { Plus, Settings, Moon, Sun, Key } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { apiClient } from '../lib/api';
import type { Model } from '../lib/api';

interface SidebarProps {
  onNewChat: () => void;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onApiKeyChange: (apiKey: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  onNewChat, 
  selectedModel, 
  onModelChange,
  onApiKeyChange 
}) => {
  const { theme, toggleTheme } = useTheme();
  const [showSettings, setShowSettings] = useState(false);
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_DEFAULT_API_KEY || 'your-api-key');
  const [models, setModels] = useState<Model[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    setIsLoadingModels(true);
    try {
      const response = await apiClient.getModels();
      setModels(response.data || []);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setIsLoadingModels(false);
    }
  };

  const handleApiKeySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    apiClient.setApiKey(apiKey);
    onApiKeyChange(apiKey);
    loadModels(); // Reload models with new API key
  };

  return (
    <div className="w-64 bg-gray-900 dark:bg-gray-950 text-white flex flex-col h-full">
      <div className="p-4 border-b border-gray-700">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
        >
          <Plus size={16} />
          New Chat
        </button>
      </div>

      <div className="flex-1 p-4">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Model
          </label>
          <select
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={isLoadingModels}
            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoadingModels ? (
              <option>Loading models...</option>
            ) : models.length > 0 ? (
              models.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.id}
                </option>
              ))
            ) : (
              <option>No models available</option>
            )}
          </select>
        </div>
      </div>

      <div className="p-4 border-t border-gray-700 space-y-2">
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
        >
          <Settings size={16} />
          Settings
        </button>
        
        {showSettings && (
          <div className="mt-2 space-y-3">
            <form onSubmit={handleApiKeySubmit} className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">
                API Key
              </label>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="flex-1 px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  placeholder="Enter API key"
                />
                <button
                  type="submit"
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
                >
                  <Key size={14} />
                </button>
              </div>
            </form>
          </div>
        )}

        <button
          onClick={toggleTheme}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>
      </div>
    </div>
  );
};