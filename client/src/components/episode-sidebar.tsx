import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ListOrdered, Download, FileText, CheckCircle } from "lucide-react";
import type { VideoSeries, Episode } from "@shared/schema";

interface EpisodeSidebarProps {
  series: VideoSeries;
  episodes: Episode[];
  currentEpisodeIndex: number;
  onEpisodeSelect: (index: number) => void;
}

export default function EpisodeSidebar({ 
  series, 
  episodes, 
  currentEpisodeIndex, 
  onEpisodeSelect 
}: EpisodeSidebarProps) {
  const watchedEpisodes = episodes.filter(ep => ep.isWatched).length;
  const totalDuration = episodes.reduce((total, ep) => {
    const duration = parseInt(ep.duration.split(':')[0]) || 0;
    return total + duration;
  }, 0);
  const progressPercentage = episodes.length > 0 ? (watchedEpisodes / episodes.length) * 100 : 0;

  const handleDownloadAll = () => {
    // In a real implementation, this would trigger downloading all episodes
    episodes.forEach(episode => {
      if (episode.videoUrl) {
        window.open(episode.videoUrl, '_blank');
      }
    });
  };

  const handleDownloadTranscript = () => {
    // In a real implementation, this would download the series transcript
    const transcript = episodes.map(ep => `${ep.title}\n\n${ep.script}\n\n---\n\n`).join('');
    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${series.title}-transcript.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Video Information */}
      <Card className="bg-white rounded-2xl shadow-lg">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center">
            <ListOrdered className="text-primary mr-2" size={20} />
            {episodes.length > 1 ? `Series: ${series.title}` : `Video: ${series.title}`}
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">Subject:</span>
              <span className="font-medium">{series.subject}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">Level:</span>
              <span className="font-medium">{series.difficultyLevel}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-neutral-600">Duration:</span>
              <span className="font-medium">{totalDuration} minutes</span>
            </div>
            {episodes.length > 1 && (
              <>
                <div className="flex justify-between text-sm">
                  <span className="text-neutral-600">Progress:</span>
                  <span className="font-medium text-secondary">{Math.round(progressPercentage)}%</span>
                </div>
                <div className="mt-4">
                  <Progress value={progressPercentage} className="h-2" />
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Episode List - Only show for multiple episodes */}
      {episodes.length > 1 && (
        <Card className="bg-white rounded-2xl shadow-lg">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold text-neutral-900 mb-4">Episodes</h4>
            
            <div className="space-y-3">
              {episodes.map((episode, index) => (
                <div
                  key={episode.id}
                  onClick={() => onEpisodeSelect(index)}
                  className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${
                    index === currentEpisodeIndex
                      ? 'bg-primary/5 border border-primary/20'
                      : 'hover:bg-neutral-50'
                  }`}
                >
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium mr-3 ${
                    index === currentEpisodeIndex
                      ? 'bg-primary text-white'
                      : 'bg-neutral-200 text-neutral-600'
                  }`}>
                    {episode.episodeNumber}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-neutral-900 truncate">
                      {episode.title}
                    </p>
                    <p className="text-xs text-neutral-500">
                      {episode.duration} • {episode.isWatched ? 'Watched' : 'Not watched'}
                    </p>
                  </div>
                  {episode.isWatched && (
                    <CheckCircle className="text-secondary flex-shrink-0" size={16} />
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Download Section */}
      <Card className="bg-white rounded-2xl shadow-lg">
        <CardContent className="p-6">
          <h4 className="text-lg font-semibold text-neutral-900 mb-4">
            {episodes.length > 1 ? 'Download Series' : 'Download Video'}
          </h4>
          <div className="space-y-3">
            <Button
              onClick={handleDownloadAll}
              className="w-full bg-primary text-white hover:bg-blue-600 flex items-center justify-center"
            >
              <Download className="mr-2" size={16} />
              {episodes.length > 1 ? 'Download All Episodes' : 'Download Video'}
            </Button>
            <Button
              onClick={handleDownloadTranscript}
              variant="outline"
              className="w-full border-neutral-300 text-neutral-700 hover:bg-neutral-50 flex items-center justify-center"
            >
              <FileText className="mr-2" size={16} />
              Download Transcript
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
