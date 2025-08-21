import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Wand2, Lightbulb, Sparkles } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import type { VideoGenerationRequest } from "@shared/schema";

interface VideoGenerationFormProps {
  onGenerationStart: (seriesId: number) => void;
}

export default function VideoGenerationForm({ onGenerationStart }: VideoGenerationFormProps) {
  const [formData, setFormData] = useState({
    topic: "",
    subject: "",
    difficultyLevel: "",
    style: "Visual and Demonstrative",
    videoDuration: "2-3 minutes",
  });

  const { toast } = useToast();

  const generateMutation = useMutation({
    mutationFn: async (data: VideoGenerationRequest) => {
      const response = await apiRequest("POST", "/api/generate-series", data);
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Generation Started",
        description: "Your educational video is being generated. This may take a few minutes.",
      });
      onGenerationStart(data.seriesId);
    },
    onError: (error) => {
      toast({
        title: "Generation Failed",
        description: error.message || "Failed to start video generation",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.topic.trim()) {
      toast({
        title: "Missing Information",
        description: "Please enter a topic for your video",
        variant: "destructive",
      });
      return;
    }

    if (!formData.subject || !formData.difficultyLevel) {
      toast({
        title: "Missing Information",
        description: "Please fill in subject and depth level",
        variant: "destructive",
      });
      return;
    }

    // Convert single video request to series format for backend compatibility
    const seriesRequest = {
      ...formData,
      totalEpisodes: "1 episode",
      episodeDuration: "2-3 minutes",
      style: "Visual and Demonstrative",
    };

    generateMutation.mutate(seriesRequest as VideoGenerationRequest);
  };

  return (
    <Card className="bg-white rounded-2xl shadow-lg p-8 mb-12">
      <div className="max-w-3xl mx-auto">
        <h3 className="text-2xl font-bold text-neutral-900 mb-6 text-center flex items-center justify-center">
          <Wand2 className="text-accent mr-3" size={28} />
          Create Your Educational Video
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Prompt Section */}
          <div className="space-y-4">
            <Label htmlFor="topic-prompt" className="block text-lg font-semibold text-neutral-800 mb-3">
              What would you like to learn about?
            </Label>
            <Textarea
              id="topic-prompt"
              rows={4}
              className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none text-base"
              placeholder="e.g., 'Explain the concept of limits in calculus' or 'Create a video about photosynthesis for high school students'"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            />
            <p className="text-sm text-neutral-500 flex items-center">
              <Lightbulb className="mr-2" size={16} />
              Be specific about the topic and difficulty level for best results.
            </p>
          </div>

          {/* Subject and Depth Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <Label htmlFor="subject" className="block text-lg font-semibold text-neutral-800">
                Subject Area
              </Label>
              <Select value={formData.subject} onValueChange={(value) => setFormData({ ...formData, subject: value })}>
                <SelectTrigger className="w-full px-4 py-3 border border-neutral-300 rounded-lg text-base">
                  <SelectValue placeholder="Select subject" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Mathematics">Mathematics</SelectItem>
                  <SelectItem value="Science">Science</SelectItem>
                  <SelectItem value="History">History</SelectItem>
                  <SelectItem value="Literature">Literature</SelectItem>
                  <SelectItem value="Computer Science">Computer Science</SelectItem>
                  <SelectItem value="Languages">Languages</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="difficulty" className="block text-lg font-semibold text-neutral-800">
                Depth Level
              </Label>
              <Select value={formData.difficultyLevel} onValueChange={(value) => setFormData({ ...formData, difficultyLevel: value })}>
                <SelectTrigger className="w-full px-4 py-3 border border-neutral-300 rounded-lg text-base">
                  <SelectValue placeholder="Select depth level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Elementary School">Elementary School</SelectItem>
                  <SelectItem value="Middle School">Middle School</SelectItem>
                  <SelectItem value="High School">High School</SelectItem>
                  <SelectItem value="College/University">College/University</SelectItem>
                  <SelectItem value="Graduate Level">Graduate Level</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Style and Duration: fixed for MVP */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1">
              <Label className="block text-lg font-semibold text-neutral-800">Style</Label>
              <div className="px-4 py-3 border border-neutral-200 rounded-lg bg-neutral-50 text-neutral-700">
                Visual & Demonstrative (fixed)
              </div>
            </div>
            <div className="space-y-1">
              <Label className="block text-lg font-semibold text-neutral-800">Video Duration</Label>
              <div className="px-4 py-3 border border-neutral-200 rounded-lg bg-neutral-50 text-neutral-700">
                2-3 minutes (fixed)
              </div>
            </div>
          </div>

          {/* Submit Section */}
          <div className="flex justify-center pt-4">
            <Button
              type="submit"
              disabled={generateMutation.isPending}
              className="bg-primary text-white px-12 py-4 rounded-lg font-semibold hover:bg-blue-600 transition-colors flex items-center text-lg"
            >
              <Sparkles className="mr-3" size={20} />
              {generateMutation.isPending ? "Generating..." : "Generate Video"}
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
}
