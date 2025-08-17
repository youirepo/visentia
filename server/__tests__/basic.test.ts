// Basic test to verify testing framework setup
describe('Testing Framework Setup', () => {
  test('should have access to global test utilities', () => {
    expect(global.testUtils).toBeDefined();
    expect(typeof global.testUtils.createMockOpenAIResponse).toBe('function');
    expect(typeof global.testUtils.createMockManimCode).toBe('function');
    expect(typeof global.testUtils.createMockContent).toBe('function');
  });

  test('should be able to create mock data', () => {
    const mockResponse = global.testUtils.createMockOpenAIResponse('test content');
    expect(mockResponse.choices).toHaveLength(1);
    expect(mockResponse.choices[0].message.content).toBe('test content');

    const mockCode = global.testUtils.createMockManimCode(72);
    expect(mockCode).toContain('font_size=72');
    expect(mockCode).toContain('class TestScene(Scene)');

    const mockContent = global.testUtils.createMockContent(true);
    expect(mockContent).toContain('complete lesson');
    expect(mockContent).not.toContain('next episode');
  });

  test('should have proper test environment', () => {
    expect(process.env.NODE_ENV).toBe('test');
    expect(process.env.OPENAI_API_KEY).toBe('test-key');
  });
});
