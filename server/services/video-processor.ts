import fs from "fs";
import path from "path";
import { exec } from "child_process";
import { promisify } from "util";
// Define the interface locally since we're not importing from manim-generator anymore
interface ManimFile {
  fileName: string;
  filePath: string;
  fullCode: string;
}

const execAsync = promisify(exec);

export interface VideoResult {
  videoPath: string;
  videoUrl: string;
  duration: number;
}

export async function renderManimVideo(
  manimFile: ManimFile,
  seriesId: number,
  episodeNumber: number
): Promise<string> {
  try {
    console.log(`Rendering Manim video for ${manimFile.fileName}...`);
    
    // Create manim directory if it doesn't exist
    const manimDir = path.join(process.cwd(), 'server', 'manim');
    if (!fs.existsSync(manimDir)) {
      fs.mkdirSync(manimDir, { recursive: true });
    }
    
    // Write the Manim file
    const filePath = path.join(manimDir, manimFile.fileName);
    fs.writeFileSync(filePath, manimFile.fullCode);
    
    // Render the video using Manim
    const outputDir = path.join(process.cwd(), 'server', 'videos');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const sceneName = manimFile.fileName.replace('.py', '');
    // Use low quality without preview (-ql). Do not pass an explicit scene name to avoid mismatches; render first scene in file.
    const command = `manim -ql ${filePath} -o ${sceneName}`;
    
    console.log(`Executing: ${command}`);
    const { stdout, stderr } = await execAsync(command, { cwd: manimDir });
    
    if (stderr) {
      console.warn('Manim stderr:', stderr);
    }
    
    console.log('Manim stdout:', stdout);
    
    // Find the generated video file (try different quality settings)
    let videoFile = path.join(manimDir, 'media', 'videos', sceneName, '1080p60', `${sceneName}.mp4`);
    if (!fs.existsSync(videoFile)) {
      videoFile = path.join(manimDir, 'media', 'videos', sceneName, '480p15', `${sceneName}.mp4`);
    }
    if (!fs.existsSync(videoFile)) {
      videoFile = path.join(manimDir, 'media', 'videos', sceneName, '720p30', `${sceneName}.mp4`);
    }
    
    if (!fs.existsSync(videoFile)) {
      throw new Error(`Manim video file not found: ${videoFile}`);
    }
    
    // Move to our videos directory
    const finalVideoPath = path.join(outputDir, `${sceneName}.mp4`);
    fs.copyFileSync(videoFile, finalVideoPath);
    
    console.log(`Manim video rendered successfully: ${finalVideoPath}`);
    console.log(`Video duration: ${videoFile} -> ${finalVideoPath}`);
    
    // Verify the video was copied successfully
    if (!fs.existsSync(finalVideoPath)) {
      throw new Error(`Failed to copy video to final location: ${finalVideoPath}`);
    }
    
    return finalVideoPath;
    
  } catch (error) {
    console.error('Failed to render Manim video:', error);
    throw new Error(`Failed to render Manim video: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export async function combineAudioAndVideo(
  videoPath: string,
  audioPath: string,
  seriesId: number,
  episodeNumber: number
): Promise<VideoResult> {
  try {
    console.log(`Combining audio and video for series ${seriesId}, episode ${episodeNumber}...`);
    
    const outputDir = path.join(process.cwd(), 'server', 'final-videos');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const timestamp = Date.now();
    const outputFileName = `series-${seriesId}-episode-${episodeNumber}-${timestamp}.mp4`;
    const outputPath = path.join(outputDir, outputFileName);
    
    // Get audio duration
    const audioDurationCommand = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${audioPath}"`;
    const { stdout: audioDurationOutput } = await execAsync(audioDurationCommand);
    const audioDuration = parseFloat(audioDurationOutput.trim());
    console.log(`Audio duration: ${audioDuration}s`);

    // Get video duration
    const videoDurationCommand = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${videoPath}"`;
    const { stdout: videoDurationOutput } = await execAsync(videoDurationCommand);
    const videoDuration = parseFloat(videoDurationOutput.trim());
    console.log(`Video duration: ${videoDuration}s`);

    // Build filters and total duration so output never cuts off prematurely
    const audioLonger = audioDuration > videoDuration;
    const durationDiff = Math.max(0, (audioLonger ? audioDuration - videoDuration : videoDuration - audioDuration));
    const targetDuration = Math.max(audioDuration, videoDuration);

    // Video filter: always scale to even dimensions; if audio is longer, extend last frame to match
    const vf = audioLonger
      ? `scale=trunc(iw/2)*2:trunc(ih/2)*2,tpad=stop_mode=clone:stop_duration=${durationDiff.toFixed(3)}`
      : `scale=trunc(iw/2)*2:trunc(ih/2)*2`;

    // Audio filter: if video is longer, pad silence to match
    const af = audioLonger
      ? 'anull' // no-op when audio is already longer
      : `apad=pad_dur=${durationDiff.toFixed(3)}`;

    // Limit output to the intended max duration explicitly
    const command = `ffmpeg -i "${videoPath}" -i "${audioPath}" -c:v libx264 -c:a aac -vf "${vf}" -af "${af}" -t ${targetDuration.toFixed(3)} "${outputPath}"`;

    console.log(`Executing FFmpeg: ${command}`);
    const { stdout, stderr } = await execAsync(command);
    
    if (stderr) {
      console.warn('FFmpeg stderr:', stderr);
    }
    
    console.log('FFmpeg stdout:', stdout);
    
    if (!fs.existsSync(outputPath)) {
      throw new Error(`Combined video file not found: ${outputPath}`);
    }
    
    // Get final video duration
    const durationCommand = `ffprobe -v quiet -show_entries format=duration -of csv=p=0 "${outputPath}"`;
    const { stdout: durationOutput } = await execAsync(durationCommand);
    const duration = parseFloat(durationOutput.trim());
    
    console.log(`Video and audio combined successfully: ${outputPath} (duration: ${duration}s)`);
    console.log(`Final video URL: /api/video/${outputFileName}`);
    
    // Verify the final video file exists and has content
    const stats = fs.statSync(outputPath);
    console.log(`Final video file size: ${stats.size} bytes`);
    
    if (stats.size < 1000) {
      throw new Error(`Final video file is too small (${stats.size} bytes), indicating processing failure`);
    }
    
    return {
      videoPath: outputPath,
      videoUrl: `/api/video/${outputFileName}`,
      duration
    };
    
  } catch (error) {
    console.error('Failed to combine audio and video:', error);
    throw new Error(`Failed to combine audio and video: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export async function cleanupTempFiles(manimFile: ManimFile, videoPath: string): Promise<void> {
  try {
    // Clean up Manim file
    const manimFilePath = path.join(process.cwd(), 'server', 'manim', manimFile.fileName);
    if (fs.existsSync(manimFilePath)) {
      fs.unlinkSync(manimFilePath);
    }
    
    // Clean up intermediate video file
    if (fs.existsSync(videoPath)) {
      fs.unlinkSync(videoPath);
    }
    
    console.log('Temporary files cleaned up successfully');
  } catch (error) {
    console.warn('Failed to cleanup temp files:', error);
  }
} 