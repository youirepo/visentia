import { jest } from '@jest/globals';

// Global test setup
beforeAll(() => {
  // Set test environment variables
  process.env.NODE_ENV = 'test';
  process.env.OPENAI_API_KEY = 'test-key';
  process.env.DATABASE_URL = 'test-database-url';
});

// Global test teardown
afterAll(() => {
  // Clean up any global test state
});

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: jest.fn(),
  debug: jest.fn(),
  info: jest.fn(),
  warn: jest.fn(),
  error: jest.fn(),
};

// Mock file system operations for tests
jest.mock('fs', () => ({
  ...jest.requireActual('fs'),
  promises: {
    ...jest.requireActual('fs').promises,
    writeFile: jest.fn(),
    readFile: jest.fn(),
    unlink: jest.fn(),
    stat: jest.fn(),
  },
  existsSync: jest.fn(),
  createReadStream: jest.fn(),
  createWriteStream: jest.fn(),
}));

// Mock path operations
jest.mock('path', () => ({
  ...jest.requireActual('path'),
  join: jest.fn((...args) => args.join('/')),
}));

// Global test utilities
global.testUtils = {
  // Helper to create mock OpenAI responses
  createMockOpenAIResponse: (content: string) => ({
    choices: [{ message: { content } }],
  }),
  
  // Helper to create mock video file info
  createMockVideoInfo: (duration: number, hasAudio: boolean = true) => ({
    duration,
    hasAudio,
    audioCodec: hasAudio ? 'aac' : undefined,
    videoCodec: 'h264',
    width: 1920,
    height: 1080,
  }),
  
  // Helper to create mock Manim code
  createMockManimCode: (fontSize: number = 48) => `
from manim import *

class TestScene(Scene):
    def construct(self):
        title = Text("Test Title", font_size=${fontSize}, color=WHITE)
        self.play(FadeIn(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)
  `,
  
  // Helper to create mock content
  createMockContent: (isComplete: boolean = true) => {
    if (isComplete) {
      return `This is a complete lesson about the topic. It covers all aspects thoroughly from basic concepts to advanced understanding. The content includes practical examples, detailed explanations, and concludes with a comprehensive summary of everything learned. This is not an introduction to a series - it's a complete standalone lesson.`;
    } else {
      return `In this series, we will learn about the topic. This episode introduces the basic concepts. In the next episode, we will cover more advanced topics. Stay tuned for the complete series.`;
    }
  },
};

// Type declarations for global test utilities
declare global {
  var testUtils: {
    createMockOpenAIResponse: (content: string) => any;
    createMockVideoInfo: (duration: number, hasAudio?: boolean) => any;
    createMockManimCode: (fontSize?: number) => string;
    createMockContent: (isComplete?: boolean) => string;
  };
}
