import OpenAI from "openai";

// the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY || process.env.OPENAI_API_KEY_ENV_VAR || "default_key" 
});

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
  totalEpisodes: string,
  episodeDuration: string
): Promise<SeriesOutline> {
  const prompt = `Create a comprehensive educational video series outline for the topic: "${topic}"

Subject: ${subject}
Difficulty Level: ${difficultyLevel}
Number of Episodes: ${totalEpisodes}
Target Episode Duration: ${episodeDuration}

Generate a structured outline with:
1. A clear series title
2. Individual episode breakdown with titles, descriptions, key topics, and estimated duration

Ensure the content is educational, well-structured, and appropriate for the specified difficulty level. The episodes should build upon each other logically.

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
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: "You are an expert educational content creator. Create comprehensive, well-structured educational video series outlines."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      response_format: { type: "json_object" },
      temperature: 0.7,
    });

    const result = JSON.parse(response.choices[0].message.content || "{}");
    return result as SeriesOutline;
  } catch (error) {
    throw new Error(`Failed to generate series outline: ${error.message}`);
  }
}

export async function generateEpisodeScript(
  seriesTitle: string,
  episodeTitle: string,
  episodeDescription: string,
  keyTopics: string[],
  difficultyLevel: string,
  targetDuration: string
): Promise<EpisodeScript> {
  const prompt = `Create a detailed educational video script for:

Series: ${seriesTitle}
Episode: ${episodeTitle}
Description: ${episodeDescription}
Key Topics: ${keyTopics.join(", ")}
Difficulty Level: ${difficultyLevel}
Target Duration: ${targetDuration}

Generate a comprehensive script that includes:
1. An engaging introduction
2. Clear explanations of key concepts
3. Examples and analogies appropriate for the difficulty level
4. Smooth transitions between topics
5. A conclusion that summarizes key points

The script should be conversational, educational, and suitable for voice narration. Include timing cues and ensure the content fits the target duration.

Respond with JSON in this exact format:
{
  "title": "Episode Title",
  "description": "Updated episode description",
  "script": "Full narration script with clear sections and timing",
  "duration": "Estimated duration"
}`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: "You are an expert educational script writer. Create engaging, clear, and educational video scripts suitable for narration."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      response_format: { type: "json_object" },
      temperature: 0.7,
    });

    const result = JSON.parse(response.choices[0].message.content || "{}");
    return result as EpisodeScript;
  } catch (error) {
    throw new Error(`Failed to generate episode script: ${error.message}`);
  }
}
