import { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Share2 } from "lucide-react";
import type { Episode } from "@shared/schema";

interface VideoPlayerProps {
  episodes: Episode[];
  currentEpisodeIndex: number;
  onEpisodeChange: (index: number) => void;
  onEpisodeWatched: (episodeId: number) => void;
}

export default function VideoPlayer({ 
  episodes, 
  currentEpisodeIndex, 
  onEpisodeChange, 
  onEpisodeWatched 
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const currentEpisode = episodes[currentEpisodeIndex];

  useEffect(() => {
    if (currentEpisode && !currentEpisode.isWatched) {
      // Mark as watched when episode starts playing
      onEpisodeWatched(currentEpisode.id);
    }
  }, [currentEpisode?.id, currentEpisode?.isWatched, onEpisodeWatched]);


  const handlePrevious = () => {
    if (currentEpisodeIndex > 0) {
      onEpisodeChange(currentEpisodeIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentEpisodeIndex < episodes.length - 1) {
      onEpisodeChange(currentEpisodeIndex + 1);
    }
  };

  const handleDownload = () => {
    if (currentEpisode?.videoUrl) {
      // Create a temporary link to trigger download
      const link = document.createElement('a');
      link.href = currentEpisode.videoUrl;
      link.download = `${currentEpisode.title}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: currentEpisode?.title,
        text: currentEpisode?.description,
        url: window.location.href,
      });
    } else {
      // Fallback to copying URL to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
  };

  if (!currentEpisode) {
    return (
      <div className="lg:col-span-2">
        <Card className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="aspect-video bg-neutral-100 flex items-center justify-center">
            <p className="text-neutral-500">No episodes available</p>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="lg:col-span-2">
      <Card className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="aspect-video bg-neutral-900 relative">
          {/* Actual Video Player */}
          {currentEpisode.videoUrl ? (
            <video
              ref={videoRef}
              className="w-full h-full object-cover"
              controls={true}
              preload="metadata"
              muted={false}
              autoPlay={false}
              playsInline
              crossOrigin="anonymous"
              onError={(e) => {
                console.error('Video load error:', e);
                console.error('Video URL:', currentEpisode.videoUrl);
              }}
              onLoadStart={() => {
                console.log('Video loading started:', currentEpisode.videoUrl);
              }}
              onCanPlay={() => {
                console.log('Video can play:', currentEpisode.videoUrl);
              }}
            >
              <source src={currentEpisode.videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-white">Video not available</p>
            </div>
          )}
          
          {/* Episode title overlay */}
          <div className="absolute top-4 left-4 bg-black/70 text-white px-3 py-1 rounded-lg text-sm font-medium">
            {currentEpisode.title}
          </div>
        </div>
        
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-neutral-900 mb-2">
            {currentEpisode.title}
          </h3>
          <p className="text-neutral-600 mb-4">
            {currentEpisode.description}
          </p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button onClick={handleDownload} className="bg-primary text-white hover:bg-blue-600">
                <Download className="mr-2" size={16} />
                Download
              </Button>
              <Button onClick={handleShare} variant="outline" className="text-neutral-600 hover:text-primary">
                <Share2 className="mr-2" size={16} />
                Share
              </Button>
            </div>
            <div className="text-sm text-neutral-500">
              Duration: {currentEpisode.duration}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Single-video MVP: no episode navigation */}
    </div>
  );
}
