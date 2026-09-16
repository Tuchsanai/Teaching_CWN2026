const {defineConfig}=require('@playwright/test');
const fs=require('fs'),candidate=process.env.WEEK2_CHROMIUM||'/opt/ms-playwright/chromium-1243/chrome-linux64/chrome';
module.exports=defineConfig({testDir:__dirname,testMatch:'*.spec.cjs',timeout:45000,workers:1,retries:0,outputDir:'../../evidence/browser/test-results',reporter:[['list'],['json',{outputFile:'../../evidence/browser/playwright-results.json'}]],use:{browserName:'chromium',headless:true,viewport:{width:1440,height:1000},launchOptions:fs.existsSync(candidate)?{executablePath:candidate}:{}}});
