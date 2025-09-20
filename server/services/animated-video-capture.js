import puppeteer from 'puppeteer';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

/**
 * Captures animated HTML content as video using Puppeteer
 * This replaces the simple text overlay approach with actual browser rendering
 */
export class AnimatedVideoCapture {
  constructor() {
    this.browser = null;
  }

  async initialize() {
    if (!this.browser) {
      this.browser = await puppeteer.launch({
        headless: 'new',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu'
        ]
      });
    }
  }

  async captureVideoFromHTML(htmlPath, outputPath, duration) {
    await this.initialize();
    
    console.log(`Capturing animated video from HTML: ${htmlPath}`);
    
    const page = await this.browser.newPage();
    
    try {
      // Set viewport for consistent video dimensions
      await page.setViewport({
        width: 1920,
        height: 1080,
        deviceScaleFactor: 1
      });

      // Load the HTML file
      const htmlUrl = `file://${path.resolve(htmlPath)}`;
      await page.goto(htmlUrl, { waitUntil: 'networkidle0' });

      // Wait for scene to be ready
      try {
        await page.waitForFunction('window.sceneReady === true', { timeout: 10000 });
      } catch (error) {
        console.warn('Scene ready timeout, proceeding anyway...');
      }

      // Start video recording
      const tempVideoPath = outputPath.replace('.mp4', '_temp.mp4');
      
      await page.screencast({
        path: tempVideoPath,
        duration: duration * 1000, // Convert to milliseconds
        fps: 30
      });

      // Convert the screencast to proper MP4 format
      const ffmpegCommand = `ffmpeg -y -i "${tempVideoPath}" -c:v libx264 -pix_fmt yuv420p -r 30 "${outputPath}"`;
      console.log(`Converting screencast: ${ffmpegCommand}`);
      
      await execAsync(ffmpegCommand);

      // Clean up temp file
      if (fs.existsSync(tempVideoPath)) {
        fs.unlinkSync(tempVideoPath);
      }

      console.log(`Animated video captured successfully: ${outputPath}`);
      return outputPath;

    } catch (error) {
      console.error('Error capturing video:', error);
      throw error;
    } finally {
      await page.close();
    }
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
    }
  }
}
