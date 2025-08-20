import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Play, Video } from "lucide-react";
import Header from "@/components/header";
import Footer from "@/components/footer";
import VideoGenerationForm from "@/components/video-generation-form";
import ProgressIndicator from "@/components/progress-indicator";
import VideoPlayer from "@/components/video-player";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import type { VideoSeries, Episode } from "@shared/schema";

export default function Home() {
  const [generatingSeriesId, setGeneratingSeriesId] = useState<number | null>(null);
  const [selectedSeriesId, setSelectedSeriesId] = useState<number | null>(null);
  const [currentEpisodeIndex, setCurrentEpisodeIndex] = useState(0);
  
  const queryClient = useQueryClient();

  // Get the selected series data
  const { data: selectedSeries } = useQuery<VideoSeries>({
    queryKey: ['/api/series', selectedSeriesId],
    enabled: !!selectedSeriesId,
  });

  // Get episodes for the selected series
  const { data: episodes = [] } = useQuery<Episode[]>({
    queryKey: ['/api/series', selectedSeriesId, 'episodes'],
    enabled: !!selectedSeriesId,
  });

  // Mutation to mark episode as watched
  const markWatchedMutation = useMutation({
    mutationFn: async ({ episodeId, watched }: { episodeId: number; watched: boolean }) => {
      await apiRequest("PATCH", `/api/episodes/${episodeId}/watched`, { watched });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/series', selectedSeriesId, 'episodes'] });
    },
  });

  const handleGenerationStart = (seriesId: number) => {
    setGeneratingSeriesId(seriesId);
    setSelectedSeriesId(null);
  };

  const handleGenerationComplete = () => {
    if (generatingSeriesId) {
      setSelectedSeriesId(generatingSeriesId);
      setGeneratingSeriesId(null);
      setCurrentEpisodeIndex(0);
    }
  };

  const handleEpisodeChange = (index: number) => {
    setCurrentEpisodeIndex(index);
  };

  const handleEpisodeSelect = (index: number) => {
    setCurrentEpisodeIndex(index);
  };

  const handleEpisodeWatched = (episodeId: number) => {
    markWatchedMutation.mutate({ episodeId, watched: true });
  };

  const showVideoPlayer = selectedSeries && episodes.length > 0;

  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />
      
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary to-accent text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Generate Educational Videos with AI
          </h2>
          <p className="text-xl md:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Transform any educational topic into an engaging video. Just describe what you want to learn, and our AI creates professional educational content for you.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:bg-neutral-100 transition-colors">
              <Play className="mr-2" size={20} />
              Get Started
            </Button>
            <Button 
              variant="outline" 
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary transition-colors"
            >
              <Video className="mr-2" size={20} />
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        
        {/* Video Generation Form */}
        {!generatingSeriesId && !showVideoPlayer && (
          <VideoGenerationForm onGenerationStart={handleGenerationStart} />
        )}

        {/* Generation Progress */}
        {generatingSeriesId && (
          <ProgressIndicator 
            seriesId={generatingSeriesId} 
            onComplete={handleGenerationComplete}
          />
        )}

        {/* Generated Video Display */}
        {showVideoPlayer && (
          <div className="grid grid-cols-1 gap-8 mb-12">
            <VideoPlayer
              episodes={episodes}
              currentEpisodeIndex={currentEpisodeIndex}
              onEpisodeChange={handleEpisodeChange}
              onEpisodeWatched={handleEpisodeWatched}
            />
          </div>
        )}

        {/* Single-video MVP: no series/episodes list */}

      </main>

      <Footer />
    </div>
  );
}
