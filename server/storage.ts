import { users, videoSeries, episodes, type User, type InsertUser, type VideoSeries, type InsertVideoSeries, type Episode, type InsertEpisode } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  createVideoSeries(series: InsertVideoSeries): Promise<VideoSeries>;
  getVideoSeries(id: number): Promise<VideoSeries | undefined>;
  getVideoSeriesByUserId(userId: number): Promise<VideoSeries[]>;
  updateVideoSeriesStatus(id: number, status: string, progress: number): Promise<void>;
  updateVideoSeriesTitle(id: number, title: string): Promise<void>;
  
  createEpisode(episode: InsertEpisode): Promise<Episode>;
  getEpisodesBySeriesId(seriesId: number): Promise<Episode[]>;
  markEpisodeWatched(episodeId: number, watched: boolean): Promise<void>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private videoSeries: Map<number, VideoSeries>;
  private episodes: Map<number, Episode>;
  private currentUserId: number;
  private currentSeriesId: number;
  private currentEpisodeId: number;

  constructor() {
    this.users = new Map();
    this.videoSeries = new Map();
    this.episodes = new Map();
    this.currentUserId = 1;
    this.currentSeriesId = 1;
    this.currentEpisodeId = 1;

    // Create a default user
    this.createUser({ username: "demo", password: "demo" });
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createVideoSeries(insertSeries: InsertVideoSeries): Promise<VideoSeries> {
    const id = this.currentSeriesId++;
    const series: VideoSeries = {
      ...insertSeries,
      id,
      status: "generating",
      progress: 0,
      createdAt: new Date(),
    };
    this.videoSeries.set(id, series);
    return series;
  }

  async getVideoSeries(id: number): Promise<VideoSeries | undefined> {
    return this.videoSeries.get(id);
  }

  async getVideoSeriesByUserId(userId: number): Promise<VideoSeries[]> {
    return Array.from(this.videoSeries.values())
      .filter(series => series.userId === userId)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async updateVideoSeriesStatus(id: number, status: string, progress: number): Promise<void> {
    const series = this.videoSeries.get(id);
    if (series) {
      this.videoSeries.set(id, { ...series, status, progress });
    }
  }

  async updateVideoSeriesTitle(id: number, title: string): Promise<void> {
    const series = this.videoSeries.get(id);
    if (series) {
      this.videoSeries.set(id, { ...series, title });
    }
  }

  async createEpisode(insertEpisode: InsertEpisode): Promise<Episode> {
    const id = this.currentEpisodeId++;
    const episode: Episode = {
      ...insertEpisode,
      id,
      isWatched: false,
      createdAt: new Date(),
    };
    this.episodes.set(id, episode);
    return episode;
  }

  async getEpisodesBySeriesId(seriesId: number): Promise<Episode[]> {
    return Array.from(this.episodes.values())
      .filter(episode => episode.seriesId === seriesId)
      .sort((a, b) => a.episodeNumber - b.episodeNumber);
  }

  async markEpisodeWatched(episodeId: number, watched: boolean): Promise<void> {
    const episode = this.episodes.get(episodeId);
    if (episode) {
      this.episodes.set(episodeId, { ...episode, isWatched: watched });
    }
  }
}

export const storage = new MemStorage();
