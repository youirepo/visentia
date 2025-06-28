import { generateEducationalSeries } from "./educationalDemo.js";
import { generateAudioFromScript } from "./elevenlabs.js";
import { storage } from "../storage.js";
import type { VideoGenerationRequest, InsertVideoSeries, InsertEpisode } from "@shared/schema";

const generationProgress = new Map<number, {
  seriesId: number;
  progress: number;
  currentStep: string;
  status: 'generating' | 'completed' | 'error';
}>();

export async function generateEducationalSeriesDirectly(request: VideoGenerationRequest): Promise<{ seriesId: number }> {
  // Create series entry immediately
  const seriesData: InsertVideoSeries = {
    topic: request.topic,
    subject: request.subject,
    difficultyLevel: request.difficultyLevel,
    totalEpisodes: parseInt(request.totalEpisodes.split(' ')[0]) || 3,
    episodeDuration: request.episodeDuration,
    title: "Generating...",
  };

  const series = await storage.createVideoSeries(seriesData);

  // Start async generation without API dependency
  setImmediate(() => generateContentAsync(series.id, request));

  return { seriesId: series.id };
}

async function generateContentAsync(seriesId: number, request: VideoGenerationRequest) {
  const updateProgress = (progress: number, step: string, status: 'generating' | 'completed' | 'error' = 'generating') => {
    generationProgress.set(seriesId, {
      seriesId,
      progress,
      currentStep: step,
      status
    });
    storage.updateVideoSeriesStatus(seriesId, status === 'error' ? 'error' : status === 'completed' ? 'completed' : 'generating', progress);
  };

  try {
    updateProgress(20, "Generating comprehensive educational content...");
    
    // Use our educational demo content system
    const demoContent = generateEducationalSeries(
      request.topic,
      request.subject,
      request.difficultyLevel,
      request.totalEpisodes,
      request.episodeDuration
    );
    
    const outline = demoContent.outline;
    const scripts = demoContent.scripts;
    
    // Update series title
    await storage.updateVideoSeriesTitle(seriesId, outline.title);
    updateProgress(30, "Educational content generated, creating episodes...");

    // Generate episodes using demo content
    const totalEpisodes = outline.episodes.length;
    for (let i = 0; i < totalEpisodes; i++) {
      const episode = outline.episodes[i];
      const script = scripts[i];
      const progressStep = 30 + ((i + 1) / totalEpisodes) * 60;
      
      updateProgress(progressStep, `Creating episode ${i + 1}: ${episode.title}...`);

      // Generate audio from script
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
        videoUrl: null, // Educational content focuses on scripts and audio
        audioUrl: audioUrl,
        transcriptUrl: `/api/transcripts/${seriesId}/episode-${episode.episodeNumber}.txt`
      };

      await storage.createEpisode(episodeData);
    }

    // Complete generation
    updateProgress(100, "Educational series completed successfully!", 'completed');
    
  } catch (error) {
    console.error(`Educational content generation failed for series ${seriesId}:`, error);
    updateProgress(0, `Error: ${(error as Error).message}`, 'error');
  }
}

export function getGenerationProgress(seriesId: number) {
  return generationProgress.get(seriesId) || null;
}