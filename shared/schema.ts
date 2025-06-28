import { pgTable, text, serial, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const videoSeries = pgTable("video_series", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  title: text("title").notNull(),
  topic: text("topic").notNull(),
  subject: text("subject").notNull(),
  difficultyLevel: text("difficulty_level").notNull(),
  totalEpisodes: integer("total_episodes").notNull(),
  episodeDuration: text("episode_duration").notNull(),
  status: text("status").notNull().default("generating"), // generating, completed, error
  progress: integer("progress").notNull().default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const episodes = pgTable("episodes", {
  id: serial("id").primaryKey(),
  seriesId: integer("series_id").references(() => videoSeries.id).notNull(),
  episodeNumber: integer("episode_number").notNull(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  script: text("script").notNull(),
  duration: text("duration").notNull(),
  videoUrl: text("video_url"),
  audioUrl: text("audio_url"),
  transcriptUrl: text("transcript_url"),
  isWatched: boolean("is_watched").default(false),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertVideoSeriesSchema = createInsertSchema(videoSeries).omit({
  id: true,
  createdAt: true,
  status: true,
  progress: true,
});

export const insertEpisodeSchema = createInsertSchema(episodes).omit({
  id: true,
  createdAt: true,
  isWatched: true,
});

export const videoGenerationRequestSchema = z.object({
  topic: z.string().min(10, "Topic must be at least 10 characters"),
  subject: z.string().min(1, "Subject is required"),
  difficultyLevel: z.string().min(1, "Difficulty level is required"),
  totalEpisodes: z.string().min(1, "Number of episodes is required"),
  episodeDuration: z.string().min(1, "Episode duration is required"),
});

export type InsertVideoSeries = z.infer<typeof insertVideoSeriesSchema>;
export type VideoSeries = typeof videoSeries.$inferSelect;
export type InsertEpisode = z.infer<typeof insertEpisodeSchema>;
export type Episode = typeof episodes.$inferSelect;
export type VideoGenerationRequest = z.infer<typeof videoGenerationRequestSchema>;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});
