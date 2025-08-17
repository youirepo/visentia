# Visentia MVP - Automated Test Plan

## 🎯 **Test Objectives**
- Validate video generation pipeline end-to-end
- Ensure text visibility and audio playback work correctly
- Verify content completeness and duration requirements
- Catch regressions in Manim code generation
- Validate API endpoints and error handling

## 🏗️ **Test Architecture**

### **1. Unit Tests**
- **Manim Code Generation**: Test prompt engineering and code validation
- **Video Processing**: Test FFmpeg operations and file handling
- **API Services**: Test individual service functions
- **Validation Logic**: Test Manim code validation rules

### **2. Integration Tests**
- **End-to-End Pipeline**: Full video generation workflow
- **API Endpoints**: Test complete request/response cycles
- **Database Operations**: Test series/episode creation and retrieval
- **File System Operations**: Test audio/video file handling

### **3. E2E Tests**
- **Browser Automation**: Test complete user journey
- **Video Player Functionality**: Test playback, audio, controls
- **Content Generation**: Test different topics and parameters

## 📋 **Test Categories**

### **A. Core Functionality Tests**
1. **Video Generation Pipeline**
   - [ ] User prompt submission
   - [ ] Content generation (OpenAI)
   - [ ] Audio generation (OpenAI TTS)
   - [ ] Manim code generation
   - [ ] Manim code validation
   - [ ] Video rendering
   - [ ] Audio-video combination
   - [ ] Final video serving

2. **Content Quality Tests**
   - [ ] Text visibility (font_size >= 48)
   - [ ] Audio playback functionality
   - [ ] Video duration (2-3 minutes)
   - [ ] Content completeness (not just introductions)
   - [ ] Proper fade in/out animations

3. **API Endpoint Tests**
   - [ ] POST /api/generate-video
   - [ ] GET /api/progress/:seriesId
   - [ ] GET /api/series
   - [ ] GET /api/series/:id
   - [ ] GET /api/video/:filename
   - [ ] GET /api/audio/:filename

### **B. Error Handling Tests**
1. **Input Validation**
   - [ ] Empty prompts
   - [ ] Invalid topic types
   - [ ] Malformed requests
   - [ ] Missing required fields

2. **Processing Failures**
   - [ ] OpenAI API failures
   - [ ] Manim rendering errors
   - [ ] FFmpeg processing failures
   - [ ] File system errors

3. **Recovery Scenarios**
   - [ ] Partial failures in pipeline
   - [ ] Retry mechanisms
   - [ ] Error reporting to user

### **C. Performance Tests**
1. **Response Times**
   - [ ] API endpoint response times
   - [ ] Video generation completion time
   - [ ] File serving performance

2. **Resource Usage**
   - [ ] Memory consumption during rendering
   - [ ] CPU usage during Manim processing
   - [ ] Disk space management

## 🛠️ **Testing Tools & Framework**

### **Backend Testing**
```typescript
// Jest + Supertest for API testing
// Mocks for OpenAI and external services
// Test database setup/teardown
```

### **Frontend Testing**
```typescript
// Playwright for E2E testing
// Component testing with React Testing Library
// Mock service workers for API calls
```

### **Manim Testing**
```python
# pytest for Python code validation
# Mock Manim rendering for fast tests
# Font size validation scripts
```

## 📝 **Test Implementation Plan**

### **Phase 1: Core Unit Tests (Week 1)**
- [ ] Set up testing framework
- [ ] Implement Manim code validation tests
- [ ] Test video processing functions
- [ ] Test API service functions

### **Phase 2: Integration Tests (Week 2)**
- [ ] Test complete video generation pipeline
- [ ] Test database operations
- [ ] Test file system operations
- [ ] Test error handling scenarios

### **Phase 3: E2E Tests (Week 3)**
- [ ] Set up Playwright
- [ ] Implement user journey tests
- [ ] Test video player functionality
- [ ] Test content quality validation

### **Phase 4: Performance & Load Tests (Week 4)**
- [ ] Performance benchmarking
- [ ] Load testing for concurrent requests
- [ ] Resource usage monitoring
- [ ] Optimization recommendations

