import OpenAI from "openai";
import fs from "fs";
import path from "path";

const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY || "default_key" 
});

export interface TTSOptions {
  text: string;
  voice?: "alloy" | "echo" | "fable" | "onyx" | "nova" | "shimmer";
  model?: "tts-1" | "tts-1-hd";
  speed?: number;
}

export async function generateAudioFromScript(
  script: string,
  episodeTitle: string,
  seriesId: number,
  episodeNumber: number
): Promise<string> {
  const apiKey = process.env.OPENAI_API_KEY;
  
  if (!apiKey) {
    console.log("OpenAI API key not found, generating mock audio URL");
    return generateMockAudioUrl(seriesId, episodeNumber);
  }

  try {
    console.log(`Generating audio for "${episodeTitle}" using OpenAI TTS...`);
    
    // Use OpenAI's TTS API
    const response = await openai.audio.speech.create({
      model: "tts-1",
      voice: "nova", // Clear, professional female voice
      input: script,
      speed: 1.0
    });

    if (!response.ok) {
      throw new Error(`OpenAI TTS API error: ${response.status} ${response.statusText}`);
    }

    // Convert the response to a buffer
    const audioBuffer = Buffer.from(await response.arrayBuffer());
    
    // Create the audio directory if it doesn't exist
    const audioDir = path.join(process.cwd(), 'server', 'audio');
    if (!fs.existsSync(audioDir)) {
      fs.mkdirSync(audioDir, { recursive: true });
    }
    
    // Save the audio file
    const audioFileName = `series-${seriesId}-episode-${episodeNumber}-${Date.now()}.mp3`;
    const audioFilePath = path.join(audioDir, audioFileName);
    fs.writeFileSync(audioFilePath, audioBuffer);
    
    console.log(`Generated audio for "${episodeTitle}" - saved as: ${audioFileName}`);
    
    return `/api/audio/${audioFileName}`;
  } catch (error) {
    console.error('Failed to generate audio with OpenAI TTS:', error);
    return generateMockAudioUrl(seriesId, episodeNumber);
  }
}

function generateMockAudioUrl(seriesId: number, episodeNumber: number): string {
  return `/api/audio/${seriesId}/episode-${episodeNumber}.mp3`;
}

export async function getAvailableVoices() {
  return [
    {
      voice_id: "alloy",
      name: "Alloy",
      description: "Clear, professional voice with slight warmth"
    },
    {
      voice_id: "echo", 
      name: "Echo",
      description: "Clear, professional male voice"
    },
    {
      voice_id: "fable",
      name: "Fable",
      description: "Warm, storytelling voice"
    },
    {
      voice_id: "onyx",
      name: "Onyx",
      description: "Deep, authoritative male voice"
    },
    {
      voice_id: "nova",
      name: "Nova",
      description: "Clear, engaging female voice - ideal for educational content"
    },
    {
      voice_id: "shimmer",
      name: "Shimmer", 
      description: "Bright, energetic voice"
    }
  ];
} 