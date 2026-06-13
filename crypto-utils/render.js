const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  await page.goto('file:///home/user/Polling_-api/crypto-utils/diagram.html');
  const el = await page.$('body');
  await el.screenshot({ path: '/home/user/Polling_-api/crypto-utils/aes_gcm_diagram.png' });
  await browser.close();
  console.log('rendered');
})();