## 🔍 **Critical Test Scenarios**

### **1. Text Visibility Test**
```typescript
// Test that generated Manim code always uses font_size >= 48
test('Manim code uses visible font sizes', async () => {
  const code = await generateManimCode(topic, content);
  expect(code).toMatch(/font_size=\d+/);
  const fontSizes = code.match(/font_size=(\d+)/g);
  fontSizes.forEach(size => {
    const fontSize = parseInt(size.replace('font_size=', ''));
    expect(fontSize).toBeGreaterThanOrEqual(48);
  });
});
```

### **2. Content Completeness Test**
```typescript
// Test that generated content is complete, not just introductory
test('Generated content is complete lesson', async () => {
  const content = await generateContent(topic);
  expect(content).not.toMatch(/in this series/i);
  expect(content).not.toMatch(/next episode/i);
  expect(content).toMatch(/conclusion/i);
  expect(content.length).toBeGreaterThan(1000);
});
```

### **3. Video Duration Test**
```typescript
// Test that videos meet duration requirements
test('Video duration is 2-3 minutes', async () => {
  const videoPath = await generateVideo(topic);
  const duration = await getVideoDuration(videoPath);
  expect(duration).toBeGreaterThanOrEqual(120); // 2 minutes
  expect(duration).toBeLessThanOrEqual(180);    // 3 minutes
});
```

### **4. Audio Playback Test**
```typescript
// Test that generated videos have working audio
test('Video has working audio track', async () => {
  const videoPath = await generateVideo(topic);
  const audioInfo = await getAudioInfo(videoPath);
  expect(audioInfo.hasAudio).toBe(true);
  expect(audioInfo.audioCodec).toBeDefined();
});
```

## 📊 **Test Metrics & Reporting**

### **Coverage Goals**
- **Code Coverage**: >90% for critical paths
- **API Coverage**: 100% for all endpoints
- **User Journey Coverage**: 100% for main flows

### **Quality Gates**
- [ ] All critical tests pass
- [ ] No regressions in text visibility
- [ ] No regressions in audio playback
- [ ] Performance within acceptable limits

### **Reporting**
- [ ] Test execution reports
- [ ] Coverage reports
- [ ] Performance benchmarks
- [ ] Regression detection

## 🚀 **Implementation Priority**

### **High Priority (Week 1-2)**
1. **Text Visibility Tests** - Critical for user experience
2. **Content Completeness Tests** - Core functionality
3. **Basic API Tests** - Ensure system stability

### **Medium Priority (Week 3)**
1. **E2E User Journey Tests** - Full workflow validation
2. **Error Handling Tests** - Robustness
3. **Performance Benchmarks** - User experience

### **Low Priority (Week 4+)**
1. **Load Testing** - Scalability validation
2. **Advanced Edge Cases** - Comprehensive coverage
3. **Automated Monitoring** - Continuous validation

## 🔧 **Test Environment Setup**

### **Requirements**
- [ ] Test database (separate from production)
- [ ] Mock OpenAI API responses
- [ ] Mock Manim rendering (fast feedback)
- [ ] Test file storage (isolated from production)
- [ ] CI/CD pipeline integration

### **Configuration**
```typescript
// test.config.ts
export const testConfig = {
  database: 'test_db',
  openai: 'mock',
  manim: 'mock',
  storage: 'test_storage',
  timeout: 30000
};
```

## 📈 **Success Criteria**

### **Functional Success**
- [ ] All critical user journeys work end-to-end
- [ ] Text is always visible in generated videos
- [ ] Audio plays correctly in all videos
- [ ] Content is complete and educational

### **Quality Success**
- [ ] Test coverage >90%
- [ ] No critical bugs in main flows
- [ ] Performance meets user expectations
- [ ] Error handling is user-friendly

### **Maintenance Success**
- [ ] Tests catch regressions quickly
- [ ] Test suite is maintainable
- [ ] Automated testing reduces manual QA time
- [ ] Continuous integration prevents broken deployments
