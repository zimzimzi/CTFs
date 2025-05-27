const { chromium } = require('playwright');

(async () => {
  while (true) {
    const browser = await chromium.launch();
    const page = await browser.newPage();
    page.on('dialog', dialog => dialog.accept());

    const now = new Date();
    const formattedDate = now.toISOString();
    process.stdout.write(`${formattedDate} - Task started\n`);

    await page.goto('http://web:8000/');
    await page.fill('#username', 'manager');
    await page.fill('#password', '********REDACTED********');
    await page.click('[type="submit"]');
    await page.goto('http://web:8000/?action=order-problems');

    const orders = await page.locator('xpath=//table//a');
    let ordersCount = await orders.count();
    process.stdout.write(`${formattedDate} - ${ordersCount} new orders\n`);

    if (ordersCount === 0) {
      await page.waitForTimeout(5000);
    } else {
      await orders.first().click();
      process.stdout.write(`${formattedDate} - open order\n`);
      await page.waitForSelector('a[class="btn btn-success"]');
      const problemDescription = await page.locator('xpath=//body//div//p[1]').innerText();
      const homeOrigin = new URL(page.url()).origin;
      const problemWords = problemDescription.split(' ');

      for (const word of problemWords) {
        const urlPattern = /^http:\/\/web:8000\//;
        if (urlPattern.test(word) && word !== homeOrigin) {
          const currentProblem = page.url()
          await page.goto(word);
          await page.waitForTimeout(2000);
          await page.goto(currentProblem);
        }
      }

      await page.click('a[class="btn btn-success"]');
      process.stdout.write(`${formattedDate} - delete order\n`);
      await page.waitForSelector('xpath=//h1[text()="Order Problems List"]');
    }

    await browser.close();
  }
})();
