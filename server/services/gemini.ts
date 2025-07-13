import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export interface SeriesOutline {
  title: string;
  episodes: {
    episodeNumber: number;
    title: string;
    description: string;
    keyTopics: string[];
    estimatedDuration: string;
  }[];
}

export interface EpisodeScript {
  title: string;
  description: string;
  script: string;
  duration: string;
}

export async function generateSeriesOutline(
  topic: string,
  subject: string,
  difficultyLevel: string,
  style: string,
  totalEpisodes: string,
  episodeDuration: string
): Promise<SeriesOutline> {
  const isSingleVideo = totalEpisodes === "1 episode" || totalEpisodes.includes("1");
  
  const prompt = isSingleVideo 
    ? `Create a comprehensive educational video outline for the topic: "${topic}"

Subject: ${subject}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Target Duration: ${episodeDuration}

Generate a structured outline for a single educational video that includes:
1. A clear, engaging video title
2. A detailed breakdown with key topics, learning objectives, and estimated duration

Ensure the content is educational, well-structured, and appropriate for the specified difficulty level and style. The video should be self-contained and provide a complete learning experience.

Style Guidelines:
- Engaging and Interactive: Include questions, activities, and interactive elements
- Formal and Academic: Use precise terminology and structured explanations
- Story-based Learning: Frame concepts within narratives and real-world scenarios
- Visual and Demonstrative: Focus on visual explanations and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples

Respond with JSON in this exact format:
{
  "title": "Video Title",
  "episodes": [
    {
      "episodeNumber": 1,
      "title": "Video Title",
      "description": "Comprehensive description of what this video covers",
      "keyTopics": ["topic1", "topic2", "topic3"],
      "estimatedDuration": "${episodeDuration}"
    }
  ]
}`
    : `Create a comprehensive educational video series outline for the topic: "${topic}"

Subject: ${subject}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Number of Episodes: ${totalEpisodes}
Target Episode Duration: ${episodeDuration}

Generate a structured outline with:
1. A clear, engaging series title
2. Individual episode breakdown with titles, descriptions, key topics, and estimated duration

Ensure the content is educational, well-structured, and appropriate for the specified difficulty level and style. The episodes should build upon each other logically and create a complete learning experience.

Style Guidelines:
- Engaging and Interactive: Include questions, activities, and interactive elements
- Formal and Academic: Use precise terminology and structured explanations
- Story-based Learning: Frame concepts within narratives and real-world scenarios
- Visual and Demonstrative: Focus on visual explanations and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples

Respond with JSON in this exact format:
{
  "title": "Series Title",
  "episodes": [
    {
      "episodeNumber": 1,
      "title": "Episode Title",
      "description": "Brief description of what this episode covers",
      "keyTopics": ["topic1", "topic2", "topic3"],
      "estimatedDuration": "5-8 minutes"
    }
  ]
}`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "object",
          properties: {
            title: { type: "string" },
            episodes: {
              type: "array",
              items: {
                type: "object",
                properties: {
                  episodeNumber: { type: "number" },
                  title: { type: "string" },
                  description: { type: "string" },
                  keyTopics: {
                    type: "array",
                    items: { type: "string" }
                  },
                  estimatedDuration: { type: "string" }
                },
                required: ["episodeNumber", "title", "description", "keyTopics", "estimatedDuration"]
              }
            }
          },
          required: ["title", "episodes"]
        }
      },
      contents: prompt,
    });

    const result = JSON.parse(response.text || "{}");
    return result as SeriesOutline;
  } catch (error) {
    throw new Error(`Failed to generate series outline: ${(error as Error).message}`);
  }
}

export async function generateEpisodeScript(
  seriesTitle: string,
  episodeTitle: string,
  episodeDescription: string,
  keyTopics: string[],
  difficultyLevel: string,
  style: string,
  targetDuration: string
): Promise<EpisodeScript> {
  const isSingleVideo = seriesTitle === episodeTitle || !seriesTitle.includes("Series");
  
  const prompt = isSingleVideo
    ? `Create a detailed educational video script for:

Video: ${episodeTitle}
Description: ${episodeDescription}
Key Topics: ${keyTopics.join(", ")}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Target Duration: ${targetDuration}

Generate a comprehensive script for a single educational video that includes:
1. An engaging introduction that hooks the viewer
2. Clear explanations of key concepts with examples
3. Analogies and real-world applications appropriate for the difficulty level
4. Smooth transitions between topics
5. A conclusion that summarizes key points and provides next steps

The script should be conversational, educational, and suitable for voice narration. Make it engaging and easy to follow while maintaining educational rigor.

Style Guidelines:
- Engaging and Interactive: Include questions, activities, and interactive elements
- Formal and Academic: Use precise terminology and structured explanations
- Story-based Learning: Frame concepts within narratives and real-world scenarios
- Visual and Demonstrative: Focus on visual explanations and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples

Respond with JSON in this exact format:
{
  "title": "Video Title",
  "description": "Updated video description",
  "script": "Full narration script with clear sections and smooth flow",
  "duration": "Estimated duration"
}`
    : `Create a detailed educational video script for:

Series: ${seriesTitle}
Episode: ${episodeTitle}
Description: ${episodeDescription}
Key Topics: ${keyTopics.join(", ")}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Target Duration: ${targetDuration}

Generate a comprehensive script that includes:
1. An engaging introduction that hooks the viewer
2. Clear explanations of key concepts with examples
3. Analogies and real-world applications appropriate for the difficulty level
4. Smooth transitions between topics
5. A conclusion that summarizes key points and previews the next episode

The script should be conversational, educational, and suitable for voice narration. Make it engaging and easy to follow while maintaining educational rigor.

Style Guidelines:
- Engaging and Interactive: Include questions, activities, and interactive elements
- Formal and Academic: Use precise terminology and structured explanations
- Story-based Learning: Frame concepts within narratives and real-world scenarios
- Visual and Demonstrative: Focus on visual explanations and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples

Respond with JSON in this exact format:
{
  "title": "Episode Title",
  "description": "Updated episode description",
  "script": "Full narration script with clear sections and smooth flow",
  "duration": "Estimated duration"
}`;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-pro",
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: "object",
          properties: {
            title: { type: "string" },
            description: { type: "string" },
            script: { type: "string" },
            duration: { type: "string" }
          },
          required: ["title", "description", "script", "duration"]
        }
      },
      contents: prompt,
    });

    const result = JSON.parse(response.text || "{}");
    return result as EpisodeScript;
  } catch (error) {
    throw new Error(`Failed to generate episode script: ${(error as Error).message}`);
  }
}