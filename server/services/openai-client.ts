import OpenAI from "openai";

// Create and export the OpenAI client instance
export const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY_ENV_VAR || "default_key" 
});

// Debug: Check if API key is loaded
console.log("OpenAI API Key loaded:", process.env.OPENAI_API_KEY ? "YES" : "NO");
if (process.env.OPENAI_API_KEY) {
  console.log("API Key starts with:", process.env.OPENAI_API_KEY.substring(0, 7) + "...");
}
