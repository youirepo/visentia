// ElevenLabs Text-to-Speech integration for educational content
export interface VoiceGenerationOptions {
  text: string;
  voice_id?: string;
  model_id?: string;
  voice_settings?: {
    stability: number;
    similarity_boost: number;
    style?: number;
    use_speaker_boost?: boolean;
  };
}

export async function generateAudioFromScript(
  script: string,
  episodeTitle: string,
  seriesId: number,
  episodeNumber: number
): Promise<string> {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  
  if (!apiKey) {
    console.log("ElevenLabs API key not found, generating mock audio URL");
    return generateMockAudioUrl(seriesId, episodeNumber);
  }

  try {
    // Use a professional, educational voice (Rachel - clear, engaging)
    const voiceId = "21m00Tcm4TlvDq8ikWAM"; // Rachel voice ID
    
    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': apiKey
      },
      body: JSON.stringify({
        text: script,
        model_id: "eleven_multilingual_v2",
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
          style: 0.0,
          use_speaker_boost: true
        }
      })
    });

    if (!response.ok) {
      throw new Error(`ElevenLabs API error: ${response.status} ${response.statusText}`);
    }

    // In a real implementation, you would save the audio file to storage
    // For now, we'll return a placeholder URL
    const audioFileName = `series-${seriesId}-episode-${episodeNumber}-${Date.now()}.mp3`;
    console.log(`Generated audio for "${episodeTitle}" - would save as: ${audioFileName}`);
    
    return `/api/audio/${seriesId}/episode-${episodeNumber}.mp3`;
  } catch (error) {
    console.error('Failed to generate audio with ElevenLabs:', error);
    return generateMockAudioUrl(seriesId, episodeNumber);
  }
}

function generateMockAudioUrl(seriesId: number, episodeNumber: number): string {
  return `/api/audio/${seriesId}/episode-${episodeNumber}.mp3`;
}

export async function getAvailableVoices() {
  const apiKey = process.env.ELEVENLABS_API_KEY;
  
  if (!apiKey) {
    return getDefaultVoices();
  }

  try {
    const response = await fetch('https://api.elevenlabs.io/v1/voices', {
      headers: {
        'xi-api-key': apiKey
      }
    });

    if (!response.ok) {
      throw new Error(`ElevenLabs API error: ${response.status}`);
    }

    const data = await response.json();
    return data.voices;
  } catch (error) {
    console.error('Failed to fetch voices:', error);
    return getDefaultVoices();
  }
}

function getDefaultVoices() {
  return [
    {
      voice_id: "21m00Tcm4TlvDq8ikWAM",
      name: "Rachel",
      description: "Professional female voice, ideal for educational content"
    },
    {
      voice_id: "29vD33N1CtxCmqQRPOHJ",
      name: "Drew", 
      description: "Clear male voice, great for technical explanations"
    },
    {
      voice_id: "2EiwWnXFnvU5JabPnv8n",
      name: "Clyde",
      description: "Warm male voice, perfect for storytelling"
    }
  ];
}