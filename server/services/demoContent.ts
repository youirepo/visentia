import type { SeriesOutline, EpisodeScript } from "./openai.js";

// Realistic educational content generation (without video files)
export function generateDemoSeriesOutline(
  topic: string,
  subject: string,
  difficultyLevel: string,
  totalEpisodes: string,
  episodeDuration: string
): SeriesOutline {
  const episodeCount = parseInt(totalEpisodes.split('-')[0]) || 3;
  
  // Generate contextual content based on the topic
  const isCalculusLimits = topic.toLowerCase().includes('limit') || topic.toLowerCase().includes('calculus');
  const isPhotosynthesis = topic.toLowerCase().includes('photosynthesis');
  const isFunctions = topic.toLowerCase().includes('function');
  
  let seriesTitle = "";
  let episodes: any[] = [];
  
  if (isCalculusLimits || isFunctions) {
    seriesTitle = "Understanding Limits in Calculus";
    episodes = [
      {
        episodeNumber: 1,
        title: "What Are Limits?",
        description: "Introduction to the concept of limits and why they're fundamental to calculus",
        keyTopics: ["limit definition", "intuitive understanding", "graphical interpretation"],
        estimatedDuration: "6 minutes"
      },
      {
        episodeNumber: 2,
        title: "Evaluating Basic Limits",
        description: "Learn techniques for calculating simple limits using direct substitution and algebraic manipulation",
        keyTopics: ["direct substitution", "algebraic limits", "rational functions"],
        estimatedDuration: "7 minutes"
      },
      {
        episodeNumber: 3,
        title: "Limits at Infinity",
        description: "Understanding how functions behave as x approaches positive and negative infinity",
        keyTopics: ["horizontal asymptotes", "end behavior", "infinite limits"],
        estimatedDuration: "6 minutes"
      }
    ];
  } else if (isPhotosynthesis) {
    seriesTitle = "Photosynthesis: How Plants Make Food";
    episodes = [
      {
        episodeNumber: 1,
        title: "Introduction to Photosynthesis",
        description: "Overview of photosynthesis and its importance in the ecosystem",
        keyTopics: ["chlorophyll", "sunlight energy", "carbon dioxide"],
        estimatedDuration: "5 minutes"
      },
      {
        episodeNumber: 2,
        title: "Light Reactions",
        description: "How plants capture and convert light energy in the thylakoids",
        keyTopics: ["chloroplasts", "ATP production", "oxygen release"],
        estimatedDuration: "6 minutes"
      },
      {
        episodeNumber: 3,
        title: "Calvin Cycle",
        description: "The dark reactions that convert CO2 into glucose",
        keyTopics: ["carbon fixation", "glucose formation", "energy storage"],
        estimatedDuration: "7 minutes"
      }
    ];
  } else {
    // Generic educational content
    seriesTitle = `Understanding ${topic}`;
    episodes = [
      {
        episodeNumber: 1,
        title: `Introduction to ${topic}`,
        description: `Fundamental concepts and overview of ${topic}`,
        keyTopics: ["basic concepts", "key principles", "real-world applications"],
        estimatedDuration: "6 minutes"
      },
      {
        episodeNumber: 2,
        title: `Core Principles`,
        description: `Deep dive into the main principles and theories`,
        keyTopics: ["theoretical framework", "practical examples", "problem solving"],
        estimatedDuration: "7 minutes"
      },
      {
        episodeNumber: 3,
        title: `Applications and Examples`,
        description: `Real-world applications and worked examples`,
        keyTopics: ["case studies", "practical implementation", "advanced concepts"],
        estimatedDuration: "6 minutes"
      }
    ];
  }

  // Limit to requested number of episodes
  episodes = episodes.slice(0, episodeCount);

  return {
    title: seriesTitle,
    episodes
  };
}

export function generateDemoEpisodeScript(
  seriesTitle: string,
  episodeTitle: string,
  episodeDescription: string,
  keyTopics: string[],
  difficultyLevel: string,
  targetDuration: string
): EpisodeScript {
  
  // Generate contextual script content
  let script = "";
  
  if (episodeTitle.toLowerCase().includes("limits")) {
    script = `Welcome to our exploration of limits in calculus!

In this episode, we'll discover what limits are and why they're so important in mathematics.

Imagine you're walking toward a wall. With each step, you get closer and closer, but you never quite reach it. In mathematics, we can describe what happens as you approach that wall - this is the concept of a limit.

A limit describes the value that a function approaches as the input approaches some value. For example, if we have the function f(x) = 2x + 1, and we want to know what happens as x approaches 3, we can substitute values very close to 3.

When x = 2.9, f(x) = 6.8
When x = 2.99, f(x) = 6.98
When x = 2.999, f(x) = 6.998

We can see that as x gets closer to 3, f(x) gets closer to 7. We say the limit of f(x) as x approaches 3 is 7.

This concept becomes especially powerful when dealing with functions that have discontinuities or undefined points. Limits allow us to understand the behavior of functions even at points where they're not explicitly defined.

In our next episode, we'll learn specific techniques for calculating limits algebraically. Thank you for joining me, and I'll see you next time!`;
  } else if (episodeTitle.toLowerCase().includes("photosynthesis")) {
    script = `Welcome to our journey into the amazing world of photosynthesis!

Have you ever wondered how a tiny seed can grow into a massive tree? The secret lies in photosynthesis - one of the most important biological processes on Earth.

Photosynthesis is how plants make their own food using sunlight, water, and carbon dioxide from the air. It's like having a solar-powered kitchen inside every leaf!

The process happens mainly in the leaves, specifically in tiny structures called chloroplasts. These contain a green pigment called chlorophyll, which captures sunlight energy.

The basic equation for photosynthesis is:
6CO2 + 6H2O + light energy → C6H12O6 + 6O2

This means six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose and six molecules of oxygen.

What's amazing is that plants not only make food for themselves, but they also release oxygen as a byproduct - the very oxygen we breathe! Without photosynthesis, there would be no complex life on Earth.

In our next episode, we'll dive deeper into the light reactions and see exactly how plants capture and convert sunlight into chemical energy. Stay curious, and I'll see you next time!`;
  } else {
    script = `Welcome to this educational exploration!

In this episode, we'll examine the fundamental concepts that form the foundation of our topic. Understanding these basics is crucial for building deeper knowledge.

Let's start by defining key terms and establishing the conceptual framework. Each concept builds upon the previous one, creating a comprehensive understanding.

Throughout this series, we'll use real-world examples to illustrate abstract concepts, making them more relatable and easier to remember.

The key principles we'll cover include the theoretical foundations, practical applications, and problem-solving strategies. These elements work together to provide a complete learning experience.

As we progress through the material, you'll notice how these concepts interconnect and support each other. This systematic approach ensures thorough comprehension.

Remember, learning is a process. Don't worry if everything doesn't click immediately - that's completely normal. Take your time to absorb the information, and feel free to review sections as needed.

In our next episode, we'll build upon these foundations and explore more advanced concepts. Thank you for joining me on this educational journey!`;
  }

  return {
    title: episodeTitle,
    description: episodeDescription,
    script,
    duration: targetDuration
  };
}