# EduVideoAI - AI-Powered Educational Video Series Generator

## Overview

EduVideoAI is a modern web application that generates educational video series using AI. Users can input a topic and receive a structured video series with scripts, episodes, and progress tracking. The application features a clean, responsive interface built with React and a robust Express.js backend with PostgreSQL integration.

## System Architecture

The application follows a modern full-stack architecture with clear separation between frontend and backend:

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: Wouter (lightweight router)
- **State Management**: TanStack Query (React Query) for server state
- **UI Components**: Radix UI with shadcn/ui design system
- **Styling**: Tailwind CSS with CSS variables for theming
- **Build Tool**: Vite for fast development and optimized builds

### Backend Architecture
- **Runtime**: Node.js with Express.js
- **Language**: TypeScript with ES modules
- **Database**: PostgreSQL with Drizzle ORM
- **Cloud Database**: Neon Database (serverless PostgreSQL)
- **API Design**: RESTful endpoints with structured error handling
- **Session Management**: PostgreSQL-based session storage

## Key Components

### Database Schema
The application uses three main entities:
- **Users**: Basic user management with username/password
- **Video Series**: Contains metadata about generated series (topic, difficulty, progress)
- **Episodes**: Individual episodes within a series with scripts and media URLs

### AI Integration
- **OpenAI Integration**: Uses GPT-4o for content generation
- **Series Generation**: Creates structured outlines and episode breakdowns
- **Script Generation**: Generates detailed scripts for each episode

### Storage Strategy
- **Development**: In-memory storage with MemStorage class
- **Production**: PostgreSQL with Drizzle ORM
- **Session Management**: PostgreSQL-based sessions with connect-pg-simple

### API Endpoints
- `POST /api/generate-series`: Start video series generation
- `GET /api/generation-progress/:seriesId`: Track generation progress
- `GET /api/series`: List user's video series
- `GET /api/series/:id`: Get specific series details
- `GET /api/series/:id/episodes`: Get episodes for a series

## Data Flow

1. **Content Creation**: User submits topic, subject, difficulty level, and preferences
2. **AI Processing**: OpenAI generates series outline and episode scripts
3. **Storage**: Series and episodes are stored in PostgreSQL
4. **Progress Tracking**: Real-time progress updates via polling
5. **Content Delivery**: Episodes are served with video player interface

## External Dependencies

### Core Dependencies
- **@neondatabase/serverless**: Serverless PostgreSQL connection
- **drizzle-orm**: Type-safe database ORM
- **@tanstack/react-query**: Server state management
- **@radix-ui/***: Accessible UI components
- **tailwindcss**: Utility-first CSS framework

### Development Tools
- **tsx**: TypeScript execution for development
- **esbuild**: Fast JavaScript bundler for production
- **vite**: Frontend build tool and dev server

### AI Services
- **OpenAI API**: Content generation and processing
- Requires `OPENAI_API_KEY` environment variable

## Deployment Strategy

### Development
- Vite dev server for frontend with HMR
- tsx for backend development with auto-restart
- Environment-based configuration

### Production Build
- Frontend: Vite builds to `dist/public`
- Backend: esbuild bundles to `dist/index.js`
- Single-server deployment with static file serving

### Database Management
- Drizzle migrations in `./migrations` directory
- Schema defined in `shared/schema.ts`
- Push-based schema updates with `db:push` command

### Environment Configuration
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API authentication
- `NODE_ENV`: Environment mode (development/production)

## Changelog
```
Changelog:
- June 27, 2025. Initial setup
```

## User Preferences
```
Preferred communication style: Simple, everyday language.
```