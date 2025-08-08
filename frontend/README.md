# ChatGPT Clone Frontend

A modern, minimalist React frontend application that interfaces with an OpenAI-compatible backend API to provide a ChatGPT-like conversational interface.

## Features

- **💬 Real-time Chat Interface**: Streaming responses with typing indicators
- **🌓 Dark/Light Mode**: Toggle between themes with dark mode as default
- **🎨 Minimalist Design**: Clean, responsive UI inspired by ChatGPT
- **🔧 Model Selection**: Choose from available AI models
- **🔐 API Key Management**: Secure API key configuration
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **⚡ Real-time Streaming**: Stream responses as they're generated
- **🎯 TypeScript**: Fully typed for better development experience

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety and better developer experience
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **OpenAI SDK** - Official OpenAI JavaScript/TypeScript SDK
- **Lucide React** - Beautiful icon library
- **UUID** - Generate unique identifiers for messages

## Prerequisites

- Node.js 18+ and npm
- Backend API server running (see `/backend` folder)
- Valid API key for the backend service

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment variables:**
   Copy the `.env` file and update the values:
   ```bash
   cp .env .env.local
   ```
   
   Update the following variables in `.env.local`:
   ```
   VITE_BACKEND_URL=http://localhost:8000
   VITE_DEFAULT_API_KEY=your-api-key
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5173`

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
| `npm run type-check` | Run TypeScript compiler check |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_BACKEND_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_DEFAULT_API_KEY` | Default API key | `your-api-key` |

### Backend API Endpoints

The frontend communicates with the following backend endpoints:

- `GET /v1/models` - List available AI models
- `POST /v1/chat/completions` - Create chat completions (streaming and non-streaming)
- `GET /health` - Health check endpoint
- `GET /metrics` - Metrics endpoint

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # React components
│   │   ├── Chat.tsx      # Main chat interface
│   │   ├── ChatInput.tsx # Message input component
│   │   ├── ChatMessage.tsx # Individual message component
│   │   └── Sidebar.tsx   # Sidebar with settings
│   ├── contexts/         # React contexts
│   │   └── ThemeContext.tsx # Dark/light mode context
│   ├── lib/              # Utilities and API client
│   │   └── api.ts        # Backend API client
│   ├── App.tsx           # Main app component
│   ├── main.tsx          # Application entry point
│   ├── index.css         # Global styles
│   └── vite-env.d.ts     # TypeScript declarations
├── .env                  # Environment variables template
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
├── tsconfig.json         # TypeScript configuration
├── vite.config.ts        # Vite configuration
└── package.json          # Dependencies and scripts
```

## Components Overview

### Chat.tsx
Main chat interface component that manages:
- Message history
- Streaming responses
- Message sending and abort functionality
- Integration with the API client

### ChatInput.tsx
Message input component featuring:
- Auto-resizing textarea
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Send/Stop button states
- Input validation

### ChatMessage.tsx
Individual message display component with:
- User/Assistant message differentiation
- Avatar icons
- Formatted message content
- Proper spacing and styling

### Sidebar.tsx
Navigation and settings sidebar including:
- New chat functionality
- Model selection dropdown
- API key configuration
- Dark/light mode toggle
- Settings panel

### ThemeContext.tsx
Theme management context providing:
- Theme state management
- Theme persistence in localStorage
- System theme detection
- Dark mode as default

## API Integration

The application uses the OpenAI SDK configured to communicate with your backend API. The `BackendAPIClient` class provides:

- **Model listing**: Fetches available AI models
- **Chat completions**: Supports both streaming and non-streaming responses
- **Error handling**: Comprehensive error management
- **Configuration**: Dynamic API key and base URL configuration

### Key Features:

1. **Streaming Support**: Real-time message streaming for better user experience
2. **Error Recovery**: Graceful error handling with user-friendly messages
3. **Abort Controller**: Ability to cancel ongoing requests
4. **Type Safety**: Full TypeScript support with proper typing

## Styling and Theming

The application uses Tailwind CSS with a custom dark/light theme system:

- **Dark Mode**: Default theme with dark backgrounds and light text
- **Light Mode**: Clean light theme with dark text
- **Responsive Design**: Mobile-first approach with responsive breakpoints
- **Custom Colors**: Carefully chosen color palette for both themes
- **Accessibility**: Proper contrast ratios and focus states

## Development Guidelines

### Adding New Features

1. Create feature branch: `git checkout -b feature/feature-name`
2. Implement feature with proper TypeScript typing
3. Add appropriate error handling
4. Test in both dark and light modes
5. Ensure responsive design
6. Update documentation if needed

### Code Style

- Use TypeScript for all new code
- Follow React functional component patterns
- Use proper prop typing with interfaces
- Implement error boundaries where appropriate
- Follow naming conventions (PascalCase for components, camelCase for functions)

### Performance Considerations

- Components are optimized for re-rendering
- Proper key props for list items
- Efficient state management
- Lazy loading where applicable
- Optimized bundle size

## Troubleshooting

### Common Issues

1. **Backend Connection Issues**
   - Verify `VITE_BACKEND_URL` is correct
   - Ensure backend server is running
   - Check CORS configuration on backend

2. **API Key Issues**
   - Verify API key is correctly set in settings
   - Check backend logs for authentication errors
   - Ensure API key has proper permissions

3. **Build Issues**
   - Clear `node_modules` and reinstall: `rm -rf node_modules package-lock.json && npm install`
   - Check TypeScript errors: `npm run type-check`
   - Verify environment variables are set

4. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check PostCSS configuration
   - Verify all CSS imports are correct

### Debug Mode

Enable debug logging by setting:
```javascript
localStorage.setItem('debug', 'true');
```

## Security Considerations

- API keys are stored securely and not logged
- All user inputs are properly sanitized
- HTTPS is recommended for production deployments
- Environment variables are properly scoped (VITE_ prefix)

## Browser Support

- Chrome 90+
- Firefox 90+
- Safari 14+
- Edge 90+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of a private chat application. Please refer to the main project license.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review backend API documentation
3. Check browser console for errors
4. Verify environment configuration

## Deployment

### Production Build

```bash
# Build the application
npm run build

# Preview the build locally
npm run preview
```

### Environment Setup

For production deployment:

1. Set proper environment variables
2. Configure reverse proxy (nginx recommended)
3. Enable HTTPS
4. Set proper CORS policies
5. Configure proper caching headers

### Docker Deployment

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

Built with ❤️ using React, TypeScript, and Tailwind CSS.
