import { generateEducationalSeries } from "./educationalDemo.js";
import { generateAudioFromScript } from "./openai-tts.js";
import { ManimGenerator } from "./manim-generator.js";
import { ManimCodeValidator } from "./manim-validator.js";
import { generateUniqueTitle } from "./title-generator.js";
import { renderManimVideo, combineAudioAndVideo, cleanupTempFiles } from "./video-processor.js";
import { storage } from "../storage.js";
import fs from "fs";
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
      request.style,
      request.totalEpisodes,
      request.episodeDuration
    );
    
    const outline = demoContent.outline;
    const scripts = demoContent.scripts;

    // Generate a unique, intelligent series title based on the prompt/context
    const uniqueSeriesTitle = await generateUniqueTitle({
      topic: request.topic,
      subject: request.subject,
      style: request.style,
      difficultyLevel: request.difficultyLevel,
      scriptExcerpt: scripts[0]?.script
    });
    
    // Update series title
    await storage.updateVideoSeriesTitle(seriesId, uniqueSeriesTitle);
    updateProgress(30, "Educational content generated, creating episodes...");

    // Generate episodes using demo content
    const totalEpisodes = outline.episodes.length;
    for (let i = 0; i < totalEpisodes; i++) {
      const episode = outline.episodes[i];
      const script = scripts[i];
      // Generate a unique episode title for each script
      const uniqueEpisodeTitle = await generateUniqueTitle({
        topic: request.topic,
        subject: request.subject,
        style: request.style,
        difficultyLevel: request.difficultyLevel,
        scriptExcerpt: script.script
      });
      const progressStep = 30 + ((i + 1) / totalEpisodes) * 60;
      
      updateProgress(progressStep, `Creating episode ${i + 1}: ${episode.title}...`);

      // Generate audio from script
      const audioUrl = await generateAudioFromScript(
        script.script,
        script.title,
        seriesId,
        episode.episodeNumber
      );

      // Generate Manim code and render video
      updateProgress(progressStep + 5, `Generating Manim animation for episode ${i + 1}...`);
      
      const manimGenerator = new ManimGenerator();
      const manimCode = await manimGenerator.generateManimCode(uniqueSeriesTitle, uniqueEpisodeTitle, script.script);
      
      // Create the Manim file
      const fileName = `series-${seriesId}-episode-${episode.episodeNumber}-${Date.now()}.py`;
      const filePath = `server/manim/${fileName}`;
      
      // Extract the actual class name from the generated code
      const classNameMatch = manimCode.match(/class\s+(\w+)\s*\(/);
      const className = classNameMatch ? classNameMatch[1] : uniqueEpisodeTitle.replace(/[^a-zA-Z0-9]/g, '');
      
      const fullCode = `from manim import *
import numpy as np

${manimCode}

if __name__ == "__main__":
    scene = ${className}()
    scene.render()
`;
      
      const manimFile = { fileName, filePath, fullCode };
      
      // Try to render the video, with retry logic if it fails
      updateProgress(progressStep + 10, `Rendering video for episode ${i + 1}...`);
      let videoPath: string;
      let retryCount = 0;
      const maxRetries = 2;
      
      while (retryCount <= maxRetries) {
        try {
          videoPath = await renderManimVideo(manimFile, seriesId, episode.episodeNumber);
          break; // Success, exit the retry loop
        } catch (error) {
          retryCount++;
          if (retryCount > maxRetries) {
            throw error; // Give up after max retries
          }
          
          console.log(`Video rendering failed, attempt ${retryCount}/${maxRetries}. Error: ${error}`);
          updateProgress(progressStep + 10, `Video rendering failed, retrying with improved code (${retryCount}/${maxRetries})...`);
          
          // Use the validator to fix the code and try again
          const validator = new ManimCodeValidator();
          const validationResult = await validator.validateAndFix(manimCode);
          
          if (validationResult.fixedCode) {
            console.log('Code was fixed by validator, retrying...');
            
            // Update the Manim file with fixed code
            const fixedClassNameMatch = validationResult.fixedCode.match(/class\s+(\w+)\s*\(/);
            const fixedClassName = fixedClassNameMatch ? fixedClassNameMatch[1] : className;
            
            const fixedFullCode = `from manim import *
import numpy as np

${validationResult.fixedCode}

if __name__ == "__main__":
    scene = ${fixedClassName}()
    scene.render()
`;
            
            manimFile.fullCode = fixedFullCode;
            fs.writeFileSync(manimFile.filePath, fixedFullCode);
          }
        }
      }
      
      // Get audio file path
      const audioFileName = audioUrl.split('/').pop();
      const audioPath = `server/audio/${audioFileName}`;
      
      updateProgress(progressStep + 15, `Combining audio and video for episode ${i + 1}...`);
      const videoResult = await combineAudioAndVideo(
        videoPath,
        audioPath,
        seriesId,
        episode.episodeNumber
      );
      
      // Clean up temporary files
      await cleanupTempFiles(manimFile, videoPath);

      const episodeData: InsertEpisode = {
        seriesId,
        episodeNumber: episode.episodeNumber,
        title: uniqueEpisodeTitle,
        description: script.description,
        script: script.script,
        duration: script.duration,
        videoUrl: videoResult.videoUrl,
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