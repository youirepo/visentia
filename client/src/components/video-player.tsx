import { useState, useEffect, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Download, Share2, ChevronLeft, ChevronRight, Pause, Volume2, VolumeX, Maximize } from "lucide-react";
import { Progress } from "@/components/ui/progress";
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
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const currentEpisode = episodes[currentEpisodeIndex];

  useEffect(() => {
    if (currentEpisode && !currentEpisode.isWatched) {
      // Mark as watched when episode starts playing
      onEpisodeWatched(currentEpisode.id);
    }
  }, [currentEpisode?.id, currentEpisode?.isWatched, onEpisodeWatched]);

  const handlePlay = async () => {
    if (videoRef.current) {
      try {
        if (isPlaying) {
          videoRef.current.pause();
        } else {
          // Ensure audio is enabled and volume is up
          videoRef.current.muted = false;
          videoRef.current.volume = volume;
          
          // Try to play with audio first
          try {
            await videoRef.current.play();
          } catch (audioError) {
            console.log('Audio playback blocked, trying muted first:', audioError);
            // If audio playback fails, try muted first then unmute
            videoRef.current.muted = true;
            await videoRef.current.play();
            // Wait a bit then unmute
            setTimeout(() => {
              if (videoRef.current) {
                videoRef.current.muted = false;
                videoRef.current.volume = volume;
              }
            }, 100);
          }
        }
        setIsPlaying(!isPlaying);
      } catch (error) {
        console.error('Error playing video:', error);
      }
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const current = videoRef.current.currentTime;
      const total = videoRef.current.duration;
      setCurrentTime(current);
      setDuration(total);
      setProgress((current / total) * 100);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
      // Ensure audio is enabled
      videoRef.current.muted = false;
      videoRef.current.volume = volume;
      
      // Debug audio state
      console.log('Video loaded metadata:', {
        duration: videoRef.current.duration,
        muted: videoRef.current.muted,
        volume: videoRef.current.volume,
        readyState: videoRef.current.readyState,
        networkState: videoRef.current.networkState
      });
    }
  };

  const handleVolumeToggle = () => {
    if (videoRef.current) {
      if (isMuted) {
        videoRef.current.muted = false;
        videoRef.current.volume = volume;
        setIsMuted(false);
      } else {
        videoRef.current.muted = true;
        setIsMuted(true);
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

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
      // In a real implementation, this would trigger the actual download
      window.open(currentEpisode.videoUrl, '_blank');
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
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onClick={handlePlay}
              controls={false}
              preload="metadata"
              muted={false}
              autoPlay={false}
            >
              <source src={currentEpisode.videoUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-white">Video not available</p>
            </div>
          )}
          
          {/* Video player controls overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
            <div className="flex items-center space-x-4 text-white">
              <Button
                onClick={handlePlay}
                variant="ghost"
                size="sm"
                className="text-white hover:text-primary"
              >
                {isPlaying ? <Pause size={16} /> : <Play size={16} />}
              </Button>
              <div className="flex-1">
                <Progress value={progress} className="h-1" />
              </div>
              <span className="text-sm">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
              <Button 
                onClick={handleVolumeToggle}
                variant="ghost" 
                size="sm" 
                className="text-white hover:text-primary"
              >
                {isMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
              </Button>
              <Button variant="ghost" size="sm" className="text-white hover:text-primary">
                <Maximize size={16} />
              </Button>
            </div>
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

      {/* Episode Navigation - Only show for multiple episodes */}
      {episodes.length > 1 && (
        <div className="flex items-center justify-between mt-6">
          <Button
            onClick={handlePrevious}
            disabled={currentEpisodeIndex === 0}
            variant="ghost"
            className="flex items-center text-neutral-600 hover:text-primary disabled:opacity-50"
          >
            <ChevronLeft className="mr-2" size={16} />
            Previous Episode
          </Button>
          <div className="text-sm text-neutral-500">
            Episode {currentEpisodeIndex + 1} of {episodes.length}
          </div>
          <Button
            onClick={handleNext}
            disabled={currentEpisodeIndex === episodes.length - 1}
            variant="ghost"
            className="flex items-center text-neutral-600 hover:text-primary disabled:opacity-50"
          >
            Next Episode
            <ChevronRight className="ml-2" size={16} />
          </Button>
        </div>
      )}
    </div>
  );
}
