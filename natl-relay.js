#!/usr/bin/env node
// natl-relay.js — NATL Console relay server
// Bridges pi-bridge.html ↔ Slack API
// POST  / → send message to Slack channel
// GET   /?channel=C0XX&limit=25 → read channel history
// Usage: node natl-relay.js   (runs on port 7778)

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Minimal env loader (no dotenv dep). Reads .env.local from script dir.
(function loadEnvLocal() {
  const envFile = path.join(__dirname, '.env.local');
  if (!fs.existsSync(envFile)) return;
  for (const line of fs.readFileSync(envFile, 'utf8').split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eq = trimmed.indexOf('=');
    if (eq < 0) continue;
    const key = trimmed.slice(0, eq).trim();
    let val = trimmed.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) ||
        (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = val;
  }
})();

const PORT = 7778;
const BOT_TOKEN = process.env.SLACK_BOT_TOKEN;
if (!BOT_TOKEN) {
  console.error('FATAL: SLACK_BOT_TOKEN not set. Add to .env.local or environment.');
  process.exit(1);
}

// In-memory EEG state — written by crown-stream-relay.mjs via POST /eeg-state
// Read by AVP passthrough or any local consumer via GET /eeg-state
let eegState = {
  updatedAt: null,
  deviceId: "1c1aac337ba06f9d0db3b5caa68a8dc4",
  data: null
};

// In-memory biosensor state — BITalino ECG/EDA/ACC
let biosensorState = {
  updatedAt: null,
  device: "BITalino-40-A5",
  data: null
};

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function slackRequest(method, path, body) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const opts = {
      hostname: 'slack.com',
      path: `/api/${path}`,
      method,
      headers: {
        'Authorization': `Bearer ${BOT_TOKEN}`,
        'Content-Type': 'application/json; charset=utf-8',
        ...(payload ? { 'Content-Length': Buffer.byteLength(payload) } : {}),
      },
    };
    const req = https.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { reject(new Error('JSON parse error: ' + data)); }
      });
    });
    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

const server = http.createServer(async (req, res) => {
  // CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, CORS);
    res.end();
    return;
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);

  // ── GET /eeg-state — read current Crown band power ────────────────
  if (req.method === 'GET' && url.pathname === '/eeg-state') {
    res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
    res.end(JSON.stringify(eegState));
    return;
  }

  // ── POST /eeg-state — written by crown-stream-relay.mjs ──────────
  if (req.method === 'POST' && url.pathname === '/eeg-state') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const incoming = JSON.parse(body);
        eegState = { ...eegState, ...incoming, updatedAt: new Date().toISOString() };
        res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
      } catch(e) {
        res.writeHead(400, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: 'invalid JSON' }));
      }
    });
    return;
  }

  // ── GET /biosensor-state — read BITalino ECG/EDA/ACC ─────────────
  if (req.method === 'GET' && url.pathname === '/biosensor-state') {
    res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
    res.end(JSON.stringify(biosensorState));
    return;
  }

  // ── POST /biosensor-state — written by bitalino-relay.py ─────────
  if (req.method === 'POST' && url.pathname === '/biosensor-state') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try {
        const incoming = JSON.parse(body);
        biosensorState = { ...biosensorState, ...incoming, updatedAt: new Date().toISOString() };
        res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: true }));
      } catch(e) {
        res.writeHead(400, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: 'invalid JSON' }));
      }
    });
    return;
  }

  // ── GET: read channel history ──────────────────────────────────────
  if (req.method === 'GET') {
    const channel = url.searchParams.get('channel');
    const limit = parseInt(url.searchParams.get('limit') || '25', 10);
    if (!channel) {
      res.writeHead(400, { ...CORS, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: 'missing channel param' }));
      return;
    }
    try {
      const data = await slackRequest('GET',
        `conversations.history?channel=${encodeURIComponent(channel)}&limit=${limit}`);
      res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
      res.end(JSON.stringify(data));
    } catch(e) {
      res.writeHead(500, { ...CORS, 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: false, error: e.message }));
    }
    return;
  }

  // ── POST: send message ─────────────────────────────────────────────
  if (req.method === 'POST') {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', async () => {
      let msg;
      try { msg = JSON.parse(body); } catch(e) {
        res.writeHead(400, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: 'invalid JSON' }));
        return;
      }
      try {
        const payload = {
          channel: msg.channel,
          username: msg.username,
          icon_emoji: msg.icon_emoji,
          text: msg.text,
          ...(msg.blocks ? { blocks: msg.blocks } : {}),
        };
        const data = await slackRequest('POST', 'chat.postMessage', payload);
        res.writeHead(200, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify(data));
      } catch(e) {
        res.writeHead(500, { ...CORS, 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ ok: false, error: e.message }));
      }
    });
    return;
  }

  res.writeHead(404, CORS);
  res.end('Not found');
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`\n⬡ NATL Relay live on http://127.0.0.1:${PORT}`);
  console.log(`  POST /            → send to Slack`);
  console.log(`  GET  /?channel=   → read channel history`);
  console.log(`  GET  /eeg-state   → read Crown band power state`);
  console.log(`  POST /eeg-state   → write Crown band power state`);
  console.log(`\nPress Ctrl+C to stop.\n`);
});
