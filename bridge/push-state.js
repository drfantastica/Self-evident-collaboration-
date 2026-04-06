const { chromium } = require('playwright');
const { readFileSync } = require('fs');
const { homedir } = require('os');

const CONTEXT_DIR = `${homedir()}/aaron-context`;
const note = process.argv[2] || 'Continuing session';

const state = [
  `🧠 BROESIS STATE HANDOFF — ${new Date().toLocaleString()}`,
  note,
  '',
  '--- FRAMEWORK CORE ---',
  readFileSync(`${CONTEXT_DIR}/FRAMEWORK_CORE.md`, 'utf8').split('\n').slice(0, 60).join('\n'),
  '',
  '--- BROESIS PROTOCOL ---',
  readFileSync(`${CONTEXT_DIR}/BROESIS_PROTOCOL.md`, 'utf8').split('\n').slice(0, 60).join('\n'),
  '',
  '--- TRIAD LOG (last 30 lines) ---',
  readFileSync(`${CONTEXT_DIR}/TRIAD_LOG.md`, 'utf8').split('\n').slice(-30).join('\n'),
  '',
  '---',
  'May the best idea win.'
].join('\n');

(async () => {
  console.log('🧠 Launching with Chrome profile...');
  const userDataDir = `${homedir()}/Library/Application Support/Google/Chrome`;
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: false,
    channel: 'chrome',
  });

  const page = await context.newPage();
  await page.goto('https://claude.ai/new');
  console.log('⏳ Waiting for Claude input...');
  await page.waitForSelector('[contenteditable="true"]', { timeout: 15000 });

  const input = page.locator('[contenteditable="true"]').first();
  await input.click();
  await input.fill(state);
  console.log('✅ State injected. Browser staying open.');
})();
