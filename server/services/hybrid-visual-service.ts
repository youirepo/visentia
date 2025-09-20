import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import type { Scene, SceneBasedScript } from './scene-generator.js';
import { generateAudioFromScript } from './openai-tts.js';

const execAsync = promisify(exec);

export interface HybridSceneResult {
  sceneNumber: number;
  title: string;
  audioPath: string;
  videoPath: string;
  htmlPath: string;
  duration: number;
}

export interface HybridProcessingResult {
  scenes: HybridSceneResult[];
  totalDuration: number;
}

export class HybridVisualService {
  private outputDir: string;
  private pythonScriptPath: string;
  private nodeScriptPath: string;

  constructor() {
    this.outputDir = path.join(process.cwd(), 'server', 'generated-scenes');
    this.pythonScriptPath = path.join(process.cwd(), 'server', 'services', 'hybrid-visual-generator.py');
    this.nodeScriptPath = path.join(process.cwd(), 'server', 'services', 'video-capture.js');
    
    // Ensure output directory exists
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
  }

  async processScenes(
    script: SceneBasedScript,
    seriesId: number,
    episodeNumber: number
  ): Promise<HybridProcessingResult> {
    console.log(`Processing ${script.scenes.length} scenes using hybrid visual approach`);
    
    const processedScenes: HybridSceneResult[] = [];
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
        
        // STEP 4: Generate HTML using Python hybrid visual generator
        const htmlPath = await this.generateSceneHTML(timedScene, script.title, timestamp);
        
        // STEP 5: Generate video from HTML using Puppeteer
        const videoFileName = `scene-${scene.sceneNumber}-${timestamp}.mp4`;
        const videoPath = path.join(this.outputDir, videoFileName);
        
        await this.captureVideoFromHTML(htmlPath, videoPath, actualAudioDuration);
        
        // STEP 6: Store scene data with actual audio duration
        processedScenes.push({
          sceneNumber: scene.sceneNumber,
          title: scene.title,
          audioPath,
          videoPath,
          htmlPath,
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

  private async generateSceneHTML(
    scene: Scene,
    seriesTitle: string,
    timestamp: number
  ): Promise<string> {
    console.log(`Generating HTML for scene ${scene.sceneNumber}: ${scene.title}`);
    
    // Create scene data for Python script
    const sceneData = {
      sceneNumber: scene.sceneNumber,
      title: scene.title,
      description: scene.description,
      narration: scene.narration,
      duration: scene.duration,
      visualElements: scene.visualElements,
      animationType: scene.animationType
    };

    const seriesData = {
      title: seriesTitle,
      subject: "Mathematics", // This could be passed from the script
      difficulty_level: "Beginner",
      style: "Visual and Demonstrative"
    };

    // Write temporary data files for Python script
    const sceneDataPath = path.join(this.outputDir, `scene-${scene.sceneNumber}-${timestamp}-data.json`);
    const seriesDataPath = path.join(this.outputDir, `series-${timestamp}-data.json`);
    
    fs.writeFileSync(sceneDataPath, JSON.stringify(sceneData, null, 2));
    fs.writeFileSync(seriesDataPath, JSON.stringify(seriesData, null, 2));

    // Run Python script to generate HTML
    const pythonCommand = `python3 "${this.pythonScriptPath}" "${sceneDataPath}" "${seriesDataPath}" "${this.outputDir}"`;
    
    console.log(`Running Python script: ${pythonCommand}`);
    const { stdout, stderr } = await execAsync(pythonCommand);
    
    if (stderr) {
      console.warn('Python script stderr:', stderr);
    }
    
    console.log('Python script stdout:', stdout);
    
    // Expected HTML filename
    const htmlFileName = `scene-${scene.sceneNumber:02d}-${this.sanitizeFilename(scene.title)}.html`;
    const htmlPath = path.join(this.outputDir, htmlFileName);
    
    if (!fs.existsSync(htmlPath)) {
      throw new Error(`HTML file not generated: ${htmlPath}`);
    }
    
    // Clean up temporary data files
    try {
      fs.unlinkSync(sceneDataPath);
      fs.unlinkSync(seriesDataPath);
    } catch (error) {
      console.warn('Failed to clean up temporary files:', error);
    }
    
    return htmlPath;
  }

  private async captureVideoFromHTML(
    htmlPath: string,
    outputPath: string,
    duration: number
  ): Promise<string> {
    console.log(`Capturing video from HTML: ${htmlPath}`);
    
    // Run Node.js script to capture video
    const nodeCommand = `node "${this.nodeScriptPath}" "${htmlPath}" "${outputPath}" ${duration}`;
    
    console.log(`Running Node.js script: ${nodeCommand}`);
    const { stdout, stderr } = await execAsync(nodeCommand);
    
    if (stderr) {
      console.warn('Node.js script stderr:', stderr);
    }
    
    console.log('Node.js script stdout:', stdout);
    
    if (!fs.existsSync(outputPath)) {
      throw new Error(`Video file not generated: ${outputPath}`);
    }
    
    return outputPath;
  }

  async stitchScenes(
    processedScenes: HybridSceneResult[],
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
        
        // Sync audio and video for this scene using -shortest
        const syncCommand = `ffmpeg -i "${scene.videoPath}" -i "${scene.audioPath}" -c:v libx264 -c:a aac -shortest "${syncedScenePath}"`;
        
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

  private sanitizeFilename(filename: string): string {
    return filename.replace(/[^\w\s-]/g, '').trim();
  }
}

