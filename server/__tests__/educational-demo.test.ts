import { generateEducationalSeries } from '../services/educationalDemo';

describe('EducationalDemo', () => {
  describe('generateEducationalSeries', () => {
    test('should generate only 1 episode for standalone videos', () => {
      const result = generateEducationalSeries(
        'Calculus Limits',
        'Mathematics',
        'Intermediate',
        'Explanatory',
        '5',
        '15-20 minutes'
      );

      expect(result.outline.episodes).toHaveLength(1);
      expect(result.scripts).toHaveLength(1);
    });

    test('should create complete standalone content for calculus limits', () => {
      const result = generateEducationalSeries(
        'Calculus Limits',
        'Mathematics',
        'Intermediate',
        'Explanatory',
        '5',
        '15-20 minutes'
      );

      const episode = result.outline.episodes[0];
      const script = result.scripts[0];

      // Check episode structure
      expect(episode.title).toContain('Complete Guide');
      expect(episode.description).toContain('comprehensive, standalone lesson');
      expect(episode.estimatedDuration).toBe('15-20 minutes');

      // Check script content
      expect(script.script).toContain('Welcome to our complete guide');
      const hasConclusionPhrase = script.script.includes('This completes our comprehensive guide') || script.script.includes('This concludes our comprehensive guide');
      expect(hasConclusionPhrase).toBe(true);
      expect(script.script).not.toContain('next episode');
      expect(script.script).not.toContain('in this series');
      expect(script.script).not.toContain('stay tuned');
    });

    test('should create complete standalone content for computer science', () => {
      const result = generateEducationalSeries(
        'Computer Science',
        'Technology',
        'Beginner',
        'Explanatory',
        '3',
        '10-15 minutes'
      );

      const episode = result.outline.episodes[0];
      const script = result.scripts[0];

      // Check episode structure
      expect(episode.title).toContain('Complete Guide');
      expect(episode.description).toContain('comprehensive, standalone lesson');
      expect(episode.estimatedDuration).toBe('15-20 minutes');

      // Check script content
      expect(script.script).toContain('Welcome to our complete guide');
      const hasConclusionPhrase = script.script.includes('This completes our comprehensive guide') || script.script.includes('This concludes our comprehensive guide');
      expect(hasConclusionPhrase).toBe(true);
      expect(script.script).not.toContain('next episode');
      expect(script.script).not.toContain('in this series');
    });

    test('should create complete standalone content for chemistry', () => {
      const result = generateEducationalSeries(
        'Chemistry',
        'Science',
        'Advanced',
        'Explanatory',
        '4',
        '20-25 minutes'
      );

      const episode = result.outline.episodes[0];
      const script = result.scripts[0];

      // Check episode structure
      expect(episode.title).toContain('Complete Guide');
      expect(script.script).toContain('Welcome to our complete guide');
      const hasConclusionPhrase = script.script.includes('This completes our comprehensive guide') || script.script.includes('This concludes our comprehensive guide');
      expect(hasConclusionPhrase).toBe(true);
      expect(script.script).not.toContain('next episode');
      expect(script.script).not.toContain('in this series');
    });

    test('should create complete standalone content for generic topics', () => {
      const result = generateEducationalSeries(
        'Generic Topic',
        'General',
        'Beginner',
        'Explanatory',
        '2',
        '10-15 minutes'
      );

      const episode = result.outline.episodes[0];
      const script = result.scripts[0];

      // Check episode structure
      expect(episode.title).toContain('Complete Guide');
      expect(script.script).toContain('Welcome to our complete guide');
      const hasConclusionPhrase = script.script.includes('This completes our comprehensive guide') || script.script.includes('This concludes our comprehensive guide');
      expect(hasConclusionPhrase).toBe(true);
      expect(script.script).not.toContain('next episode');
      expect(script.script).not.toContain('in this series');
    });

    test('should include comprehensive key topics for calculus limits', () => {
      const result = generateEducationalSeries(
        'Calculus Limits',
        'Mathematics',
        'Intermediate',
        'Explanatory',
        '5',
        '15-20 minutes'
      );

      const episode = result.outline.episodes[0];
      const expectedTopics = [
        'limit definition',
        'approaching values',
        'graphical interpretation',
        'direct substitution',
        'factoring',
        'rationalizing',
        'squeeze theorem',
        'one-sided limits',
        'continuity'
      ];

      expectedTopics.forEach(topic => {
        expect(episode.keyTopics).toContain(topic);
      });
    });

    test('should generate content with sufficient length for standalone lesson', () => {
      const result = generateEducationalSeries(
        'Calculus Limits',
        'Mathematics',
        'Intermediate',
        'Explanatory',
        '5',
        '15-20 minutes'
      );

      const script = result.scripts[0];
      
      // Content should be substantial for a complete lesson
      expect(script.script.length).toBeGreaterThan(2000);
      
      // Should cover multiple concepts thoroughly
      expect(script.script).toContain('fundamental concept');
      expect(script.script).toContain('example');
      expect(script.script).toContain('method');
      expect(script.script).toContain('technique');
      const hasConclusionWord = /conclusion|completes our comprehensive guide|concludes our comprehensive guide/i.test(script.script);
      expect(hasConclusionWord).toBe(true);
    });

    test('should not contain series introduction language', () => {
      const result = generateEducationalSeries(
        'Any Topic',
        'Any Subject',
        'Any Level',
        'Any Style',
        'Any Number',
        'Any Duration'
      );

      const script = result.scripts[0];
      const seriesIntroPhrases = [
        'in this series',
        'next episode',
        'stay tuned',
        'coming up',
        'we will learn',
        'we are going to learn',
        'over the course of',
        'throughout this series'
      ];

      seriesIntroPhrases.forEach(phrase => {
        expect(script.script.toLowerCase()).not.toContain(phrase.toLowerCase());
      });
    });

    test('should contain standalone lesson language', () => {
      const result = generateEducationalSeries(
        'Any Topic',
        'Any Subject',
        'Any Level',
        'Any Style',
        'Any Number',
        'Any Duration'
      );

      const script = result.scripts[0];
      const standalonePhrases = [
        'complete guide',
        'comprehensive lesson',
        'everything you need to know',
        'covers everything',
        'complete understanding',
        'thorough explanation',
        'comprehensive summary'
      ];

      // At least some standalone language should be present
      const hasStandaloneLanguage = standalonePhrases.some(phrase =>
        script.script.toLowerCase().includes(phrase.toLowerCase())
      );
      
      expect(hasStandaloneLanguage).toBe(true);
    });
  });
});
