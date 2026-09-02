import { chromium } from 'playwright';

const base = process.env.SECX_URL || 'http://127.0.0.1:8008/secx-grid-prototype/';
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
const consoleErrors = [];
page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
page.on('pageerror', err => consoleErrors.push(String(err)));

await page.goto(base, { waitUntil: 'networkidle' });
await page.waitForFunction(() => document.querySelector('#status')?.textContent.includes('1,156 audited cards'));

const selectedTitle = () => page.locator('.tile.selected strong').innerText();
if ((await selectedTitle()).trim() !== 'SecX') throw new Error('root must start on SecX');
if (await page.locator('.root-grid .tile').count() !== 5) throw new Error('root must contain SecX + four domains');

await page.keyboard.press('ArrowUp');
if (!(await selectedTitle()).includes('Governance')) throw new Error('ArrowUp from SecX must select GRC');
await page.keyboard.press('ArrowLeft');
if ((await selectedTitle()).trim() !== 'SecX') throw new Error('perpendicular root arrow must return to SecX instead of doing nothing');
await page.keyboard.press('ArrowUp');
await page.keyboard.press('Enter');
await page.waitForFunction(() => document.querySelector('#levelLabel')?.textContent === 'DOMAIN');
if (await page.locator('.tile').count() < 5) throw new Error('GRC objective grid not populated');
await page.keyboard.press('Escape');
if (!(await selectedTitle()).includes('Governance')) throw new Error('Escape must restore parent selection');

await page.keyboard.press('Home');
if ((await selectedTitle()).trim() !== 'SecX') throw new Error('Home must return to SecX');
await page.keyboard.press('Space');
if (!(await page.locator('#detailBody').innerText()).includes('Exam map')) throw new Error('Space depth reveal failed');
await page.keyboard.press('Shift+Space');
if ((await page.locator('#detailKicker').innerText()).includes('DEPTH 1')) throw new Error('Shift+Space must reduce depth');

await page.keyboard.press('/');
await page.locator('#searchInput').fill('Policy');
await page.waitForFunction(() => document.querySelectorAll('[data-search-index]').length > 0);
await page.keyboard.press('Enter');
await page.waitForFunction(() => location.hash.startsWith('#card=SX-'));
if (!(await page.locator('#detailKicker').innerText()).startsWith('CARD')) throw new Error('search jump did not land on card');

await page.keyboard.press('m');
const progressText = await page.locator('#chips').innerText();
if (!/Progress · (Learning|Strong|Mastered|Seen)/.test(progressText)) throw new Error('mastery state not visible');

const relatedText = await page.locator('#relatedHint').innerText();
if (!relatedText.includes('related cards')) throw new Error('related count missing');
await page.keyboard.press('r');
await page.waitForFunction(() => document.querySelector('#levelLabel')?.textContent === 'RELATIONSHIPS');
if (await page.locator('.tile').count() < 1) throw new Error('related grid empty');

if (consoleErrors.length) throw new Error(`browser console errors: ${consoleErrors.join(' | ')}`);
console.log('PASS SecX browser smoke: root-all-arrows, hierarchy, parent restore, depth, search, progress, relationships');
await browser.close();
