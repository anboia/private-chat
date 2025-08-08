import OpenAI from 'openai';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  id?: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  stream?: boolean;
  temperature?: number;
  max_tokens?: number;
}

export interface Model {
  id: string;
  object: string;
  created: number;
  owned_by: string;
}

export interface ModelsResponse {
  object: string;
  data: Model[];
}

class BackendAPIClient {
  private baseURL: string;
  private apiKey: string;
  private openai: OpenAI;

  constructor(
    baseURL: string = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000', 
    apiKey: string = import.meta.env.VITE_DEFAULT_API_KEY || 'your-api-key'
  ) {
    this.baseURL = baseURL;
    this.apiKey = apiKey;
    
    this.openai = new OpenAI({
      baseURL: `${this.baseURL}/v1`,
      apiKey: this.apiKey,
      dangerouslyAllowBrowser: true,
    });
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
    this.openai = new OpenAI({
      baseURL: `${this.baseURL}/v1`,
      apiKey: apiKey,
      dangerouslyAllowBrowser: true,
    });
  }

  async getModels(): Promise<ModelsResponse> {
    try {
      const response = await this.openai.models.list();
      return response as ModelsResponse;
    } catch (error) {
      console.error('Error fetching models:', error);
      throw error;
    }
  }

  async createChatCompletion(request: ChatCompletionRequest): Promise<OpenAI.Chat.Completions.ChatCompletion> {
    try {
      const response = await this.openai.chat.completions.create({
        model: request.model,
        messages: request.messages,
        stream: false,
        temperature: request.temperature,
        max_tokens: request.max_tokens,
      });
      return response;
    } catch (error) {
      console.error('Error creating chat completion:', error);
      throw error;
    }
  }

  async *createChatCompletionStream(request: ChatCompletionRequest): AsyncGenerator<OpenAI.Chat.Completions.ChatCompletionChunk> {
    try {
      const stream = await this.openai.chat.completions.create({
        model: request.model,
        messages: request.messages,
        stream: true,
        temperature: request.temperature,
        max_tokens: request.max_tokens,
      });

      for await (const chunk of stream) {
        yield chunk;
      }
    } catch (error) {
      console.error('Error creating streaming chat completion:', error);
      throw error;
    }
  }
}

export const apiClient = new BackendAPIClient();