import OpenAI from "openai";

// Debug: Check if API key is loaded
console.log("OpenAI API Key loaded:", process.env.OPENAI_API_KEY ? "YES" : "NO");
if (process.env.OPENAI_API_KEY) {
  console.log("API Key starts with:", process.env.OPENAI_API_KEY.substring(0, 7) + "...");
}

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

Generate a structured outline for a single educational explainer video that includes:
1. A clear, engaging video title that captures the essence of the topic
2. A detailed breakdown with key topics, learning objectives, and estimated duration

The video should be a complete, self-contained educational experience that:
- Introduces the concept clearly and engagingly
- Explains key principles with examples and analogies
- Provides practical applications or real-world connections
- Summarizes main points and reinforces learning

Style Guidelines:
- Engaging and Interactive: Include rhetorical questions, call-to-actions, and interactive elements
- Formal and Academic: Use precise terminology, structured explanations, and scholarly tone
- Story-based Learning: Frame concepts within narratives, case studies, or real-world scenarios
- Visual and Demonstrative: Focus on visual explanations, step-by-step processes, and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples and casual tone

Respond with JSON in this exact format:
{
  "title": "Video Title",
  "episodes": [
    {
      "episodeNumber": 1,
      "title": "Video Title",
      "description": "Comprehensive description of what this video covers and how it will teach the concept",
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
1. A clear series title that reflects the educational journey
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
  style: string,
  targetDuration: string
): Promise<EpisodeScript> {
  const isSingleVideo = seriesTitle === episodeTitle || !seriesTitle.includes("Series");
  
  const prompt = isSingleVideo
    ? `Create a detailed educational explainer video script for:

Video: ${episodeTitle}
Description: ${episodeDescription}
Key Topics: ${keyTopics.join(", ")}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Target Duration: ${targetDuration}

Generate a comprehensive explainer script that follows this structure:

1. HOOK (0:00-0:30): Start with an engaging hook that captures attention
   - Pose an intriguing question
   - Share a surprising fact or statistic
   - Present a relatable problem or scenario

2. INTRODUCTION (0:30-1:30): Introduce the topic and set expectations
   - Clearly state what the video will cover
   - Explain why this topic matters
   - Preview the key takeaways

3. MAIN CONTENT (1:30-end-1:00): Core educational content
   - Break down complex concepts into digestible parts
   - Use examples, analogies, and real-world applications
   - Include transitions between topics
   - Maintain engagement throughout

4. CONCLUSION (last 1:00): Wrap up and reinforce learning
   - Summarize key points
   - Provide actionable takeaways
   - End with a memorable closing thought

Style Guidelines:
- Engaging and Interactive: Include rhetorical questions, "imagine if..." scenarios, and call-to-actions
- Formal and Academic: Use precise terminology, structured explanations, and scholarly tone
- Story-based Learning: Frame concepts within narratives, case studies, or real-world scenarios
- Visual and Demonstrative: Focus on visual explanations, step-by-step processes, and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples and casual tone

The script should be:
- Conversational and suitable for voice narration
- Engaging and easy to follow
- Educational while maintaining entertainment value
- Appropriate for the specified difficulty level
- Structured to fit the target duration

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

The script should be conversational, educational, and suitable for voice narration. Include timing cues and ensure the content fits the target duration.

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

export async function generateExplainerScript(
  userPrompt: string,
  subject: string,
  difficultyLevel: string,
  style: string,
  targetDuration: string
): Promise<EpisodeScript> {
  const prompt = `Create a detailed educational explainer video script based on this user request: "${userPrompt}"

Subject: ${subject}
Difficulty Level: ${difficultyLevel}
Style: ${style}
Target Duration: ${targetDuration}

Generate a comprehensive explainer script that follows this structure:

1. HOOK (0:00-0:30): Start with an engaging hook that captures attention
   - Pose an intriguing question related to the topic
   - Share a surprising fact or statistic
   - Present a relatable problem or scenario

2. INTRODUCTION (0:30-1:30): Introduce the topic and set expectations
   - Clearly state what the video will cover
   - Explain why this topic matters to the viewer
   - Preview the key takeaways

3. MAIN CONTENT (1:30-end-1:00): Core educational content
   - Break down complex concepts into digestible parts
   - Use examples, analogies, and real-world applications
   - Include smooth transitions between topics
   - Maintain engagement throughout

4. CONCLUSION (last 1:00): Wrap up and reinforce learning
   - Summarize key points
   - Provide actionable takeaways
   - End with a memorable closing thought

Style Guidelines:
- Engaging and Interactive: Include rhetorical questions, "imagine if..." scenarios, and call-to-actions
- Formal and Academic: Use precise terminology, structured explanations, and scholarly tone
- Story-based Learning: Frame concepts within narratives, case studies, or real-world scenarios
- Visual and Demonstrative: Focus on visual explanations, step-by-step processes, and demonstrations
- Conversational and Friendly: Use warm, approachable language with relatable examples and casual tone

The script should be:
- Conversational and suitable for voice narration
- Engaging and easy to follow
- Educational while maintaining entertainment value
- Appropriate for the specified difficulty level
- Structured to fit the target duration
- Based directly on the user's prompt and requirements

Respond with JSON in this exact format:
{
  "title": "Video Title",
  "description": "Comprehensive description of the video content",
  "script": "Full narration script with clear sections and smooth flow",
  "duration": "Estimated duration"
}`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        {
          role: "system",
          content: "You are an expert educational script writer specializing in creating engaging explainer videos. You excel at breaking down complex topics into clear, entertaining, and educational content suitable for voice narration."
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
    throw new Error(`Failed to generate explainer script: ${(error as Error).message}`);
  }
}
