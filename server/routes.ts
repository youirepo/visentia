import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage.js";
import { videoGenerationRequestSchema } from "@shared/schema";
import { startVideoGeneration, getGenerationProgress } from "./services/videoGeneration.js";

export async function registerRoutes(app: Express): Promise<Server> {
  // Generate video series
  app.post("/api/generate-series", async (req, res) => {
    try {
      const validatedData = videoGenerationRequestSchema.parse(req.body);
      const result = await startVideoGeneration(validatedData);
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
      const progress = getGenerationProgress(seriesId);
      
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

  const httpServer = createServer(app);
  return httpServer;
}
