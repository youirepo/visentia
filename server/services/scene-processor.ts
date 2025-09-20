import fs from "fs";
import path from "path";
import { exec } from "child_process";
import { promisify } from "util";
import { generateAudioFromScript } from "./openai-tts.js";
import { SceneManimGenerator } from "./scene-manim-generator.js";
import { renderManimVideo } from "./video-processor.js";
import type { Scene, SceneBasedScript } from "./scene-generator.js";

const execAsync = promisify(exec);

export interface ProcessedScene {
  sceneNumber: number;
  title: string;
  audioPath: string;
  videoPath: string;
  duration: number;
}

export interface SceneProcessingResult {
  scenes: ProcessedScene[];
  totalDuration: number;
}

export class SceneProcessor {
  private manimGenerator: SceneManimGenerator;

  constructor() {
    this.manimGenerator = new SceneManimGenerator();
  }

  async processScenes(
    script: SceneBasedScript,
    seriesId: number,
    episodeNumber: number
  ): Promise<SceneProcessingResult> {
    console.log(`Processing ${script.scenes.length} scenes for series ${seriesId}, episode ${episodeNumber}`);
    
    const processedScenes: ProcessedScene[] = [];
    const timestamp = Date.now();

    for (let i = 0; i < script.scenes.length; i++) {
      const scene = script.scenes[i];
      console.log(`Processing scene ${i + 1}/${script.scenes.length}: ${scene.title}`);
      
      try {
        // STEP 1: Generate audio for this scene FIRST
        const audioUrl = await generateAudioFromScript(
          scene.narration,
          scene.title,
          seriesId,
          episodeNumber
        );
        
        // STEP 2: Calculate exact audio duration using ffprobe
        const audioFileName = audioUrl.split('/').pop();
        const audioPath = path.join(process.cwd(), 'server', 'audio', audioFileName!);
        
        const audioDurationCommand = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${audioPath}"`;
        const { stdout: audioDurationOutput } = await execAsync(audioDurationCommand);
        const actualAudioDuration = parseFloat(audioDurationOutput.trim());
        
        console.log(`Scene ${scene.sceneNumber} actual audio duration: ${actualAudioDuration}s`);
        
        // STEP 3: Create updated scene with actual audio duration
        const timedScene = {
          ...scene,
          duration: actualAudioDuration
        };
        
        // STEP 4: Generate Manim code with exact audio duration for perfect timing
        const manimCode = await this.manimGenerator.generateSceneManimCode(
          timedScene,
          script.title,
          `Episode ${episodeNumber}`,
          3
        );
        
        // Create scene-specific file
        const sceneFileName = `series-${seriesId}-episode-${episodeNumber}-scene-${scene.sceneNumber}-${timestamp}.py`;
        const sceneFilePath = path.join(process.cwd(), 'server', 'manim', sceneFileName);
        
        // Extract class name and create full code
        const classNameMatch = manimCode.match(/class\s+(\w+)\s*\(/);
        const className = classNameMatch ? classNameMatch[1] : `Scene${scene.sceneNumber}`;
        
        const fullCode = `from manim import *
import numpy as np

${manimCode}

if __name__ == "__main__":
    scene = ${className}()
    scene.render()
`;
        
        const manimFile = {
          fileName: sceneFileName,
          filePath: sceneFilePath,
          fullCode
        };
        
        // STEP 5: Render the scene video with exact timing
        const videoPath = await renderManimVideo(manimFile, seriesId, episodeNumber);
        
        // STEP 6: Store scene data with actual audio duration
        processedScenes.push({
          sceneNumber: scene.sceneNumber,
          title: scene.title,
          audioPath,
          videoPath,
          duration: actualAudioDuration
        });
        
        console.log(`Scene ${scene.sceneNumber} processed successfully`);
        
      } catch (error) {
        console.error(`Failed to process scene ${scene.sceneNumber}:`, error);
        throw new Error(`Failed to process scene ${scene.sceneNumber}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    return {
      scenes: processedScenes,
      totalDuration: script.totalDuration
    };
  }

  async stitchScenes(
    processedScenes: ProcessedScene[],
    seriesId: number,
    episodeNumber: number
  ): Promise<string> {
    console.log(`Stitching ${processedScenes.length} scenes together`);
    
    const timestamp = Date.now();
    const outputDir = path.join(process.cwd(), 'server', 'final-videos');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const outputFileName = `series-${seriesId}-episode-${episodeNumber}-${timestamp}.mp4`;
    const outputPath = path.join(outputDir, outputFileName);
    
    // Create a temporary directory for intermediate files
    const tempDir = path.join(process.cwd(), 'server', 'temp-stitching');
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
    
    try {
      // Process each scene to sync audio and video
      const syncedScenePaths: string[] = [];
      
      for (let i = 0; i < processedScenes.length; i++) {
        const scene = processedScenes[i];
        console.log(`Syncing scene ${scene.sceneNumber}: ${scene.title}`);
        
        const syncedScenePath = path.join(tempDir, `scene-${scene.sceneNumber}-synced.mp4`);
        
        // Get durations
        const audioDurationCommand = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${scene.audioPath}"`;
        const { stdout: audioDurationOutput } = await execAsync(audioDurationCommand);
        const audioDuration = parseFloat(audioDurationOutput.trim());
        
        const videoDurationCommand = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${scene.videoPath}"`;
        const { stdout: videoDurationOutput } = await execAsync(videoDurationCommand);
        const videoDuration = parseFloat(videoDurationOutput.trim());
        
        console.log(`Scene ${scene.sceneNumber} durations - Audio: ${audioDuration}s, Video: ${videoDuration}s`);
        
        // Sync audio and video for this scene
        const audioLonger = audioDuration > videoDuration;
        const durationDiff = Math.max(0, Math.abs(audioDuration - videoDuration));
        const targetDuration = Math.max(audioDuration, videoDuration);
        
        const vf = audioLonger
          ? `scale=trunc(iw/2)*2:trunc(ih/2)*2,tpad=stop_mode=clone:stop_duration=${durationDiff.toFixed(3)}`
          : `scale=trunc(iw/2)*2:trunc(ih/2)*2`;
        
        const af = audioLonger
          ? 'anull'
          : `apad=pad_dur=${durationDiff.toFixed(3)}`;
        
        // Use -shortest to avoid trailing silence or black frames
        const syncCommand = `ffmpeg -i "${scene.videoPath}" -i "${scene.audioPath}" -c:v libx264 -c:a aac -vf "${vf}" -af "${af}" -shortest "${syncedScenePath}"`;
        
        console.log(`Syncing scene ${scene.sceneNumber}: ${syncCommand}`);
        await execAsync(syncCommand);
        
        syncedScenePaths.push(syncedScenePath);
      }
      
      // Create a file list for FFmpeg concatenation
      const fileListPath = path.join(tempDir, 'filelist.txt');
      const fileListContent = syncedScenePaths.map(p => `file '${p}'`).join('\n');
      fs.writeFileSync(fileListPath, fileListContent);
      
      // Concatenate all synced scenes
      const concatCommand = `ffmpeg -f concat -safe 0 -i "${fileListPath}" -c copy "${outputPath}"`;
      console.log(`Concatenating scenes: ${concatCommand}`);
      await execAsync(concatCommand);
      
      console.log(`Successfully stitched ${processedScenes.length} scenes into: ${outputPath}`);
      
      // Clean up temporary files
      for (const tempFile of syncedScenePaths) {
        if (fs.existsSync(tempFile)) {
          fs.unlinkSync(tempFile);
        }
      }
      if (fs.existsSync(fileListPath)) {
        fs.unlinkSync(fileListPath);
      }
      
      return outputPath;
      
    } catch (error) {
      console.error('Failed to stitch scenes:', error);
      throw new Error(`Failed to stitch scenes: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}
