# 🧪 Visentia MVP Testing Guide

## 🎯 **Overview**

This document outlines the automated testing strategy for the Visentia MVP, ensuring that all critical functionality works correctly and regressions are caught quickly.

## 🚀 **Quick Start**

### **Run All Tests**
```bash
# Run tests with coverage
./run-tests.sh

# Or use npm directly
npm run test:coverage
```

### **Run Tests in Watch Mode**
```bash
npm run test:watch
```

### **Run Tests for CI/CD**
```bash
npm run test:ci
```

## 📋 **Test Categories**

### **1. Unit Tests** (`server/__tests__/`)
- **Manim Code Validation**: Ensures generated code meets font size and structure requirements
- **Content Generation**: Validates educational content completeness
- **Service Functions**: Tests individual service logic
- **Utility Functions**: Tests helper functions and utilities

### **2. Integration Tests** (Coming Soon)
- **API Endpoints**: Tests complete request/response cycles
- **Database Operations**: Tests data persistence and retrieval
- **File Processing**: Tests video/audio file handling
- **Pipeline Workflow**: Tests end-to-end video generation

### **3. E2E Tests** (Coming Soon)
- **Browser Automation**: Tests complete user journeys
- **Video Player**: Tests playback functionality
- **Content Quality**: Validates generated video quality

## 🔍 **Critical Test Scenarios**

### **Text Visibility Tests**
```typescript
// Ensures all Manim text uses font_size >= 48
test('Manim code uses visible font sizes', async () => {
  const code = await generateManimCode(topic, content);
  const fontSizes = code.match(/font_size=(\d+)/g);
  fontSizes.forEach(size => {
    const fontSize = parseInt(size.replace('font_size=', ''));
    expect(fontSize).toBeGreaterThanOrEqual(48);
  });
});
```

### **Content Completeness Tests**
```typescript
// Ensures content is complete, not just introductory
test('Generated content is complete lesson', async () => {
  const content = await generateContent(topic);
  expect(content).not.toMatch(/in this series/i);
  expect(content).toContain('conclusion');
  expect(content.length).toBeGreaterThan(1000);
});
```

### **Video Duration Tests**
```typescript
// Ensures videos meet 2-3 minute requirement
test('Video duration is 2-3 minutes', async () => {
  const videoPath = await generateVideo(topic);
  const duration = await getVideoDuration(videoPath);
  expect(duration).toBeGreaterThanOrEqual(120); // 2 minutes
  expect(duration).toBeLessThanOrEqual(180);    // 3 minutes
});
```

## 🛠️ **Test Framework Setup**

### **Jest Configuration** (`jest.config.js`)
- **TypeScript Support**: Uses `ts-jest` for TypeScript files
- **Coverage Reporting**: Generates HTML and LCOV reports
- **Test Timeout**: 30 seconds for long-running tests
- **Module Mapping**: Aliases for clean imports

### **Test Utilities** (`test-setup.ts`)
- **Global Mocks**: File system, console, path operations
- **Helper Functions**: Mock data generators
- **Environment Setup**: Test environment variables

### **Mock Strategy**
- **OpenAI API**: Mock responses for consistent testing
- **File System**: Mock file operations for fast tests
- **External Services**: Mock dependencies for isolation

## 📊 **Test Coverage Goals**

### **Code Coverage Targets**
- **Overall Coverage**: >90%
- **Critical Paths**: 100%
- **API Endpoints**: 100%
- **Core Services**: >95%

### **Quality Gates**
- [ ] All critical tests pass
- [ ] No regressions in text visibility
- [ ] No regressions in audio playback
- [ ] Performance within acceptable limits

## 🔧 **Adding New Tests**

### **1. Create Test File**
```bash
# Create test file in appropriate directory
touch server/__tests__/new-service.test.ts
```

### **2. Write Test Structure**
```typescript
import { NewService } from '../services/new-service';

describe('NewService', () => {
  let service: NewService;

  beforeEach(() => {
    service = new NewService();
  });

  test('should perform expected behavior', () => {
    // Test implementation
    expect(result).toBe(expected);
  });
});
```

### **3. Run Tests**
```bash
# Run specific test file
npm test -- new-service.test.ts

# Run tests in watch mode
npm run test:watch
```

## 🚨 **Common Test Issues**

### **Font Size Validation Failures**
- **Problem**: Tests fail because generated code uses `font_size < 48`
- **Solution**: Check Manim generator prompts and ensure `font_size=48+` is enforced

### **Content Completeness Failures**
- **Problem**: Tests fail because content contains series introduction language
- **Solution**: Verify educational content generation creates standalone lessons

### **Timing Validation Failures**
- **Problem**: Tests fail because total `Wait()` time is too short
- **Solution**: Ensure Manim code includes sufficient timing for 2-3 minute videos

## 📈 **Continuous Integration**

### **GitHub Actions** (Coming Soon)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run test:ci
```

### **Pre-commit Hooks** (Coming Soon)
- Run tests before each commit
- Ensure code coverage requirements are met
- Validate code quality standards

## 🎯 **Test Priorities**

### **Phase 1: Critical Functionality** (Week 1)
- [x] Manim code validation
- [x] Content completeness validation
- [ ] Basic API endpoint testing
- [ ] Font size enforcement

### **Phase 2: Integration Testing** (Week 2)
- [ ] End-to-end video generation
- [ ] Database operations
- [ ] File processing workflows
- [ ] Error handling scenarios

### **Phase 3: E2E Testing** (Week 3)
- [ ] User journey automation
- [ ] Video player functionality
- [ ] Content quality validation
- [ ] Performance benchmarking

### **Phase 4: Advanced Testing** (Week 4+)
- [ ] Load testing
- [ ] Security testing
- [ ] Accessibility testing
- [ ] Cross-browser compatibility

## 📚 **Testing Best Practices**

### **Test Structure**
- **Arrange**: Set up test data and conditions
- **Act**: Execute the function being tested
- **Assert**: Verify expected outcomes

### **Naming Conventions**
- **Test Names**: Describe expected behavior
- **File Names**: Match service names with `.test.ts` suffix
- **Directory Structure**: Mirror source code structure

### **Mock Strategy**
- **External APIs**: Always mock for consistent testing
- **File Operations**: Mock for fast, reliable tests
- **Database**: Use test database or mocks

### **Assertions**
- **Specific**: Test exact expected values
- **Comprehensive**: Cover edge cases and error conditions
- **Readable**: Use descriptive assertion messages

## 🔍 **Debugging Tests**

### **Common Commands**
```bash
# Run single test with verbose output
npm test -- --verbose --testNamePattern="specific test name"

# Run tests with debugging
npm test -- --detectOpenHandles --forceExit

# Check test coverage for specific files
npm run test:coverage -- --collectCoverageFrom="server/services/*.ts"
```

### **Test Isolation**
- Each test should be independent
- Use `beforeEach` and `afterEach` for cleanup
- Avoid shared state between tests

## 📞 **Getting Help**

### **Test Issues**
1. Check test output for specific error messages
2. Verify test data and mock setup
3. Ensure dependencies are properly mocked
4. Check test environment configuration

### **Adding New Tests**
1. Follow existing test patterns
2. Use provided test utilities
3. Ensure proper coverage of edge cases
4. Add tests for both success and failure scenarios

---

## 🎉 **Success Metrics**

- **Test Coverage**: >90%
- **Test Execution Time**: <30 seconds
- **Critical Test Pass Rate**: 100%
- **Regression Detection**: <24 hours
- **Manual QA Reduction**: >70%

This testing framework ensures that your Visentia MVP maintains high quality and catches issues before they reach users!
