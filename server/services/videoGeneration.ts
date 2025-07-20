import { generateSeriesOutline, generateEpisodeScript, generateExplainerScript } from "./openai.js";
import { generateEducationalSeries } from "./educationalDemo.js";
import { generateAudioFromScript } from "./openai-tts.js";
import { storage } from "../storage.js";
import type { VideoGenerationRequest, InsertVideoSeries, InsertEpisode } from "@shared/schema";

export interface GenerationProgress {
  seriesId: number;
  progress: number;
  currentStep: string;
  status: 'generating' | 'completed' | 'error';
}

// Store generation progress in memory (in production, use Redis or similar)
const generationProgress = new Map<number, GenerationProgress>();

export async function startVideoGeneration(
  request: VideoGenerationRequest,
  userId: number = 1 // Default user for demo
): Promise<{ seriesId: number }> {
  try {
    // Create initial series record
    const seriesData: InsertVideoSeries = {
      userId,
      title: request.topic,
      topic: request.topic,
      subject: request.subject,
      difficultyLevel: request.difficultyLevel,
      totalEpisodes: parseInt(request.totalEpisodes.split('-')[0]) || 3,
      episodeDuration: request.episodeDuration,
    };

    const series = await storage.createVideoSeries(seriesData);
    
    // Initialize progress tracking
    generationProgress.set(series.id, {
      seriesId: series.id,
      progress: 0,
      currentStep: "Analyzing topic and creating outline...",
      status: 'generating'
    });

    // Start generation process asynchronously
    generateVideoSeriesAsync(series.id, request).catch(error => {
      console.error(`Video generation failed for series ${series.id}:`, error);
      generationProgress.set(series.id, {
        seriesId: series.id,
        progress: 0,
        currentStep: `Error: ${(error as Error).message}`,
        status: 'error'
      });
      storage.updateVideoSeriesStatus(series.id, 'error', 0);
    });

    return { seriesId: series.id };
  } catch (error) {
    throw new Error(`Failed to start video generation: ${(error as Error).message}`);
  }
}

