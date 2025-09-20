#!/usr/bin/env node
/**
 * Test script for Hybrid Visual Generator
 * Tests the complete pipeline from HTML generation to video capture
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

async function testHybridSystem() {
    console.log('🧪 Testing Hybrid Visual Generator System...\n');

    try {
        // Test 1: Check Python dependencies
        console.log('1️⃣  Testing Python dependencies...');
        try {
            await execAsync('python3 -c "import jinja2, matplotlib, numpy, PIL; print(\'✅ Python dependencies OK\')"');
            console.log('   ✅ Python dependencies are installed\n');
        } catch (error) {
            console.log('   ❌ Python dependencies missing. Run: pip3 install -r server/requirements-hybrid.txt\n');
            return false;
        }

        // Test 2: Check Node.js dependencies
        console.log('2️⃣  Testing Node.js dependencies...');
        try {
            await execAsync('node -c "const puppeteer = require(\'puppeteer\'); console.log(\'✅ Node.js dependencies OK\')"');
            console.log('   ✅ Node.js dependencies are installed\n');
        } catch (error) {
            console.log('   ❌ Node.js dependencies missing. Run: npm install\n');
            return false;
        }

        // Test 3: Create test data
        console.log('3️⃣  Creating test scene data...');
        const testSceneData = {
            sceneNumber: 1,
            title: "Test Fractions",
            description: "A test scene for fractions",
            narration: "This is a test scene. We have $\\frac{1}{2}$ which represents half of something. Here's a simple diagram:\n\n```mermaid\ngraph LR\n    A[Whole] --> B[Half]\n    B --> C[Quarter]\n```",
            duration: 10.0,
            visualElements: ["Circle", "Fraction"],
            animationType: "Create"
        };

        const testSeriesData = {
            title: "Test Series",
            subject: "Mathematics",
            difficulty_level: "Beginner",
            style: "Visual and Demonstrative"
        };

        const outputDir = path.join(__dirname, 'generated-scenes');
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const sceneDataPath = path.join(outputDir, 'test-scene-data.json');
        const seriesDataPath = path.join(outputDir, 'test-series-data.json');

        fs.writeFileSync(sceneDataPath, JSON.stringify(testSceneData, null, 2));
        fs.writeFileSync(seriesDataPath, JSON.stringify(testSeriesData, null, 2));
        console.log('   ✅ Test data created\n');

        // Test 4: Generate HTML
        console.log('4️⃣  Testing HTML generation...');
        const pythonScript = path.join(__dirname, 'services', 'hybrid-visual-generator.py');
        const htmlCommand = `python3 "${pythonScript}" "${sceneDataPath}" "${seriesDataPath}" "${outputDir}"`;
        
        try {
            const { stdout, stderr } = await execAsync(htmlCommand);
            if (stderr) console.log('   ⚠️  Python stderr:', stderr);
            console.log('   ✅ HTML generation successful');
            console.log('   📄 Output:', stdout.trim(), '\n');
        } catch (error) {
            console.log('   ❌ HTML generation failed:', error.message, '\n');
            return false;
        }

        // Test 5: Check generated HTML file
        console.log('5️⃣  Verifying generated HTML...');
        const expectedHtmlPath = path.join(outputDir, 'scene-01-TestFractions.html');
        if (fs.existsSync(expectedHtmlPath)) {
            console.log('   ✅ HTML file generated successfully');
            console.log(`   📁 File: ${expectedHtmlPath}\n`);
        } else {
            console.log('   ❌ HTML file not found\n');
            return false;
        }

        // Test 6: Test video capture (short duration for testing)
        console.log('6️⃣  Testing video capture...');
        const nodeScript = path.join(__dirname, 'services', 'video-capture.js');
        const testVideoPath = path.join(outputDir, 'test-scene.mp4');
        const captureCommand = `node "${nodeScript}" "${expectedHtmlPath}" "${testVideoPath}" 3`;
        
        try {
            console.log('   🎥 Capturing 3-second test video...');
            const { stdout, stderr } = await execAsync(captureCommand, { timeout: 30000 });
            if (stderr) console.log('   ⚠️  Node.js stderr:', stderr);
            console.log('   ✅ Video capture successful');
            console.log('   📄 Output:', stdout.trim(), '\n');
        } catch (error) {
            console.log('   ❌ Video capture failed:', error.message, '\n');
            return false;
        }

        // Test 7: Verify generated video
        console.log('7️⃣  Verifying generated video...');
        if (fs.existsSync(testVideoPath)) {
            const stats = fs.statSync(testVideoPath);
            console.log('   ✅ Video file generated successfully');
            console.log(`   📁 File: ${testVideoPath}`);
            console.log(`   📊 Size: ${Math.round(stats.size / 1024)} KB\n`);
        } else {
            console.log('   ❌ Video file not found\n');
            return false;
        }

        console.log('🎉 All tests passed! Hybrid Visual Generator is working correctly.\n');
        
        // Cleanup
        console.log('🧹 Cleaning up test files...');
        try {
            fs.unlinkSync(sceneDataPath);
            fs.unlinkSync(seriesDataPath);
            console.log('   ✅ Test files cleaned up\n');
        } catch (error) {
            console.log('   ⚠️  Could not clean up test files\n');
        }

        console.log('📋 Next steps:');
        console.log('1. Update your video generation pipeline to use HybridVisualService');
        console.log('2. Replace SceneProcessor with HybridVisualService in directGeneration.ts');
        console.log('3. Test with real educational content\n');

        return true;

    } catch (error) {
        console.error('❌ Test failed with error:', error);
        return false;
    }
}

// Run the test
if (require.main === module) {
    testHybridSystem().then(success => {
        process.exit(success ? 0 : 1);
    });
}

module.exports = { testHybridSystem };

