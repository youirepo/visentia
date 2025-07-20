# Visentia - AI-Powered Educational Video Generator

## Overview

Visentia is a modern web application that generates educational videos using GPT-4. Users can input a topic and receive a structured video with professional narration. The application features a clean, responsive interface built with React and a robust Express.js backend.

## Features

### MVP Single Video Generation
- **Clean Interface**: Simple 4-step process for video generation
- **GPT-4 Integration**: Uses OpenAI's GPT-4 for high-quality script generation
- **Style Selection**: 5 presentation styles (Engaging, Formal, Story-based, Visual, Conversational)
- **Varying Lengths**: 5 duration options from 2-15 minutes
- **Professional Narration**: ElevenLabs integration for audio generation
- **Adaptive UI**: Components that adapt for single vs multiple videos

### Technical Stack
- **Frontend**: React 18 with TypeScript, Tailwind CSS, shadcn/ui
- **Backend**: Node.js with Express.js, TypeScript
- **AI**: OpenAI GPT-4 for script generation
- **Audio**: ElevenLabs for text-to-speech
- **Database**: PostgreSQL with Drizzle ORM

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# OpenAI API Key (Required for GPT-4 script generation)
OPENAI_API_KEY=your_openai_api_key_here

# ElevenLabs API Key (Optional - for professional audio narration)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Database Configuration
DATABASE_URL=your_database_url_here
```

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Set Environment Variables**
   - Add your OpenAI API key to `.env`
   - Optionally add ElevenLabs API key for audio generation

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Access Application**
   - Open http://localhost:3000 in your browser

## GPT-4 Integration

The application uses GPT-4 for generating educational explainer scripts:

### Script Generation Process
1. **User Input**: User enters topic, selects style, depth, and duration
2. **GPT-4 Processing**: System sends structured prompt to GPT-4
3. **Script Creation**: GPT-4 generates engaging, educational script
4. **Audio Generation**: Script is converted to professional narration
5. **Video Delivery**: Complete educational video with transcript

### Prompt Structure
- **Hook**: Engaging opening to capture attention
- **Introduction**: Topic overview and learning objectives
- **Main Content**: Detailed explanations with examples
- **Conclusion**: Summary and key takeaways

### Style Guidelines
- **Engaging & Interactive**: Questions, scenarios, call-to-actions
- **Formal & Academic**: Precise terminology, structured explanations
- **Story-based Learning**: Narratives and real-world scenarios
- **Visual & Demonstrative**: Step-by-step processes
- **Conversational & Friendly**: Warm, approachable language

## API Endpoints

- `POST /api/generate-series` - Generate educational video
- `GET /api/generation-progress/:id` - Check generation progress
- `GET /api/series` - Get all video series
- `GET /api/series/:id/episodes` - Get episodes for a series

## Development

### Project Structure
```
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/         # Page components
│   │   └── hooks/         # Custom React hooks
├── server/                 # Express.js backend
│   ├── services/          # AI and business logic
│   └── routes/            # API routes
└── shared/                # Shared types and schemas
```

### Key Services
- `openai.ts` - GPT-4 script generation
- `elevenlabs.ts` - Audio narration
- `videoGeneration.ts` - Video generation orchestration
- `storage.ts` - Database operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details 