async function generateVideoSeriesAsync(seriesId: number, request: VideoGenerationRequest) {
  const updateProgress = (progress: number, step: string) => {
    generationProgress.set(seriesId, {
      seriesId,
      progress,
      currentStep: step,
      status: 'generating'
    });
    storage.updateVideoSeriesStatus(seriesId, 'generating', progress);
  };

  // Check if this is a single video request
  const isSingleVideo = request.totalEpisodes === "1 episode" || request.totalEpisodes.includes("1");

  try {
    // Step 1: Generate content outline (20% progress)
    updateProgress(20, isSingleVideo ? "Generating video content..." : "Generating series outline...");
    
    let outline, scripts;
    
    try {
      // Try GPT-4 API first for high-quality script generation
      console.log("Using GPT-4 for script generation...");
      
      if (isSingleVideo) {
        // For single videos, generate explainer script directly from user prompt
        updateProgress(30, "Generating explainer script from your prompt...");
        
        const script = await generateExplainerScript(
          request.topic,
          request.subject,
          request.difficultyLevel,
          request.style,
          request.episodeDuration
        );

        // Create a simple outline for single video
        outline = {
          title: script.title,
          episodes: [{
            episodeNumber: 1,
            title: script.title,
            description: script.description,
            keyTopics: [request.topic],
            estimatedDuration: script.duration
          }]
        };

        // Update series title
        await storage.updateVideoSeriesTitle(seriesId, script.title);

        // Generate audio from script using ElevenLabs
        updateProgress(70, "Generating audio narration for your video...");
        const audioUrl = await generateAudioFromScript(
          script.script,
          script.title,
          seriesId,
          1
        );

        const episodeData: InsertEpisode = {
          seriesId,
          episodeNumber: 1,
          title: script.title,
          description: script.description,
          script: script.script,
          duration: script.duration,
          videoUrl: null, // No video generation - scripts and audio only
          audioUrl: audioUrl,
          transcriptUrl: `/api/transcripts/${seriesId}/episode-1.txt`,
        };

        await storage.createEpisode(episodeData);
      } else {
        // For series, use the original outline and episode generation
        outline = await generateSeriesOutline(
          request.topic,
          request.subject,
          request.difficultyLevel,
          request.style,
          request.totalEpisodes,
          request.episodeDuration
        );

        // Update series title
        await storage.updateVideoSeriesTitle(seriesId, outline.title);

        // Step 2: Generate episode(s) using GPT-4 (20% -> 80% progress)
        const totalEpisodes = outline.episodes.length;
        for (let i = 0; i < totalEpisodes; i++) {
          const episode = outline.episodes[i];
          const progressStep = 20 + ((i + 1) / totalEpisodes) * 60;
          
          updateProgress(progressStep, `Generating episode ${i + 1} script: ${episode.title}...`);
          
          const script = await generateEpisodeScript(
            outline.title,
            episode.title,
            episode.description,
            episode.keyTopics,
            request.difficultyLevel,
            request.style,
            episode.estimatedDuration
          );

          // Generate audio from script using ElevenLabs
          updateProgress(progressStep + 5, `Generating audio narration for episode ${i + 1}...`);
          const audioUrl = await generateAudioFromScript(
            script.script,
            script.title,
            seriesId,
            episode.episodeNumber
          );

          const episodeData: InsertEpisode = {
            seriesId,
            episodeNumber: episode.episodeNumber,
            title: script.title,
            description: script.description,
            script: script.script,
            duration: script.duration,
            videoUrl: null, // No video generation - scripts and audio only
            audioUrl: audioUrl,
            transcriptUrl: `/api/transcripts/${seriesId}/episode-${episode.episodeNumber}.txt`,
          };

          await storage.createEpisode(episodeData);
        }
      }
    } catch (openaiError) {
      console.log("GPT-4 API error, falling back to educational demo content...", openaiError);
      
      // Use educational demo content when GPT-4 is unavailable
      const demoContent = generateEducationalSeries(
        request.topic,
        request.subject,
        request.difficultyLevel,
        request.style,
        request.totalEpisodes,
        request.episodeDuration
      );
      
      outline = demoContent.outline;
      scripts = demoContent.scripts;
      
      // Update series title
      await storage.updateVideoSeriesTitle(seriesId, outline.title);

      // Generate episodes using demo content
      const totalEpisodes = outline.episodes.length;
      for (let i = 0; i < totalEpisodes; i++) {
        const episode = outline.episodes[i];
        const script = scripts[i];
        const progressStep = 20 + ((i + 1) / totalEpisodes) * 60;
        
        updateProgress(progressStep, isSingleVideo 
          ? `Generating video: ${episode.title}...` 
          : `Generating episode ${i + 1}: ${episode.title}...`
        );

        // Generate audio from script
        updateProgress(progressStep + 5, isSingleVideo 
          ? `Generating audio for video...` 
          : `Generating audio for episode ${i + 1}...`
        );
        const audioUrl = await generateAudioFromScript(
          script.script,
          script.title,
          seriesId,
          episode.episodeNumber
        );

        const episodeData: InsertEpisode = {
          seriesId,
          episodeNumber: episode.episodeNumber,
          title: script.title,
          description: script.description,
          script: script.script,
          duration: script.duration,
          videoUrl: null, // No video generation - scripts and audio only
          audioUrl: audioUrl,
          transcriptUrl: `/api/transcripts/${seriesId}/episode-${episode.episodeNumber}.txt`,
        };

        await storage.createEpisode(episodeData);
      }
    }

    // Step 3: Finalize (100% progress)
    updateProgress(100, isSingleVideo ? "Video generation completed!" : "Video series generation completed!");
    generationProgress.set(seriesId, {
      seriesId,
      progress: 100,
      currentStep: isSingleVideo ? "Video generation completed successfully" : "Generation completed successfully",
      status: 'completed'
    });
    await storage.updateVideoSeriesStatus(seriesId, 'completed', 100);

  } catch (error) {
    console.error(`Video generation failed for series ${seriesId}:`, error);
    updateProgress(0, `Error: ${(error as Error).message}`);
    generationProgress.set(seriesId, {
      seriesId,
      progress: 0,
      currentStep: `Error: ${(error as Error).message}`,
      status: 'error'
    });
    await storage.updateVideoSeriesStatus(seriesId, 'error', 0);
  }
}

// Generate transcript file from script content
function generateTranscriptUrl(seriesId: number, episodeNumber: number, script: string): string {
  // In production, save script as downloadable transcript file
  return `/api/transcripts/${seriesId}/episode-${episodeNumber}.txt`;
}

export function getGenerationProgress(seriesId: number): GenerationProgress | null {
  return generationProgress.get(seriesId) || null;
}
