// import { generateEducationalSeries } from "./educationalDemo.js";
import { generateSceneBasedScript } from "./scene-generator.js";
import { SceneProcessor } from "./scene-processor.js";
import { generateUniqueTitle } from "./title-generator.js";
import { storage } from "../storage.js";
import { optimizeScript } from "./script-optimizer.js";
import fs from "fs";
import path from "path";
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
    updateProgress(20, "Generating scene-based script...");
    
    // Generate scene-based script
    const sceneScript = await generateSceneBasedScript(
      request.topic,
      request.subject,
      request.difficultyLevel,
      request.style,
      request.episodeDuration
    );

    // Generate a unique, intelligent series title
    const uniqueSeriesTitle = await generateUniqueTitle({
      topic: request.topic,
      subject: request.subject,
      style: request.style,
      difficultyLevel: request.difficultyLevel,
      scriptExcerpt: sceneScript.scenes.map(s => s.narration).join(' ')
    });
    
    // Update series title
    await storage.updateVideoSeriesTitle(seriesId, uniqueSeriesTitle);
    updateProgress(30, "Scene script generated, processing scenes...");

    const episodeTitle = sceneScript.title;
    const progressStep = 40;
    
    updateProgress(progressStep, `Processing ${sceneScript.scenes.length} scenes: ${episodeTitle}...`);

    // Process all scenes
    const sceneProcessor = new SceneProcessor();
    const processedScenes = await sceneProcessor.processScenes(
      sceneScript,
      seriesId,
      1
    );
    
    updateProgress(progressStep + 40, "Stitching scenes together...");
    
    // Stitch all scenes together
    const finalVideoPath = await sceneProcessor.stitchScenes(
      processedScenes.scenes,
      seriesId,
      1
    );
    
    // Create video URL
    const videoFileName = finalVideoPath.split('/').pop();
    const videoUrl = `/api/video/${videoFileName}`;
    
    // Create audio URL (use first scene's audio as representative)
    const firstSceneAudioFileName = processedScenes.scenes[0].audioPath.split('/').pop();
    const audioUrl = `/api/audio/${firstSceneAudioFileName}`;
    
    // Create transcript from all scene narrations
    const transcript = sceneScript.scenes.map(s => `${s.title}: ${s.narration}`).join('\n\n');
    const transcriptPath = path.join(process.cwd(), 'server', 'transcripts', `series-${seriesId}-episode-1.txt`);
    const transcriptDir = path.dirname(transcriptPath);
    if (!fs.existsSync(transcriptDir)) {
      fs.mkdirSync(transcriptDir, { recursive: true });
    }
    fs.writeFileSync(transcriptPath, transcript);

    const episodeData: InsertEpisode = {
      seriesId,
      episodeNumber: 1,
      title: episodeTitle,
      description: sceneScript.scenes.map(s => s.description).join(' '),
      script: transcript,
      duration: sceneScript.totalDuration,
      videoUrl: videoUrl,
      audioUrl: audioUrl,
      transcriptUrl: `/api/transcripts/series-${seriesId}-episode-1.txt`
    };

    await storage.createEpisode(episodeData);

    // Complete generation
    updateProgress(100, "Scene-based video generation completed successfully!", 'completed');
    
  } catch (error) {
    console.error(`Educational content generation failed for series ${seriesId}:`, error);
    updateProgress(0, `Error: ${(error as Error).message}`, 'error');
  }
}

export function getGenerationProgress(seriesId: number) {
  return generationProgress.get(seriesId) || null;
}