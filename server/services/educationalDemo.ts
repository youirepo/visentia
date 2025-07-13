import type { SeriesOutline, EpisodeScript } from "./openai.js";

// Comprehensive educational content demo system
export function generateEducationalSeries(
  topic: string,
  subject: string,
  difficultyLevel: string,
  style: string,
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

  // Newton's Laws Content
  if (topic.toLowerCase().includes('newton') || topic.toLowerCase().includes('law')) {
    const outline: SeriesOutline = {
      title: "Newton's Three Laws of Motion: The Foundation of Classical Mechanics",
      episodes: [
        {
          episodeNumber: 1,
          title: "The First Law: Objects at Rest and in Motion",
          description: "Understanding inertia and why objects resist changes in their motion",
          keyTopics: ["inertia", "rest and motion", "net force", "equilibrium"],
          estimatedDuration: "8 minutes"
        },
        {
          episodeNumber: 2,
          title: "The Second Law: Force, Mass, and Acceleration",
          description: "Exploring the relationship between force, mass, and acceleration through F=ma",
          keyTopics: ["F=ma", "force vectors", "mass vs weight", "acceleration"],
          estimatedDuration: "9 minutes"
        },
        {
          episodeNumber: 3,
          title: "The Third Law: Action and Reaction Forces",
          description: "Every action has an equal and opposite reaction - understanding force pairs",
          keyTopics: ["action-reaction pairs", "force pairs", "normal force", "tension"],
          estimatedDuration: "8 minutes"
        },
        {
          episodeNumber: 4,
          title: "Applying Newton's Laws: Real-World Problem Solving",
          description: "Using all three laws together to solve physics problems and understand motion",
          keyTopics: ["free body diagrams", "problem solving", "combined forces", "applications"],
          estimatedDuration: "10 minutes"
        }
      ].slice(0, episodeCount)
    };

    const scripts: EpisodeScript[] = [
      {
        title: "The First Law: Objects at Rest and in Motion",
        description: "Understanding inertia and why objects resist changes in their motion",
        script: `Welcome to our exploration of one of physics' most fundamental principles: Newton's First Law of Motion.

Isaac Newton revolutionized our understanding of motion in 1687 with his three laws. The first law, often called the Law of Inertia, states: "An object at rest stays at rest, and an object in motion stays in motion, unless acted upon by an unbalanced force."

Let's break this down. Imagine a book sitting on your desk. According to Newton's First Law, that book will remain exactly where it is forever - unless something pushes or pulls it. The book has inertia, which is the tendency of objects to resist changes in their motion.

But what about objects already in motion? Picture a hockey puck sliding across ice. Without friction, that puck would glide in a straight line at constant speed forever. In the real world, friction acts as an unbalanced force, gradually slowing the puck until it stops.

This leads us to a crucial concept: net force. When forces are balanced - like a book on a table where gravity pulls down and the table pushes up with equal strength - there's no net force. The object remains at rest or continues moving at constant velocity.

Here's where many people get confused. They think moving objects naturally slow down and stop. But Newton showed us this only happens because of forces like friction and air resistance. In space, with no friction, a spacecraft can coast for years without using its engines.

Let's consider a car driving down a highway at constant speed. Is Newton's First Law being violated? Not at all! The engine provides just enough force to overcome air resistance and friction. The net force is zero, so the car maintains constant velocity.

Inertia depends on mass. A bowling ball has more inertia than a tennis ball - it's harder to start rolling and harder to stop once it's moving. This is why seat belts are crucial. When a car suddenly stops, your body's inertia keeps it moving forward at the car's original speed.

Newton's First Law also explains why you feel pushed backward when a car accelerates forward. Your body's inertia resists the change in motion, so you feel pressed into your seat as the car pushes you forward.

Think about this law in everyday situations: Why do you lurch forward when a bus stops suddenly? Why does a coin keep sliding when you quickly pull a tablecloth from under it? The answer is always inertia - objects resist changes in their motion.

In our next episode, we'll discover what happens when forces aren't balanced, leading us to Newton's Second Law and the famous equation F=ma.`,
        duration: "8 minutes"
      },
      {
        title: "The Second Law: Force, Mass, and Acceleration",
        description: "Exploring the relationship between force, mass, and acceleration through F=ma",
        script: `Now we dive into Newton's Second Law, perhaps the most mathematically powerful of the three laws: Force equals mass times acceleration, or F=ma.

This elegant equation tells us exactly what happens when forces become unbalanced. When there's a net force acting on an object, that object will accelerate in the direction of the net force.

Let's unpack each component. Force is a push or pull measured in Newtons. Mass is the amount of matter in an object, measured in kilograms. Acceleration is the rate of change of velocity, measured in meters per second squared.

The beauty of F=ma is that it works both ways. If you know any two variables, you can calculate the third. Need to find acceleration? Divide force by mass: a = F/m. Want to know how much force is needed? Multiply mass by desired acceleration: F = ma.

Here's a crucial insight: acceleration is inversely proportional to mass. This means if you apply the same force to two objects, the lighter object will accelerate more. Push a shopping cart and a car with equal force - the cart accelerates much more because it has less mass.

Let's work through a real example. Imagine you're pushing a 50-kilogram box with a force of 100 Newtons. Using F=ma, we get: 100 = 50 × a, so a = 2 meters per second squared. The box accelerates at 2 m/s².

But wait - what if there's friction? Say friction creates a 30-Newton force opposing your push. The net force becomes 100 - 30 = 70 Newtons. Now the acceleration is 70 ÷ 50 = 1.4 m/s². Always remember to consider all forces to find the net force.

Newton's Second Law also reveals why mass and weight are different. Weight is a force - specifically, the gravitational force acting on an object. Weight = mass × gravitational acceleration, or W = mg. On Earth, g = 9.8 m/s², so a 10-kilogram object weighs 98 Newtons.

This explains why astronauts are weightless in space. Their mass doesn't change, but without gravity creating a net force, they don't experience weight. They're in free fall, constantly accelerating toward Earth at the same rate as their spacecraft.

Consider a car accelerating from rest. The engine provides force through the wheels, but the car's acceleration depends on both this driving force and the car's mass. A sports car accelerates faster than a truck with the same engine because it has less mass.

Force is a vector, which means it has both magnitude and direction. If multiple forces act on an object, you must add them as vectors. Forces in the same direction add together; forces in opposite directions subtract.

Picture a tug-of-war. If Team A pulls with 500 Newtons east and Team B pulls with 300 Newtons west, the net force is 200 Newtons east. The rope (and whoever's attached) accelerates eastward.

Newton's Second Law also explains why airbags save lives. In a crash, the car stops quickly, but your body continues moving due to inertia. The airbag provides a force to stop you, but it increases the time over which this happens. Since impulse (force × time) equals change in momentum, extending the time reduces the required force.

Next time, we'll explore Newton's Third Law and discover why forces always come in pairs.`,
        duration: "9 minutes"
      },
      {
        title: "The Third Law: Action and Reaction Forces",
        description: "Every action has an equal and opposite reaction - understanding force pairs",
        script: `Newton's Third Law is often stated as "For every action, there is an equal and opposite reaction." But this simple phrase contains profound implications for how forces work in our universe.

More precisely, the Third Law states: "When object A exerts a force on object B, object B simultaneously exerts an equal and opposite force on object A." These are called action-reaction pairs, and they always occur together.

Here's the key insight: forces never exist alone. They always come in pairs. When you push on a wall, the wall pushes back on you with exactly the same force. When Earth pulls you down with gravity, you pull Earth up with the same gravitational force.

Let's explore some examples to make this concrete. When you walk, you push backward against the ground with your foot. By Newton's Third Law, the ground pushes forward on your foot with equal force. This forward force from the ground is what propels you forward.

Think about swimming. You push water backward with your hands and feet. The water pushes you forward with equal force. No water, no forward motion - which is why swimming in air doesn't work!

Cars demonstrate this beautifully. The engine doesn't directly push the car forward. Instead, the wheels push backward against the road. The road pushes forward on the wheels, moving the car. This is why cars can't accelerate on frictionless ice - there's no grip for the action-reaction pair.

Here's where students often get confused: "If forces are always equal and opposite, why does anything move?" The answer lies in understanding that action-reaction pairs act on different objects.

When you push a shopping cart, you exert a force on the cart, and the cart exerts an equal force on you. But these forces act on different objects. The force on the cart accelerates the cart forward. The force on you pushes you backward, but your feet grip the ground, preventing you from sliding.

Rockets provide the most dramatic example of Newton's Third Law. A rocket doesn't "push against" space. Instead, it expels hot gases downward at high speed. By Newton's Third Law, the gases push the rocket upward with equal force. This is why rockets work in the vacuum of space.

Consider a book resting on a table. Gravity pulls the book downward with its weight. But the book isn't accelerating downward, so there must be another force. The table exerts an upward normal force equal to the book's weight. But wait - these aren't action-reaction pairs! They both act on the same object (the book).

The true action-reaction pairs are: (1) Earth pulls book down, book pulls Earth up; (2) Book pushes table down, table pushes book up. Each pair involves forces on different objects.

Newton's Third Law explains many everyday phenomena. When you sit in a chair, you compress it slightly. The chair's material pushes back, supporting your weight. When you catch a baseball, the ball exerts a force on your glove, and your glove exerts an equal force on the ball, slowing it down.

Birds fly by pushing air downward with their wings. The air pushes the bird upward with equal force. Fish swim by pushing water backward; the water pushes the fish forward.

Even explosions follow Newton's Third Law. When a firecracker explodes, pieces fly in all directions. But the total momentum remains zero - for every piece flying one way, there's momentum flying the opposite way.

Understanding action-reaction pairs helps explain why some things are harder than others. It's difficult to jump when standing on ice because the ice can't provide much horizontal reaction force. It's easier to push a car than to push a wall because the car can move, allowing the action-reaction pair to result in motion.

In our final episode, we'll see how all three laws work together to solve real physics problems.`,
        duration: "8 minutes"
      },
      {
        title: "Applying Newton's Laws: Real-World Problem Solving",
        description: "Using all three laws together to solve physics problems and understand motion",
        script: `Now we bring Newton's three laws together to solve real-world problems. This is where physics becomes a powerful tool for understanding and predicting motion in our world.

The key to applying Newton's laws is systematic problem-solving. We start by identifying all forces acting on an object, draw a free-body diagram, apply Newton's laws, and solve for unknowns.

Let's work through a classic problem: a 10-kilogram box sliding down a 30-degree inclined plane with friction. We want to find the box's acceleration.

Step 1: Identify the forces. Gravity pulls straight down with force mg = 10 × 9.8 = 98 Newtons. The inclined surface exerts a normal force perpendicular to the surface. Friction acts parallel to the surface, opposing motion.

Step 2: Break forces into components. Gravity has two components: one parallel to the incline (mg sin 30° = 98 × 0.5 = 49 N down the incline) and one perpendicular (mg cos 30° = 98 × 0.866 = 85 N into the surface).

Step 3: Apply Newton's laws. Perpendicular to the incline, there's no acceleration, so normal force equals the perpendicular component of gravity: N = 85 N. Friction force equals the coefficient of friction times normal force: f = μN.

Step 4: Apply Newton's Second Law parallel to the incline. Net force = mg sin θ - f = ma. If the coefficient of friction is 0.3, then f = 0.3 × 85 = 25.5 N. Net force = 49 - 25.5 = 23.5 N. Acceleration = 23.5 ÷ 10 = 2.35 m/s².

This problem uses all three laws: First Law (perpendicular equilibrium), Second Law (F=ma parallel to incline), and Third Law (normal force as reaction to gravity's perpendicular component).

Let's consider a more complex system: two masses connected by a rope over a pulley. A 5-kg mass hangs vertically while a 3-kg mass slides on a horizontal surface with friction coefficient 0.2.

For the hanging mass: T - mg = ma, so T - 49 = 5a (where T is tension and a is acceleration).
For the sliding mass: T - f = ma, so T - 5.88 = 3a (where f = 0.2 × 29.4 = 5.88 N).

Solving these simultaneously: From the first equation, T = 49 + 5a. Substituting into the second: 49 + 5a - 5.88 = 3a, which gives 43.12 = -2a, so a = -21.56 m/s². Wait - that's impossible!

Let me recalculate. The hanging mass accelerates downward, the sliding mass accelerates horizontally. For consistent directions: hanging mass: mg - T = ma, so 49 - T = 5a. Sliding mass: T - f = ma, so T - 5.88 = 3a.

Adding equations: 49 - 5.88 = 8a, so a = 5.39 m/s². The system accelerates at 5.39 m/s² with tension T = 22.05 N.

Newton's laws also explain vehicle safety. Crumple zones in cars increase the time during which deceleration occurs. Since impulse (force × time) equals change in momentum, increasing time decreases force, reducing injury.

Seat belts work through Newton's First Law. When a car stops suddenly, passengers continue moving due to inertia. Seat belts apply force to change the passenger's motion, preventing collision with the dashboard.

Consider a rocket launch. Initially, the rocket's thrust must overcome its weight just to lift off. As fuel burns, the rocket's mass decreases, so the same thrust produces greater acceleration (a = F/m). This is why rockets accelerate faster as they climb.

Athletes use Newton's laws strategically. Sprinters push backward against starting blocks to generate forward force. High jumpers run forward to build horizontal momentum, then convert it to vertical momentum at takeoff.

Newton's laws explain why it's harder to stop a heavy truck than a car traveling at the same speed. The truck has more momentum (mass × velocity), requiring greater force or more time to stop. This is why truck drivers maintain larger following distances.

Understanding these laws helps engineers design everything from bridges to spacecraft. They calculate forces, predict accelerations, and ensure structures can withstand the forces they'll encounter.

The beauty of Newton's laws is their universality. The same principles that govern a falling apple also govern planetary orbits, rocket launches, and every motion in our daily lives. From the smallest particle to the largest celestial body, these three elegant laws describe the fundamental nature of motion in our universe.

This completes our journey through Newton's Laws of Motion - the foundation upon which all of classical mechanics is built.`,
        duration: "10 minutes"
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