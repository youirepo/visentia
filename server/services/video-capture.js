#!/usr/bin/env node
/**
 * Video Capture Service using Puppeteer
 * Captures HTML scenes as MP4 videos with precise timing
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class VideoCaptureService {
    constructor() {
        this.browser = null;
        this.defaultOptions = {
            width: 1920,
            height: 1080,
            deviceScaleFactor: 1,
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        };
    }

    async initialize() {
        if (!this.browser) {
            try {
                this.browser = await puppeteer.launch(this.defaultOptions);
                console.log('Browser initialized successfully');
            } catch (error) {
                console.error('Failed to initialize browser:', error);
                throw error;
            }
        }
        return this.browser;
    }

    async captureScene(htmlPath, outputPath, duration, options = {}) {
        const browser = await this.initialize();
        const page = await browser.newPage();

        try {
            // Set viewport
            await page.setViewport({
                width: options.width || this.defaultOptions.width,
                height: options.height || this.defaultOptions.height,
                deviceScaleFactor: options.deviceScaleFactor || this.defaultOptions.deviceScaleFactor
            });

            // Load the HTML file
            const fileUrl = `file://${path.resolve(htmlPath)}`;
            console.log(`Loading HTML from: ${fileUrl}`);
            
            await page.goto(fileUrl, {
                waitUntil: 'networkidle0',
                timeout: 30000
            });

            // Wait for scene to be ready
            console.log('Waiting for scene to be ready...');
            try {
                await page.waitForFunction(() => window.sceneReady === true, {
                    timeout: 10000
                });
            } catch (error) {
                console.log('Scene ready timeout, proceeding anyway...');
                // Continue even if scene ready flag isn't set
            }

            console.log('Scene ready, capturing screenshots...');

            // Create a temporary directory for screenshots
            const tempDir = path.join(__dirname, '..', 'temp-screenshots');
            if (!fs.existsSync(tempDir)) {
                fs.mkdirSync(tempDir, { recursive: true });
            }

            const screenshotPrefix = path.join(tempDir, `frame_${Date.now()}`);
            const fps = 30;
            const totalFrames = Math.ceil(duration * fps);
            const frameInterval = 1000 / fps;

            console.log(`Capturing ${totalFrames} frames at ${fps} FPS...`);

            // Capture frames
            for (let i = 0; i < totalFrames; i++) {
                const screenshotPath = `${screenshotPrefix}_${i.toString().padStart(6, '0')}.png`;
                await page.screenshot({
                    path: screenshotPath,
                    type: 'png',
                    fullPage: false
                });
                
                // Wait for next frame
                if (i < totalFrames - 1) {
                    await page.waitForTimeout(frameInterval);
                }
            }

            await page.close();

            // Convert screenshots to video using FFmpeg
            const videoPath = path.resolve(outputPath);
            console.log('Converting screenshots to video...');
            
            const { exec } = await import('child_process');
            const { promisify } = await import('util');
            const execAsync = promisify(exec);

            const ffmpegCommand = `ffmpeg -y -framerate ${fps} -i "${screenshotPrefix}_%06d.png" -c:v libx264 -pix_fmt yuv420p "${videoPath}"`;
            
            await execAsync(ffmpegCommand);

            // Clean up screenshots
            console.log('Cleaning up temporary files...');
            for (let i = 0; i < totalFrames; i++) {
                const screenshotPath = `${screenshotPrefix}_${i.toString().padStart(6, '0')}.png`;
                if (fs.existsSync(screenshotPath)) {
                    fs.unlinkSync(screenshotPath);
                }
            }

            console.log(`Video captured: ${videoPath}`);
            return videoPath;

        } catch (error) {
            console.error('Video capture failed:', error);
            throw error;
        } finally {
            try {
                await page.close();
                await browser.close();
                this.browser = null;
            } catch (closeError) {
                console.error('Error closing browser:', closeError);
            }
        }
    }

    async captureMultipleScenes(scenes, outputDir, options = {}) {
        const results = [];
        
        for (const scene of scenes) {
            try {
                console.log(`Capturing scene ${scene.sceneNumber}: ${scene.title}`);
                
                const outputPath = path.join(outputDir, `scene-${scene.sceneNumber.toString().padStart(2, '0')}-${this.sanitizeFilename(scene.title)}.mp4`);
                
                const result = await this.captureScene(
                    scene.htmlPath,
                    outputPath,
                    scene.duration,
                    options
                );
                
                results.push({
                    sceneNumber: scene.sceneNumber,
                    title: scene.title,
                    videoPath: result,
                    duration: scene.duration
                });
                
            } catch (error) {
                console.error(`Failed to capture scene ${scene.sceneNumber}:`, error);
                throw error;
            }
        }
        
        return results;
    }

    async close() {
        if (this.browser) {
            await this.browser.close();
            this.browser = null;
        }
    }

    sanitizeFilename(filename) {
        return filename.replace(/[^\w\s-]/g, '').trim();
    }
}

// CLI usage
async function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 3) {
        console.log('Usage: node video-capture.js <html-path> <output-path> <duration> [options]');
        console.log('Example: node video-capture.js scene.html output.mp4 15.5');
        process.exit(1);
    }

    const [htmlPath, outputPath, duration] = args;
    const durationSeconds = parseFloat(duration);

    const captureService = new VideoCaptureService();

    try {
        await captureService.captureScene(htmlPath, outputPath, durationSeconds);
        console.log('Video capture completed successfully!');
    } catch (error) {
        console.error('Video capture failed:', error);
        process.exit(1);
    } finally {
        await captureService.close();
    }
}

// Export for use as module
export default VideoCaptureService;

// Run CLI if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
    main();
}