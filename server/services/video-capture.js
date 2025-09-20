#!/usr/bin/env node
/**
 * Video Capture Service using Puppeteer
 * Captures HTML scenes as MP4 videos with precise timing
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

class VideoCaptureService {
    constructor() {
        this.browser = null;
        this.defaultOptions = {
            width: 1920,
            height: 1080,
            deviceScaleFactor: 1,
            headless: true,
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
            this.browser = await puppeteer.launch(this.defaultOptions);
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
            await page.waitForFunction(() => window.sceneReady === true, {
                timeout: 30000
            });

            console.log('Scene ready, starting video capture...');

            // Start screencast
            const videoPath = path.resolve(outputPath);
            await page.screencast({
                path: videoPath,
                format: 'mp4',
                everyNthFrame: 1
            });

            // Wait for the scene duration
            const waitTime = Math.ceil(duration * 1000);
            console.log(`Waiting for ${waitTime}ms (${duration}s)...`);
            await page.waitForTimeout(waitTime);

            // Stop screencast
            await page.screencast(null);

            console.log(`Video captured: ${videoPath}`);
            return videoPath;

        } catch (error) {
            console.error('Video capture failed:', error);
            throw error;
        } finally {
            await page.close();
        }
    }

    async captureMultipleScenes(scenes, outputDir, options = {}) {
        const results = [];
        
        for (const scene of scenes) {
            try {
                console.log(`Capturing scene ${scene.sceneNumber}: ${scene.title}`);
                
                const outputPath = path.join(outputDir, `scene-${scene.sceneNumber:02d}-${this.sanitizeFilename(scene.title)}.mp4`);
                
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
module.exports = VideoCaptureService;

// Run CLI if called directly
if (require.main === module) {
    main();
}

