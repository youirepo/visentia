import type { SeriesOutline, EpisodeScript } from "./openai.js";

// Comprehensive educational content demo system - STANDALONE VIDEOS ONLY
export function generateEducationalSeries(
  topic: string,
  subject: string,
  difficultyLevel: string,
  style: string,
  totalEpisodes: string,
  episodeDuration: string
): { outline: SeriesOutline; scripts: EpisodeScript[] } {
  
  // For now, we only generate 1 episode that contains ALL the content
  const episodeCount = 1;
  
  // Calculus Limits Content - COMPLETE STANDALONE VIDEO
  if (topic.toLowerCase().includes('limit') || topic.toLowerCase().includes('calculus')) {
    const outline: SeriesOutline = {
      title: "Understanding Limits in Calculus - Complete Guide",
      episodes: [
        {
          episodeNumber: 1,
          title: "Complete Guide to Limits in Calculus",
          description: "A comprehensive, standalone lesson covering everything about limits from basic concepts to advanced techniques",
          keyTopics: ["limit definition", "approaching values", "graphical interpretation", "direct substitution", "factoring", "rationalizing", "squeeze theorem", "one-sided limits", "continuity"],
          estimatedDuration: "15-20 minutes"
        }
      ]
    };

    const scripts: EpisodeScript[] = [
      {
        title: "Complete Guide to Limits in Calculus",
        description: "A comprehensive, standalone lesson covering everything about limits from basic concepts to advanced techniques",
        script: `Welcome to our complete guide to limits in calculus! This is a comprehensive lesson that will teach you everything you need to know about limits in one video.

Let's start with the fundamental concept. Imagine you're walking toward a wall. With each step, you get closer and closer, but you never quite reach it. In mathematics, we can describe exactly what happens as you approach that wall - this is the essence of a limit.

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

Now let's learn how to calculate limits systematically. The first and simplest method is direct substitution. If a function is continuous at a point, we can find the limit by simply plugging in the value.

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

Another powerful technique is the squeeze theorem. If we can find two functions that "squeeze" our function and both approach the same limit, then our function must approach that limit too.

Let's look at one-sided limits. Sometimes a function approaches different values from the left and right. Consider f(x) = |x|/x.

As x approaches 0 from the right (positive side), f(x) = x/x = 1
As x approaches 0 from the left (negative side), f(x) = -x/x = -1

Since the left and right limits are different, the overall limit doesn't exist.

Finally, let's talk about continuity. A function is continuous at a point if three conditions are met:
1. The function is defined at that point
2. The limit exists at that point
3. The limit equals the function value at that point

For example, f(x) = x² is continuous everywhere because at any point a, the limit as x approaches a equals a², which is exactly f(a).

This completes our comprehensive guide to limits! You now understand the definition, how to calculate them using various techniques, and how they relate to continuity. Remember, limits are the foundation of calculus - they let us study function behavior at the very points where traditional algebra breaks down.`,
        duration: "15-20 minutes"
      }
    ];

    return { outline, scripts };
  }

  // Computer Science Content - COMPLETE STANDALONE VIDEO
  if (topic.toLowerCase().includes('computer') || topic.toLowerCase().includes('programming') || topic.toLowerCase().includes('code')) {
    const outline: SeriesOutline = {
      title: "How Computers Work - Complete Understanding",
      episodes: [
        {
          episodeNumber: 1,
          title: "Complete Guide to How Computers Work",
          description: "A comprehensive, standalone lesson covering everything from basic concepts to advanced computer architecture",
          keyTopics: ["binary system", "CPU operations", "memory hierarchy", "input/output", "operating systems", "networking basics"],
          estimatedDuration: "15-20 minutes"
        }
      ]
    };

    const scripts: EpisodeScript[] = [
      {
        title: "Complete Guide to How Computers Work",
        description: "A comprehensive, standalone lesson covering everything from basic concepts to advanced computer architecture",
        script: `Welcome to our complete guide to how computers work! This comprehensive lesson will teach you everything you need to know about computer fundamentals in one video.

Let's start with the basics. At their core, computers are machines that process information using binary code - a system of 1s and 0s. But how does this simple system create the complex applications we use every day?

The binary system works because computers use electrical circuits that can be either on (1) or off (0). By combining these binary digits in different patterns, we can represent any number, letter, or instruction.

For example, the letter 'A' in ASCII is represented as 01000001 in binary. The number 42 is 00101010. This binary representation is the foundation of all computer operations.

Now let's understand how computers process this information. The Central Processing Unit, or CPU, is the brain of the computer. It performs three main functions: fetch, decode, and execute.

First, the CPU fetches an instruction from memory. This instruction is just a pattern of 1s and 0s that tells the computer what to do. Next, the CPU decodes this instruction to understand what operation it represents. Finally, it executes the instruction, which might involve adding numbers, moving data, or making decisions.

The CPU contains several key components. The Arithmetic Logic Unit (ALU) performs mathematical operations like addition, subtraction, and comparison. The Control Unit coordinates all the other parts of the CPU. Registers are small, fast memory locations that store data the CPU is currently working with.

Memory is organized in a hierarchy. At the top are CPU registers, which are the fastest but smallest. Next comes cache memory, which is faster than main memory but smaller. Main memory (RAM) is larger but slower, and finally there's storage like hard drives and SSDs, which are the largest but slowest.

When you run a program, the operating system loads it from storage into RAM. The CPU then fetches instructions from RAM, processes them, and stores results back in memory. This fetch-decode-execute cycle happens billions of times per second.

Input and output devices allow computers to interact with the world. Keyboards, mice, and touchscreens are input devices that convert human actions into digital signals. Monitors, speakers, and printers are output devices that convert digital signals back into human-readable form.

The operating system manages all these components. It allocates memory, schedules CPU time, manages files, and provides a user interface. Popular operating systems include Windows, macOS, and Linux.

Networking allows computers to communicate with each other. The internet is a global network of computers that use protocols like TCP/IP to exchange information. When you visit a website, your computer sends a request to a server, which responds with the webpage data.

This completes our comprehensive guide to how computers work! You now understand binary code, CPU operations, memory hierarchy, input/output systems, operating systems, and basic networking. Computers may seem complex, but they're built on these fundamental principles that work together to create the powerful machines we use every day.`,
        duration: "15-20 minutes"
      }
    ];

    return { outline, scripts };
  }

  // Chemistry Content - COMPLETE STANDALONE VIDEO
  if (topic.toLowerCase().includes('chemistry') || topic.toLowerCase().includes('photosynthesis') || topic.toLowerCase().includes('chemical')) {
    const outline: SeriesOutline = {
      title: "The Chemistry of Life - Complete Understanding",
      episodes: [
        {
          episodeNumber: 1,
          title: "Complete Guide to Photosynthesis and Life Chemistry",
          description: "A comprehensive, standalone lesson covering everything from basic chemistry to complex biological processes",
          keyTopics: ["atomic structure", "chemical bonds", "photosynthesis process", "cellular respiration", "energy transfer", "biological molecules"],
          estimatedDuration: "15-20 minutes"
        }
      ]
    };

    const scripts: EpisodeScript[] = [
      {
        title: "Complete Guide to Photosynthesis and Life Chemistry",
        description: "A comprehensive, standalone lesson covering everything from basic chemistry to complex biological processes",
        script: `Welcome to our complete guide to the chemistry of life! This comprehensive lesson will teach you everything you need to know about photosynthesis and life chemistry in one video.

Let's start with the fundamental building blocks. All matter is made of atoms, which contain protons, neutrons, and electrons. Protons and neutrons form the nucleus, while electrons orbit around it. The number of protons determines what element an atom is.

Atoms combine to form molecules through chemical bonds. The most important type of bond for life is the covalent bond, where atoms share electrons. For example, two hydrogen atoms and one oxygen atom share electrons to form water (H2O).

Now let's dive into photosynthesis, the process that powers almost all life on Earth. Photosynthesis converts sunlight, carbon dioxide, and water into glucose (sugar) and oxygen. This process happens in the chloroplasts of plant cells.

The photosynthesis equation is: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2

Photosynthesis has two main stages: the light-dependent reactions and the Calvin cycle. In the light-dependent reactions, sunlight energizes electrons in chlorophyll molecules. These energized electrons travel through an electron transport chain, creating ATP (adenosine triphosphate) and NADPH.

The Calvin cycle uses ATP and NADPH to convert carbon dioxide into glucose. This process is called carbon fixation because it "fixes" carbon from the atmosphere into organic molecules that living things can use.

But why is photosynthesis so important? Glucose provides energy for all living things. When organisms need energy, they break down glucose through cellular respiration, which is essentially the reverse of photosynthesis.

The cellular respiration equation is: C6H12O6 + 6O2 → 6CO2 + 6H2O + energy

This process happens in the mitochondria of cells and releases energy that organisms use for growth, movement, and reproduction.

Energy flows through ecosystems in a cycle. Plants capture solar energy through photosynthesis and store it in glucose. Animals eat plants and break down the glucose to release energy. When animals respire, they release carbon dioxide back into the atmosphere, which plants can use for photosynthesis.

The chemistry of life also involves many other important molecules. Proteins are made of amino acids and perform countless functions in cells. Lipids include fats and oils that store energy and form cell membranes. Nucleic acids like DNA and RNA store and transmit genetic information.

Enzymes are special proteins that speed up chemical reactions. They work by lowering the activation energy needed for reactions to occur. Without enzymes, many life processes would be too slow to sustain life.

This completes our comprehensive guide to the chemistry of life! You now understand atomic structure, chemical bonds, photosynthesis, cellular respiration, energy flow, and biological molecules. The chemistry of life is a beautiful example of how simple chemical principles combine to create the complexity and wonder of living things.`,
        duration: "15-20 minutes"
      }
    ];

    return { outline, scripts };
  }

  // General/Other Topics - COMPLETE STANDALONE VIDEO
  const outline: SeriesOutline = {
    title: `Complete Guide to ${topic}`,
    episodes: [
      {
        episodeNumber: 1,
        title: `Complete Guide to ${topic}`,
        description: `A comprehensive, standalone lesson covering all aspects of ${topic} from basic concepts to advanced understanding`,
        keyTopics: ["fundamental concepts", "core principles", "practical applications", "advanced techniques", "real-world examples"],
        estimatedDuration: "15-20 minutes"
      }
    ]
  };

  const scripts: EpisodeScript[] = [
    {
      title: `Complete Guide to ${topic}`,
      description: `A comprehensive, standalone lesson covering all aspects of ${topic} from basic concepts to advanced understanding`,
      script: `Welcome to our complete guide to ${topic}! This comprehensive lesson will teach you everything you need to know about this fascinating subject in one video.

${topic} is a fundamental concept that touches many aspects of our world. Let's start with the basics and build up to a complete understanding.

At its core, ${topic} involves understanding fundamental principles that govern how things work. These principles form the foundation upon which more complex ideas are built.

Let's explore the key concepts step by step. First, we need to understand the basic terminology and definitions. This gives us the language we need to discuss more advanced ideas.

Next, we'll look at the core principles that make ${topic} work. These are the fundamental rules that apply in all situations, regardless of the specific context.

Once we understand the basics, we can explore practical applications. How is ${topic} used in the real world? What problems does it help solve? These applications show us why understanding ${topic} is so important.

We'll also cover advanced techniques and methods. These build upon the basic principles and allow us to tackle more complex problems and situations.

Throughout this lesson, we'll use real-world examples to illustrate key concepts. These examples help make abstract ideas concrete and easier to understand.

By the end of this comprehensive guide, you'll have a complete understanding of ${topic}. You'll know the basic concepts, understand the core principles, be familiar with practical applications, and be able to use advanced techniques.

This knowledge will serve you well in many areas of life and work. Understanding ${topic} opens up new possibilities and helps you see the world in a different way.

Remember, learning is a journey, and this comprehensive guide is your roadmap to mastering ${topic}. Take your time with each concept, and don't hesitate to review sections if you need clarification.

This concludes our comprehensive guide to ${topic}. We've covered fundamentals, core principles, practical applications, and advanced techniques. Thank you for joining us!`,
      duration: "15-20 minutes"
    }
  ];

  return { outline, scripts };
}