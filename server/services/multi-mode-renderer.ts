import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import type { Scene, SceneBasedScript } from './scene-generator.js';
import { generateAudioFromScript } from './openai-tts.js';
import { AnimatedVideoCapture } from './animated-video-capture.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const execAsync = promisify(exec);

export interface RenderedSceneResult {
  sceneNumber: number;
  title: string;
  mode: string;
  audioPath: string;
  videoPath: string;
  duration: number;
  success: boolean;
  error?: string;
}

export interface MultiModeProcessingResult {
  scenes: RenderedSceneResult[];
  totalDuration: number;
  allSuccessful: boolean;
}

export class MultiModeRenderer {
  private outputDir: string;
  private tempDir: string;
  private videoCapture: AnimatedVideoCapture;

  constructor() {
    this.outputDir = path.join(process.cwd(), 'server', 'generated-scenes');
    this.tempDir = path.join(process.cwd(), 'server', 'temp-stitching');
    this.videoCapture = new AnimatedVideoCapture();
    
    // Ensure directories exist
    if (!fs.existsSync(this.outputDir)) {
      fs.mkdirSync(this.outputDir, { recursive: true });
    }
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir, { recursive: true });
    }
  }

  async processScenes(
    script: SceneBasedScript,
    seriesId: number,
    episodeNumber: number
  ): Promise<MultiModeProcessingResult> {
    console.log(`Processing ${script.scenes.length} scenes using multi-mode rendering`);
    
    const timestamp = Date.now();
    const processedScenes: RenderedSceneResult[] = [];
    let allSuccessful = true;

    // Process each scene based on its mode
    for (const scene of script.scenes) {
      try {
        console.log(`Processing scene ${scene.sceneNumber}/${script.scenes.length}: ${scene.title}`);
        
        // Generate audio for this scene
        const audioPath = await this.generateSceneAudio(scene, seriesId, episodeNumber, timestamp);
        const actualAudioDuration = await this.getAudioDuration(audioPath);
        
        // Route to appropriate renderer based on mode
        let videoPath: string;
        switch (scene.mode) {
          case 'math':
            videoPath = await this.renderWithManim(scene, seriesId, episodeNumber, timestamp, actualAudioDuration);
            break;
          case 'diagram':
            videoPath = await this.renderWithMermaid(scene, seriesId, episodeNumber, timestamp, actualAudioDuration);
            break;
          case 'html':
            videoPath = await this.renderWithHtml(scene, seriesId, episodeNumber, timestamp, actualAudioDuration);
            break;
          default:
            throw new Error(`Unknown rendering mode: ${scene.mode}`);
        }
        
        processedScenes.push({
          sceneNumber: scene.sceneNumber,
          title: scene.title,
          mode: scene.mode,
          audioPath,
          videoPath,
          duration: actualAudioDuration,
          success: true
        });
        
        console.log(`Scene ${scene.sceneNumber} processed successfully using ${scene.mode} mode`);
        
      } catch (error) {
        console.error(`Failed to process scene ${scene.sceneNumber} (${scene.mode} mode):`, error);
        allSuccessful = false;
        
        processedScenes.push({
          sceneNumber: scene.sceneNumber,
          title: scene.title,
          mode: scene.mode,
          audioPath: '',
          videoPath: '',
          duration: scene.duration,
          success: false,
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }

    return {
      scenes: processedScenes,
      totalDuration: script.totalDuration,
      allSuccessful
    };
  }

  private async generateSceneAudio(
    scene: Scene,
    seriesId: number,
    episodeNumber: number,
    timestamp: number
  ): Promise<string> {
    console.log(`Generating audio for "${scene.title}" using OpenAI TTS...`);
    
    const audioFileName = `series-${seriesId}-episode-${episodeNumber}-${timestamp}-scene-${scene.sceneNumber}.mp3`;
    const audioPath = path.join(process.cwd(), 'server', 'audio', audioFileName);
    
    await generateAudioFromScript(scene.narration, audioPath);
    
    console.log(`Generated audio for "${scene.title}" - saved as: ${audioFileName}`);
    return audioPath;
  }

  private async getAudioDuration(audioPath: string): Promise<number> {
    try {
      const command = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${audioPath}"`;
      const { stdout } = await execAsync(command);
      const duration = parseFloat(stdout.trim());
      console.log(`Scene audio duration: ${duration.toFixed(3)}s`);
      return duration;
    } catch (error) {
      console.error('Failed to get audio duration:', error);
      throw new Error(`Failed to get audio duration: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  async renderWithManim(
    scene: Scene,
    seriesId: number,
    episodeNumber: number,
    timestamp: number,
    duration: number
  ): Promise<string> {
    console.log(`Rendering scene "${scene.title}" with Manim (math mode)...`);
    
    // For now, fall back to HTML rendering since we removed Manim
    // In a real implementation, this would generate Manim Python code and render it
    console.log(`Note: Manim rendering not implemented, falling back to HTML mode`);
    return await this.renderWithHtml(scene, seriesId, episodeNumber, timestamp, duration);
  }

  async renderWithMermaid(
    scene: Scene,
    seriesId: number,
    episodeNumber: number,
    timestamp: number,
    duration: number
  ): Promise<string> {
    console.log(`Rendering scene "${scene.title}" with Mermaid (diagram mode)...`);
    
    // Create Mermaid diagram HTML with animations
    const htmlContent = this.generateMermaidHtml(scene, duration);
    const htmlFileName = `scene-${scene.sceneNumber.toString().padStart(2, '0')}-${this.sanitizeFilename(scene.title)}.html`;
    const htmlPath = path.join(this.outputDir, htmlFileName);
    
    fs.writeFileSync(htmlPath, htmlContent);
    
    // Generate video from HTML using animated video capture
    const videoFileName = `scene-${scene.sceneNumber}-${timestamp}.mp4`;
    const videoPath = path.join(this.outputDir, videoFileName);
    
    await this.videoCapture.captureVideoFromHTML(htmlPath, videoPath, duration);
    
    if (!fs.existsSync(videoPath)) {
      throw new Error(`Video file not generated: ${videoPath}`);
    }
    
    return videoPath;
  }

  async renderWithHtml(
    scene: Scene,
    seriesId: number,
    episodeNumber: number,
    timestamp: number,
    duration: number
  ): Promise<string> {
    console.log(`Rendering scene "${scene.title}" with HTML (html mode)...`);
    
    // Create HTML content with animations
    const htmlContent = this.generateHtmlContent(scene, duration);
    const htmlFileName = `scene-${scene.sceneNumber.toString().padStart(2, '0')}-${this.sanitizeFilename(scene.title)}.html`;
    const htmlPath = path.join(this.outputDir, htmlFileName);
    
    fs.writeFileSync(htmlPath, htmlContent);
    
    // Generate video from HTML using animated video capture
    const videoFileName = `scene-${scene.sceneNumber}-${timestamp}.mp4`;
    const videoPath = path.join(this.outputDir, videoFileName);
    
    await this.videoCapture.captureVideoFromHTML(htmlPath, videoPath, duration);
    
    if (!fs.existsSync(videoPath)) {
      throw new Error(`Video file not generated: ${videoPath}`);
    }
    
    return videoPath;
  }

  private generateMermaidHtml(scene: Scene, duration: number): string {
    // Generate a simple Mermaid diagram based on scene content
    const mermaidCode = this.generateMermaidDiagram(scene);
    
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${scene.title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: white;
            overflow: hidden;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            animation: slideInUp 1s ease-out;
        }
        h1 {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            animation: fadeInScale 1.5s ease-out;
        }
        .mermaid {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            animation: fadeIn 2s ease-out 0.5s both;
            transform: scale(0.8);
            animation: scaleIn 2s ease-out 0.5s both;
        }
        .content {
            text-align: center;
            margin-top: 1rem;
            font-size: 1.2rem;
            line-height: 1.6;
            animation: fadeInUp 2s ease-out 1s both;
        }
        .duration {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(0, 0, 0, 0.5);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            animation: fadeIn 1s ease-out;
        }
        
        /* Animations */
        @keyframes slideInUp {
            from {
                transform: translateY(100px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeInScale {
            from {
                transform: scale(0.5);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        @keyframes scaleIn {
            from {
                transform: scale(0.8);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        @keyframes fadeInUp {
            from {
                transform: translateY(30px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        /* Mermaid node animations */
        .mermaid .node rect {
            animation: pulse 2s ease-in-out infinite 2s;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
    </style>
</head>
<body>
    <div class="duration">${duration.toFixed(1)}s</div>
    <div class="container">
        <h1>${scene.title}</h1>
        <div class="mermaid">
            ${mermaidCode}
        </div>
        <div class="content">
            ${scene.narration}
        </div>
    </div>
    
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose'
        });
        
        // Set scene ready flag after animations start
        window.addEventListener('load', function() {
            setTimeout(() => {
                window.sceneReady = true;
            }, 2000); // Wait for initial animations to complete
        });
    </script>
</body>
</html>`;
  }

  private generateMermaidDiagram(scene: Scene): string {
    // Generate different diagram types based on scene content
    const title = scene.title.toLowerCase();
    
    if (title.includes('process') || title.includes('step')) {
      return `graph TD
    A[Start] --> B[Step 1]
    B --> C[Step 2]
    C --> D[Step 3]
    D --> E[End]`;
    } else if (title.includes('flow') || title.includes('decision')) {
      return `flowchart TD
    A[Input] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[Result]
    D --> E`;
    } else if (title.includes('relationship') || title.includes('connection')) {
      return `graph LR
    A[Element 1] --- B[Element 2]
    B --- C[Element 3]
    A --- C`;
    } else {
      // Default mathematical/educational diagram
      return `graph TD
    A[Concept A] --> B[Process]
    B --> C[Concept B]
    D[Supporting Info] --> B
    C --> E[Conclusion]`;
    }
  }

  private generateHtmlContent(scene: Scene, duration: number): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${scene.title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            color: white;
            overflow: hidden;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 3rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            text-align: center;
            max-width: 800px;
            animation: slideInUp 1s ease-out;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            animation: fadeInScale 1.5s ease-out;
        }
        .content {
            font-size: 1.5rem;
            line-height: 1.8;
            margin-bottom: 2rem;
            animation: fadeInUp 2s ease-out 0.5s both;
        }
        .visual-elements {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid #3498db;
            animation: slideInLeft 2s ease-out 1s both;
            position: relative;
        }
        .visual-elements::before {
            content: '';
            position: absolute;
            top: 0;
            left: -4px;
            width: 4px;
            height: 100%;
            background: linear-gradient(45deg, #3498db, #e74c3c, #f39c12, #27ae60);
            animation: colorShift 3s ease-in-out infinite;
        }
        .duration {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(0, 0, 0, 0.5);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            animation: fadeIn 1s ease-out;
        }
        
        /* Animations */
        @keyframes slideInUp {
            from {
                transform: translateY(100px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeInScale {
            from {
                transform: scale(0.5);
                opacity: 0;
            }
            to {
                transform: scale(1);
                opacity: 1;
            }
        }
        
        @keyframes fadeInUp {
            from {
                transform: translateY(30px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        @keyframes slideInLeft {
            from {
                transform: translateX(-50px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes colorShift {
            0% { background: #3498db; }
            25% { background: #e74c3c; }
            50% { background: #f39c12; }
            75% { background: #27ae60; }
            100% { background: #3498db; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Text animation */
        .content {
            animation: typewriter 3s steps(40) 0.5s both, blink 1s infinite 3.5s;
        }
        
        @keyframes typewriter {
            from { width: 0; }
            to { width: 100%; }
        }
        
        @keyframes blink {
            0%, 50% { border-right: 2px solid white; }
            51%, 100% { border-right: none; }
        }
    </style>
</head>
<body>
    <div class="duration">${duration.toFixed(1)}s</div>
    <div class="container">
        <h1>${scene.title}</h1>
        <div class="content">
            ${scene.narration}
        </div>
        <div class="visual-elements">
            <strong>Visual Elements:</strong><br>
            ${scene.visualElements.join(', ')}
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script>
        // Set scene ready flag after animations start
        window.addEventListener('load', function() {
            setTimeout(() => {
                window.sceneReady = true;
            }, 2000); // Wait for initial animations to complete
        });
    </script>
</body>
</html>`;
  }

  private sanitizeFilename(filename: string): string {
    return filename.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
  }

  async cleanup() {
    if (this.videoCapture) {
      await this.videoCapture.close();
    }
  }

  async stitchScenes(
    processedScenes: RenderedSceneResult[],
    seriesId: number,
    episodeNumber: number
  ): Promise<string> {
    console.log(`Stitching ${processedScenes.length} scenes together`);
    
    // Only stitch successful scenes
    const successfulScenes = processedScenes.filter(scene => scene.success);
    
    if (successfulScenes.length === 0) {
      throw new Error('No successful scenes to stitch together');
    }
    
    if (successfulScenes.length !== processedScenes.length) {
      console.warn(`Only stitching ${successfulScenes.length} out of ${processedScenes.length} scenes due to failures`);
    }
    
    const timestamp = Date.now();
    
    // Sync each scene's audio and video
    for (const scene of successfulScenes) {
      console.log(`Syncing scene ${scene.sceneNumber}: ${scene.title}`);
      
      const syncedVideoPath = path.join(this.tempDir, `scene-${scene.sceneNumber}-synced.mp4`);
      
      const syncCommand = `ffmpeg -y -i "${scene.videoPath}" -i "${scene.audioPath}" -c:v libx264 -c:a aac -shortest "${syncedVideoPath}"`;
      console.log(`Syncing scene ${scene.sceneNumber}: ${syncCommand}`);
      
      await execAsync(syncCommand);
    }
    
    // Create file list for concatenation
    const fileListPath = path.join(this.tempDir, 'filelist.txt');
    const fileListContent = successfulScenes
      .map(scene => `file 'scene-${scene.sceneNumber}-synced.mp4'`)
      .join('\n');
    
    fs.writeFileSync(fileListPath, fileListContent);
    
    // Concatenate all scenes
    const finalVideoPath = path.join(process.cwd(), 'server', 'final-videos', `series-${seriesId}-episode-${episodeNumber}-${timestamp}.mp4`);
    
    const concatCommand = `ffmpeg -f concat -safe 0 -i "${fileListPath}" -c copy "${finalVideoPath}"`;
    console.log(`Concatenating scenes: ${concatCommand}`);
    
    await execAsync(concatCommand);
    
    console.log(`Successfully stitched ${successfulScenes.length} scenes into: ${finalVideoPath}`);
    return finalVideoPath;
  }
}
