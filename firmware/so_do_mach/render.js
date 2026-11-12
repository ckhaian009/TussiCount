const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 2 });
  await p.goto('file://' + __dirname + '/so_do.html'); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: __dirname + '/TussiCount_So_do_mach.pdf', format: 'A4', landscape: true, printBackground: true });
  await p.setViewportSize({ width: 1123, height: 794 });
  const s = await p.$$('section.trang');
  for (let i = 0; i < s.length; i++) await s[i].screenshot({ path: __dirname + `/trang${i+1}.png`, scale: 'device' });
  await b.close();
})();
