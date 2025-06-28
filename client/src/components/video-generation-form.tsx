import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Wand2, Lightbulb } from "lucide-react";
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
    totalEpisodes: "",
    episodeDuration: "",
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
        description: "Your video series is being generated. This may take a few minutes.",
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
        description: "Please enter a topic for your video series",
        variant: "destructive",
      });
      return;
    }

    if (!formData.subject || !formData.difficultyLevel || !formData.totalEpisodes || !formData.episodeDuration) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    generateMutation.mutate(formData as VideoGenerationRequest);
  };

  return (
    <Card className="bg-white rounded-2xl shadow-lg p-8 mb-12">
      <div className="max-w-4xl mx-auto">
        <h3 className="text-2xl font-bold text-neutral-900 mb-6 text-center flex items-center justify-center">
          <Wand2 className="text-accent mr-3" size={28} />
          Create Your Educational Content Series
        </h3>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <Label htmlFor="topic-prompt" className="block text-sm font-medium text-neutral-700 mb-2">
              What would you like to learn about?
            </Label>
            <Textarea
              id="topic-prompt"
              rows={4}
              className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
              placeholder="e.g., 'Generate me a mini video series on limits of functions' or 'Create a series explaining photosynthesis for high school students'"
              value={formData.topic}
              onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            />
            <p className="text-sm text-neutral-500 mt-2 flex items-center">
              <Lightbulb className="mr-1" size={14} />
              Generates educational scripts with professional narration. Be specific about the topic and difficulty level for best results.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="subject" className="block text-sm font-medium text-neutral-700 mb-2">
                Subject Area
              </Label>
              <Select value={formData.subject} onValueChange={(value) => setFormData({ ...formData, subject: value })}>
                <SelectTrigger className="w-full px-4 py-3 border border-neutral-300 rounded-lg">
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
            <div>
              <Label htmlFor="difficulty" className="block text-sm font-medium text-neutral-700 mb-2">
                Difficulty Level
              </Label>
              <Select value={formData.difficultyLevel} onValueChange={(value) => setFormData({ ...formData, difficultyLevel: value })}>
                <SelectTrigger className="w-full px-4 py-3 border border-neutral-300 rounded-lg">
                  <SelectValue placeholder="Select difficulty" />
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

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Label htmlFor="episodes" className="block text-sm font-medium text-neutral-700 mb-2">
                Number of Episodes
              </Label>
              <Select value={formData.totalEpisodes} onValueChange={(value) => setFormData({ ...formData, totalEpisodes: value })}>
                <SelectTrigger className="w-full px-4 py-3 border border-neutral-300 rounded-lg">
                  <SelectValue placeholder="Select episodes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3-5 episodes">3-5 episodes</SelectItem>
                  <SelectItem value="6-8 episodes">6-8 episodes</SelectItem>
                  <SelectItem value="9-12 episodes">9-12 episodes</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="duration" className="block text-sm font-medium text-neutral-700 mb-2">
                Episode Duration
              </Label>
              <Select value={formData.episodeDuration} onValueChange={(value) => setFormData({ ...formData, episodeDuration: value })}>
                <SelectTrigger className="w-full px-4 py-3 border border-neutral-300 rounded-lg">
                  <SelectValue placeholder="Select duration" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3-5 minutes">3-5 minutes</SelectItem>
                  <SelectItem value="5-8 minutes">5-8 minutes</SelectItem>
                  <SelectItem value="8-12 minutes">8-12 minutes</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-center">
            <Button
              type="submit"
              disabled={generateMutation.isPending}
              className="bg-primary text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-600 transition-colors flex items-center"
            >
              <Wand2 className="mr-3" size={20} />
{generateMutation.isPending ? "Generating..." : "Generate Educational Series"}
            </Button>
          </div>
        </form>
      </div>
    </Card>
  );
}
