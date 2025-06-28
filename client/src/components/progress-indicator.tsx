import { useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Loader2, CheckCircle, Circle } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

interface ProgressIndicatorProps {
  seriesId: number;
  onComplete: () => void;
}

interface GenerationProgress {
  seriesId: number;
  progress: number;
  currentStep: string;
  status: 'generating' | 'completed' | 'error';
}

export default function ProgressIndicator({ seriesId, onComplete }: ProgressIndicatorProps) {
  const queryClient = useQueryClient();

  const { data: progress } = useQuery<GenerationProgress>({
    queryKey: ['/api/generation-progress', seriesId],
    refetchInterval: (data) => {
      // Stop polling if completed or errored
      if (data?.status === 'completed' || data?.status === 'error') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });

  useEffect(() => {
    if (progress?.status === 'completed') {
      // Invalidate series queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ['/api/series'] });
      onComplete();
    }
  }, [progress?.status, onComplete, queryClient]);

  if (!progress) {
    return null;
  }

  const getStepStatus = (stepName: string) => {
    if (progress.status === 'error') {
      return 'error';
    }
    
    if (progress.progress === 100) {
      return 'completed';
    }
    
    if (progress.currentStep.toLowerCase().includes(stepName.toLowerCase())) {
      return 'active';
    }
    
    if (progress.progress > getStepThreshold(stepName)) {
      return 'completed';
    }
    
    return 'pending';
  };

  const getStepThreshold = (stepName: string) => {
    switch (stepName) {
      case 'script': return 0;
      case 'voice': return 30;
      case 'video': return 70;
      default: return 0;
    }
  };

  return (
    <Card className="bg-white rounded-2xl shadow-lg p-8 mb-12">
      <div className="max-w-2xl mx-auto text-center">
        <div className="mb-6">
          {progress.status === 'error' ? (
            <>
              <Circle className="text-red-500 mx-auto mb-4" size={48} />
              <h3 className="text-xl font-semibold text-neutral-900 mb-2">Generation Failed</h3>
              <p className="text-red-600">{progress.currentStep}</p>
            </>
          ) : (
            <>
              <Loader2 className="animate-spin text-accent mx-auto mb-4" size={48} />
              <h3 className="text-xl font-semibold text-neutral-900 mb-2">Generating Your Video Series</h3>
              <p className="text-neutral-600">This may take a few minutes. Please don't close this page.</p>
            </>
          )}
        </div>
        
        <div className="space-y-4">
          <Progress 
            value={progress.progress} 
            className="h-3"
          />
          <div className="text-sm text-neutral-600">
            {progress.currentStep}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          <div className={`flex items-center justify-center p-4 rounded-lg ${
            getStepStatus('script') === 'completed' ? 'bg-secondary/10' : 
            getStepStatus('script') === 'active' ? 'bg-primary/10' : 'bg-neutral-100'
          }`}>
            {getStepStatus('script') === 'completed' ? (
              <CheckCircle className="text-secondary mr-2" size={20} />
            ) : (
              <Circle className="text-neutral-400 mr-2" size={20} />
            )}
            <span className="text-sm">Script Generation</span>
          </div>
          <div className={`flex items-center justify-center p-4 rounded-lg ${
            getStepStatus('voice') === 'completed' ? 'bg-secondary/10' : 
            getStepStatus('voice') === 'active' ? 'bg-primary/10' : 'bg-neutral-100'
          }`}>
            {getStepStatus('voice') === 'completed' ? (
              <CheckCircle className="text-secondary mr-2" size={20} />
            ) : (
              <Circle className="text-neutral-400 mr-2" size={20} />
            )}
            <span className="text-sm">Voice Narration</span>
          </div>
          <div className={`flex items-center justify-center p-4 rounded-lg ${
            getStepStatus('video') === 'completed' ? 'bg-secondary/10' : 
            getStepStatus('video') === 'active' ? 'bg-primary/10' : 'bg-neutral-100'
          }`}>
            {getStepStatus('video') === 'completed' ? (
              <CheckCircle className="text-secondary mr-2" size={20} />
            ) : (
              <Circle className="text-neutral-400 mr-2" size={20} />
            )}
            <span className="text-sm">Video Compilation</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
