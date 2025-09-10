import type { Express } from "express";
import { createServer, type Server } from "http";
import fs from "fs";
import path from "path";
import { storage } from "./storage.js";
import { videoGenerationRequestSchema } from "@shared/schema";
import { generateEducationalSeriesDirectly, getGenerationProgress as getDirectProgress } from "./services/directGeneration.js";

export async function registerRoutes(app: Express): Promise<Server> {
  // Generate video series
  app.post("/api/generate-series", async (req, res) => {
    try {
      const validatedData = videoGenerationRequestSchema.parse(req.body);
      const result = await generateEducationalSeriesDirectly(validatedData);
      res.json(result);
    } catch (error) {
      res.status(400).json({ 
        message: error.message || "Failed to start video generation" 
      });
    }
  });

  // Get generation progress
  app.get("/api/generation-progress/:seriesId", async (req, res) => {
    try {
      const seriesId = parseInt(req.params.seriesId);
      const progress = getDirectProgress(seriesId);
      
      if (!progress) {
        return res.status(404).json({ message: "Generation progress not found" });
      }
      
      res.json(progress);
    } catch (error) {
      res.status(500).json({ message: "Failed to get generation progress" });
    }
  });

  // Get user's video series
  app.get("/api/series", async (req, res) => {
    try {
      const userId = 1; // Default user for demo
      const series = await storage.getVideoSeriesByUserId(userId);
      res.json(series);
    } catch (error) {
      res.status(500).json({ message: "Failed to get video series" });
    }
  });

  // Get specific video series
  app.get("/api/series/:id", async (req, res) => {
    try {
      const seriesId = parseInt(req.params.id);
      const series = await storage.getVideoSeries(seriesId);
      
      if (!series) {
        return res.status(404).json({ message: "Video series not found" });
      }
      
      res.json(series);
    } catch (error) {
      res.status(500).json({ message: "Failed to get video series" });
    }
  });

  // Get episodes for a series
  app.get("/api/series/:id/episodes", async (req, res) => {
    try {
      const seriesId = parseInt(req.params.id);
      const episodes = await storage.getEpisodesBySeriesId(seriesId);
      res.json(episodes);
    } catch (error) {
      res.status(500).json({ message: "Failed to get episodes" });
    }
  });

  // Mark episode as watched
  app.patch("/api/episodes/:id/watched", async (req, res) => {
    try {
      const episodeId = parseInt(req.params.id);
      const { watched } = req.body;
      
      await storage.markEpisodeWatched(episodeId, watched);
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ message: "Failed to update episode status" });
    }
  });

  // Serve audio files
  app.get("/api/audio/:filename", (req, res) => {
    try {
      const { filename } = req.params;
      const audioPath = path.join(process.cwd(), 'server', 'audio', filename);
      
      if (!fs.existsSync(audioPath)) {
        return res.status(404).json({ message: "Audio file not found" });
      }
      
      res.setHeader('Content-Type', 'audio/mpeg');
      res.setHeader('Content-Disposition', `inline; filename="${filename}"`);
      fs.createReadStream(audioPath).pipe(res);
    } catch (error) {
      res.status(500).json({ message: "Failed to serve audio file" });
    }
  });

  // Handle CORS preflight for video files
  app.options("/api/video/:filename", (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Range');
    res.status(200).end();
  });

  // Serve video files
  app.get("/api/video/:filename", (req, res) => {
    try {
      const { filename } = req.params;
      const videoPath = path.join(process.cwd(), 'server', 'final-videos', filename);
      
      if (!fs.existsSync(videoPath)) {
        return res.status(404).json({ message: "Video file not found" });
      }
      
      const stat = fs.statSync(videoPath);
      const fileSize = stat.size;
      const range = req.headers.range;
      
      // Set CORS headers for video streaming
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, HEAD, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Range');
      
      if (range) {
        const parts = range.replace(/bytes=/, "").split("-");
        const start = parseInt(parts[0], 10);
        const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
        const chunksize = (end - start) + 1;
        const file = fs.createReadStream(videoPath, { start, end });
        const head = {
          'Content-Range': `bytes ${start}-${end}/${fileSize}`,
          'Accept-Ranges': 'bytes',
          'Content-Length': chunksize,
          'Content-Type': 'video/mp4',
          'Cache-Control': 'public, max-age=31536000',
        };
        res.writeHead(206, head);
        file.pipe(res);
      } else {
        const head = {
          'Content-Length': fileSize,
          'Content-Type': 'video/mp4',
          'Accept-Ranges': 'bytes',
          'Cache-Control': 'public, max-age=31536000',
        };
        res.writeHead(200, head);
        fs.createReadStream(videoPath).pipe(res);
      }
    } catch (error) {
      console.error('Error serving video:', error);
      res.status(500).json({ message: "Failed to serve video file" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
