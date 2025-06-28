import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Clock, ArrowRight } from "lucide-react";
import { Link } from "wouter";
import { useQuery } from "@tanstack/react-query";
import type { VideoSeries } from "@shared/schema";

export default function RecentSeries() {
  const { data: seriesList = [], isLoading } = useQuery<VideoSeries[]>({
    queryKey: ['/api/series'],
  });

  const getSubjectColor = (subject: string) => {
    const colors = {
      'Mathematics': 'from-blue-500 to-purple-600',
      'Science': 'from-green-500 to-blue-500',
      'Biology': 'from-green-500 to-blue-500',
      'History': 'from-amber-500 to-red-600',
      'Literature': 'from-purple-500 to-pink-600',
      'Computer Science': 'from-cyan-500 to-blue-600',
      'Languages': 'from-orange-500 to-red-500',
    };
    return colors[subject as keyof typeof colors] || 'from-gray-500 to-gray-600';
  };

  const getProgressPercentage = (series: VideoSeries) => {
    return series.progress || 0;
  };

  if (isLoading) {
    return (
      <section className="mt-16">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-2xl font-bold text-neutral-900 flex items-center">
            <Clock className="text-neutral-600 mr-3" size={28} />
            Your Recent Series
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="bg-white rounded-xl shadow-lg overflow-hidden animate-pulse">
              <div className="aspect-video bg-neutral-200"></div>
              <CardContent className="p-6">
                <div className="h-4 bg-neutral-200 rounded mb-2"></div>
                <div className="h-3 bg-neutral-200 rounded mb-4"></div>
                <div className="flex items-center justify-between">
                  <div className="h-3 bg-neutral-200 rounded w-16"></div>
                  <div className="h-3 bg-neutral-200 rounded w-12"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    );
  }

  if (seriesList.length === 0) {
    return (
      <section className="mt-16">
        <div className="flex items-center justify-between mb-8">
          <h3 className="text-2xl font-bold text-neutral-900 flex items-center">
            <Clock className="text-neutral-600 mr-3" size={28} />
            Your Recent Series
          </h3>
        </div>
        <Card className="bg-white rounded-xl shadow-lg p-12 text-center">
          <Clock className="mx-auto text-neutral-300 mb-4" size={48} />
          <h4 className="text-lg font-semibold text-neutral-900 mb-2">No video series yet</h4>
          <p className="text-neutral-600">Create your first educational video series using the form above.</p>
        </Card>
      </section>
    );
  }

  return (
    <section className="mt-16">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-2xl font-bold text-neutral-900 flex items-center">
          <Clock className="text-neutral-600 mr-3" size={28} />
          Your Recent Series
        </h3>
        <Link href="/series" className="text-primary hover:text-blue-600 transition-colors font-medium flex items-center">
          View All <ArrowRight className="ml-1" size={16} />
        </Link>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {seriesList.slice(0, 6).map((series) => (
          <Link key={series.id} href={`/series/${series.id}`}>
            <Card className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow cursor-pointer">
              <div className={`aspect-video bg-gradient-to-br ${getSubjectColor(series.subject)} relative`}>
                <div className="absolute inset-0 bg-black/20"></div>
                <div className="absolute top-4 right-4 bg-white/90 text-neutral-900 px-2 py-1 rounded text-sm font-medium">
                  {series.totalEpisodes} episodes
                </div>
                <div className="absolute bottom-4 left-4 text-white">
                  <div className="bg-secondary px-2 py-1 rounded text-xs font-medium mb-2">
                    {series.subject}
                  </div>
                </div>
              </div>
              <CardContent className="p-6">
                <h4 className="text-lg font-semibold text-neutral-900 mb-2 line-clamp-1">
                  {series.title}
                </h4>
                <p className="text-neutral-600 text-sm mb-4 line-clamp-2">
                  {series.topic}
                </p>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-neutral-500 flex items-center">
                    <Clock className="mr-1" size={14} />
                    {series.episodeDuration}
                  </div>
                  <div className="flex items-center">
                    <div className="bg-neutral-100 rounded-full h-2 w-16 overflow-hidden mr-2">
                      <div 
                        className="bg-secondary h-full rounded-full transition-all duration-300" 
                        style={{ width: `${getProgressPercentage(series)}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-neutral-500">
                      {series.status === 'completed' ? (
                        <span className="text-secondary font-medium">Completed</span>
                      ) : series.status === 'generating' ? (
                        `${getProgressPercentage(series)}%`
                      ) : (
                        'Error'
                      )}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}
