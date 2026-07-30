import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 600, height: 800 });
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle0' });
  
  try {
     console.log("Waiting for canvas to appear due to AutoClicker...");
     await page.waitForSelector('canvas', { timeout: 15000 });
     await new Promise(r => setTimeout(r, 2000));
     const element = await page.$('canvas');
     if (element) {
       await element.screenshot({ path: '../comparisons/app_chart.png' });
       console.log("Screenshot generated and saved to ../comparisons/app_chart.png");
     }
  } catch (e) {
     console.log("Failed to find canvas.");
  }
  
  await browser.close();
  process.exit(0);
})();
