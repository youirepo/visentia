import type { SeriesOutline, EpisodeScript } from "./openai.js";

// Comprehensive educational content demo system
export function generateEducationalSeries(
  topic: string,
  subject: string,
  difficultyLevel: string,
  totalEpisodes: string,
  episodeDuration: string
): { outline: SeriesOutline; scripts: EpisodeScript[] } {
  
  const episodeCount = parseInt(totalEpisodes.split('-')[0]) || 3;
  
  // Calculus Limits Content
  if (topic.toLowerCase().includes('limit') || topic.toLowerCase().includes('calculus')) {
    const outline: SeriesOutline = {
      title: "Understanding Limits in Calculus",
      episodes: [
        {
          episodeNumber: 1,
          title: "What Are Limits? The Foundation of Calculus",
          description: "Introduction to the fundamental concept of limits and their intuitive meaning",
          keyTopics: ["limit definition", "approaching values", "graphical interpretation"],
          estimatedDuration: "7 minutes"
        },
        {
          episodeNumber: 2,
          title: "Calculating Limits: Direct Substitution and Algebraic Methods", 
          description: "Learn practical techniques for evaluating limits using substitution and algebraic manipulation",
          keyTopics: ["direct substitution", "factoring", "rationalizing", "squeeze theorem"],
          estimatedDuration: "8 minutes"
        },
        {
          episodeNumber: 3,
          title: "One-Sided Limits and Continuity",
          description: "Understanding left and right limits, and how they relate to function continuity",
          keyTopics: ["left-hand limits", "right-hand limits", "continuity", "jump discontinuities"],
          estimatedDuration: "6 minutes"
        }
      ].slice(0, episodeCount)
    };

    const scripts: EpisodeScript[] = [
      {
        title: "What Are Limits? The Foundation of Calculus",
        description: "Introduction to the fundamental concept of limits and their intuitive meaning",
        script: `Welcome to our exploration of one of mathematics' most elegant concepts: limits.

Imagine you're walking toward a wall. With each step, you get closer and closer, but you never quite reach it. In mathematics, we can describe exactly what happens as you approach that wall - this is the essence of a limit.

A limit describes the value that a function approaches as the input approaches some specific value. It's like asking: "Where is this function heading?"

Let's look at a simple example. Consider the function f(x) = 2x + 1. What happens as x approaches 3?

When x = 2.9, f(x) = 6.8
When x = 2.99, f(x) = 6.98  
When x = 2.999, f(x) = 6.998

We can see that as x gets closer to 3, f(x) gets closer to 7. We write this as: the limit of f(x) as x approaches 3 equals 7.

But here's where limits become truly powerful - they help us understand function behavior even at points where the function isn't defined.

Consider f(x) = (x² - 9)/(x - 3). At x = 3, this function is undefined because we'd be dividing by zero. But what does the function approach as x gets close to 3?

We can factor the numerator: (x² - 9) = (x - 3)(x + 3)
So f(x) = (x - 3)(x + 3)/(x - 3) = x + 3, when x ≠ 3

As x approaches 3, x + 3 approaches 6. So the limit exists even though the function has a hole at x = 3.

This is why limits are fundamental to calculus - they let us study function behavior at the very points where traditional algebra breaks down.

In our next episode, we'll learn specific techniques for calculating limits. Until then, remember: limits are about the journey, not the destination.`,
        duration: "7 minutes"
      },
      {
        title: "Calculating Limits: Direct Substitution and Algebraic Methods",
        description: "Learn practical techniques for evaluating limits using substitution and algebraic manipulation", 
        script: `Now that we understand what limits represent, let's learn how to calculate them systematically.

The first and simplest method is direct substitution. If a function is continuous at a point, we can find the limit by simply plugging in the value.

For example, to find the limit of f(x) = x² + 3x - 1 as x approaches 2:
We substitute: (2)² + 3(2) - 1 = 4 + 6 - 1 = 9

But what happens when direct substitution gives us 0/0? This indeterminate form requires algebraic manipulation.

Let's work through f(x) = (x² - 4)/(x - 2) as x approaches 2.

Direct substitution gives us (4 - 4)/(2 - 2) = 0/0, which is indeterminate.

Step 1: Factor the numerator
x² - 4 = (x - 2)(x + 2)

Step 2: Simplify
f(x) = (x - 2)(x + 2)/(x - 2) = x + 2, for x ≠ 2

Step 3: Apply the limit
As x approaches 2, x + 2 approaches 4.

Another powerful technique is rationalization, useful when dealing with square roots.

For f(x) = (√x - 2)/(x - 4) as x approaches 4:

Multiply by the conjugate: (√x + 2)/(√x + 2)
This gives us: (x - 4)/((x - 4)(√x + 2)) = 1/(√x + 2)

As x approaches 4: 1/(√4 + 2) = 1/4

These algebraic techniques transform indeterminate forms into expressions we can evaluate. The key is recognizing which method to use.

Next time, we'll explore what happens when limits approach from different directions.`,
        duration: "8 minutes"
      },
      {
        title: "One-Sided Limits and Continuity",
        description: "Understanding left and right limits, and how they relate to function continuity",
        script: `Sometimes, a function behaves differently as we approach a point from the left versus from the right. This is where one-sided limits become essential.

A left-hand limit examines function behavior as x approaches a value from smaller numbers (the left side of the number line). We write this as x → a⁻.

A right-hand limit examines behavior from larger numbers (the right side). We write this as x → a⁺.

Consider the function f(x) = |x|/x. What happens as x approaches 0?

From the right (positive values): |x|/x = x/x = 1
From the left (negative values): |x|/x = -x/x = -1

The right-hand limit is 1, but the left-hand limit is -1. Since these don't match, the overall limit doesn't exist.

This connects directly to continuity. A function is continuous at a point if three conditions are met:
1. The function is defined at that point
2. The limit exists at that point  
3. The limit equals the function value

For a limit to exist, both one-sided limits must exist and be equal.

Let's examine a piecewise function:
f(x) = {x + 1 if x < 2; 3x - 1 if x ≥ 2}

At x = 2:
- Left-hand limit: approaching from values less than 2, we use x + 1, so the limit is 2 + 1 = 3
- Right-hand limit: approaching from values greater than or equal to 2, we use 3x - 1, so the limit is 3(2) - 1 = 5
- Function value: f(2) = 3(2) - 1 = 5

Since the one-sided limits don't match (3 ≠ 5), the limit doesn't exist, and the function has a jump discontinuity.

Understanding one-sided limits helps us analyze real-world phenomena with sudden changes, like step functions in physics or economics.

This completes our foundation in limits. You now have the tools to analyze function behavior at any point, setting the stage for derivatives and integrals - the heart of calculus.`,
        duration: "6 minutes"
      }
    ].slice(0, episodeCount);

    return { outline, scripts };
  }

  // Photosynthesis Content
  if (topic.toLowerCase().includes('photosynthesis')) {
    const outline: SeriesOutline = {
      title: "Photosynthesis: How Plants Convert Light into Life",
      episodes: [
        {
          episodeNumber: 1,
          title: "The Chemistry of Life: Introduction to Photosynthesis",
          description: "Understanding the fundamental process that powers most life on Earth",
          keyTopics: ["chlorophyll", "glucose production", "oxygen release", "energy conversion"],
          estimatedDuration: "6 minutes"
        },
        {
          episodeNumber: 2,
          title: "Light Reactions: Capturing Solar Energy",
          description: "How chloroplasts convert light energy into chemical energy",
          keyTopics: ["thylakoids", "ATP synthesis", "NADPH production", "electron transport"],
          estimatedDuration: "7 minutes"
        },
        {
          episodeNumber: 3,
          title: "The Calvin Cycle: Building Glucose from Carbon Dioxide",
          description: "The dark reactions that use chemical energy to create organic molecules",
          keyTopics: ["carbon fixation", "RuBisCO enzyme", "glucose synthesis", "energy storage"],
          estimatedDuration: "6 minutes"
        }
      ].slice(0, episodeCount)
    };

    const scripts: EpisodeScript[] = [
      {
        title: "The Chemistry of Life: Introduction to Photosynthesis",
        description: "Understanding the fundamental process that powers most life on Earth",
        script: `Every breath you take, every bite of food you eat, exists because of one remarkable process: photosynthesis.

Photosynthesis is nature's way of capturing sunlight and converting it into the chemical energy that powers virtually all life on Earth. It's happening right now in the leaves outside your window, in ocean algae, and in plants across the globe.

The fundamental equation of photosynthesis is beautifully simple:
6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂ + ATP

This means: six molecules of carbon dioxide plus six molecules of water, using light energy, produce one molecule of glucose, six molecules of oxygen, and stored chemical energy.

Think about what this represents. Plants take in the carbon dioxide we exhale, combine it with water from their roots, and use sunlight to create sugar - their food - while releasing oxygen as a byproduct. We literally breathe the waste product of plant nutrition.

This process occurs primarily in the chloroplasts, tiny green organelles packed inside plant cells. The green color comes from chlorophyll, a molecule perfectly designed to absorb light energy.

Chlorophyll absorbs red and blue light very efficiently, but reflects green light - which is why plants appear green to our eyes. This reflected green light is actually the energy plants can't use.

But photosynthesis isn't just about making food for plants. The glucose produced becomes the foundation of virtually every food chain on Earth. When you eat a vegetable, you're consuming stored solar energy. When you eat meat, you're consuming an animal that ate plants. Even fossil fuels are ancient stored photosynthetic energy.

The oxygen we breathe is entirely a product of photosynthesis. For the first billion years of Earth's history, there was virtually no oxygen in the atmosphere. It was photosynthetic bacteria and later plants that pumped oxygen into the air, making complex life possible.

In our next episode, we'll dive into exactly how plants capture light energy and convert it into chemical energy in the first stage of photosynthesis.`,
        duration: "6 minutes"
      },
      {
        title: "Light Reactions: Capturing Solar Energy",
        description: "How chloroplasts convert light energy into chemical energy",
        script: `Let's step inside a chloroplast and witness one of nature's most elegant energy conversion systems in action.

The light reactions occur in the thylakoids - flattened, disc-like structures stacked like coins inside chloroplasts. These stacks are called grana, and they're where the magic happens.

When sunlight hits a chlorophyll molecule, it doesn't just warm it up - it actually knocks an electron to a higher energy level. This energized electron is like a charged battery, ready to do work.

This process begins at Photosystem II, a protein complex embedded in the thylakoid membrane. When light hits the chlorophyll here, it excites electrons and sets off a remarkable chain reaction.

The excited electrons are immediately captured by an electron transport chain - think of it as a series of stepping stones, each at a slightly lower energy level. As electrons move down this chain, they release energy, which is used to pump hydrogen ions across the thylakoid membrane.

This creates a concentration gradient - lots of hydrogen ions on one side of the membrane, few on the other. This gradient is like a dam holding back water, storing potential energy.

Meanwhile, to replace the electrons lost from Photosystem II, the complex literally splits water molecules. This is where the oxygen we breathe comes from - it's a byproduct of splitting H₂O to harvest its electrons.

The electrons continue their journey to Photosystem I, where they get another energy boost from light. From here, they're used to create NADPH, a molecule that carries chemical energy.

Finally, those accumulated hydrogen ions rush through ATP synthase, a molecular turbine that harnesses their flow to create ATP - the universal energy currency of cells.

The light reactions have accomplished something remarkable: they've converted light energy into two forms of chemical energy - ATP and NADPH. These molecules are like charged batteries, ready to power the next stage of photosynthesis.

But plants can't eat ATP and NADPH. In our final episode, we'll see how these energy molecules are used to build glucose in the Calvin cycle.`,
        duration: "7 minutes"
      },
      {
        title: "The Calvin Cycle: Building Glucose from Carbon Dioxide",
        description: "The dark reactions that use chemical energy to create organic molecules",
        script: `Now we arrive at the second stage of photosynthesis, where the real construction work happens. The Calvin cycle is where plants take the ATP and NADPH created in the light reactions and use them to build glucose from carbon dioxide.

This process is called the "dark reactions" not because it happens in darkness, but because it doesn't directly require light. It uses the stored energy from the light reactions instead.

The Calvin cycle occurs in the stroma, the fluid-filled space surrounding the thylakoids in chloroplasts. Think of it as the factory floor where the actual product assembly takes place.

The cycle begins with carbon fixation - the process of taking inorganic carbon dioxide from the air and incorporating it into organic molecules. This happens when CO₂ combines with a five-carbon molecule called RuBP (ribulose bisphosphate).

This reaction is catalyzed by RuBisCO, arguably the most important enzyme on Earth. RuBisCO is so crucial that it makes up about 25% of all leaf protein. It's probably the most abundant protein on our planet.

When CO₂ combines with RuBP, it forms an unstable six-carbon compound that immediately splits into two three-carbon molecules called 3-phosphoglycerate. Now the real energy work begins.

Using ATP and NADPH from the light reactions, these three-carbon molecules are converted into G3P (glyceraldehyde 3-phosphate). This is where the stored light energy actually gets incorporated into organic molecules.

Here's the clever part: it takes six turns of the Calvin cycle, fixing six CO₂ molecules, to produce enough G3P to make one glucose molecule. Five of the six G3P molecules are recycled to regenerate RuBP, keeping the cycle running. Only one G3P exits the cycle every six turns.

The glucose produced isn't just plant food - it's the foundation of the plant's structure. Glucose molecules are linked together to form cellulose for cell walls, starch for energy storage, and countless other organic compounds.

This completes the remarkable journey from sunlight to sugar. Solar energy has been captured, converted to chemical energy, and used to build the organic molecules that sustain virtually all life on Earth.

The next time you see a leaf, remember: you're looking at a solar panel more efficient and elegant than anything humans have created, quietly converting sunlight into the energy that powers our world.`,
        duration: "6 minutes"
      }
    ].slice(0, episodeCount);

    return { outline, scripts };
  }

  // Generic educational content for other topics
  const outline: SeriesOutline = {
    title: `Mastering ${topic}`,
    episodes: [
      {
        episodeNumber: 1,
        title: `Foundations of ${topic}`,
        description: `Essential concepts and principles that form the basis of understanding ${topic}`,
        keyTopics: ["core concepts", "fundamental principles", "historical context"],
        estimatedDuration: "6 minutes"
      },
      {
        episodeNumber: 2,
        title: `Practical Applications`,
        description: `Real-world applications and examples of ${topic} in action`,
        keyTopics: ["case studies", "practical examples", "problem-solving techniques"],
        estimatedDuration: "7 minutes"
      },
      {
        episodeNumber: 3,
        title: `Advanced Concepts and Future Directions`,
        description: `Exploring complex aspects and emerging developments in ${topic}`,
        keyTopics: ["advanced theory", "current research", "future implications"],
        estimatedDuration: "6 minutes"
      }
    ].slice(0, episodeCount)
  };

  const scripts: EpisodeScript[] = outline.episodes.map(episode => ({
    title: episode.title,
    description: episode.description,
    script: `Welcome to this comprehensive exploration of ${topic}.

In this episode, we'll examine the fundamental aspects that make this subject both fascinating and important for understanding our world.

${topic} represents a critical area of study that impacts multiple aspects of human knowledge and experience. By understanding these core principles, we build a foundation for deeper learning and practical application.

Throughout this presentation, we'll use concrete examples and real-world applications to illustrate abstract concepts, making them more accessible and memorable.

The key principles we'll explore include the theoretical foundations, practical implementations, and problem-solving strategies that define this field. These elements work together to create a comprehensive understanding.

We'll also examine how this knowledge connects to other areas of study, demonstrating the interconnected nature of learning and discovery.

Remember that mastery comes through understanding concepts rather than memorizing facts. Take time to reflect on how these ideas relate to your existing knowledge and experience.

In our next episode, we'll build upon these foundations to explore more advanced applications and real-world examples.

Thank you for joining this educational journey. Keep questioning, keep learning, and keep growing.`,
    duration: episode.estimatedDuration
  }));

  return { outline, scripts };
}