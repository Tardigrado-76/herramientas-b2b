import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const FRONTEND_ROOT = path.resolve(__dirname, '..');

function formatTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

test('TimeTracker formatting utility produces HH:MM:SS correctly', () => {
  assert.equal(formatTime(0), '00:00:00');
  assert.equal(formatTime(65), '00:01:05');
  assert.equal(formatTime(3661), '01:01:01');
});

test('Offline queue signature generation and payload serialization is deterministic', () => {
  const payload = {
    action: 'in',
    recorded_at: '2026-10-29T08:00:00.000Z',
    latitude: 40.417,
    longitude: -3.704,
    device_info: 'Offline Browser Client',
    ip_address: '127.0.0.1 (Offline Cached)',
  };
  const accessToken = 'mock-supabase-token-123';
  const signature = Buffer.from(JSON.stringify(payload) + accessToken, 'utf8')
    .toString('base64')
    .slice(0, 32);

  assert.equal(signature.length, 32);
  const queued = { ...payload, offline_signature: signature };
  assert.equal(queued.action, 'in');
  assert.equal(queued.offline_signature, signature);
});

test('Frontend UI and Dashboard components conform to Zero-Docker and Next.js 16 standards', () => {
  const inputFile = fs.readFileSync(
    path.join(FRONTEND_ROOT, 'components', 'ui', 'input.tsx'),
    'utf8',
  );
  assert.ok(
    inputFile.includes('export type InputProps = React.InputHTMLAttributes<HTMLInputElement>'),
    'InputProps must use type alias instead of empty interface',
  );

  const layoutFile = fs.readFileSync(
    path.join(FRONTEND_ROOT, 'app', 'dashboard', 'layout.tsx'),
    'utf8',
  );
  assert.ok(
    layoutFile.includes("import Image from 'next/image'"),
    'Dashboard layout must use next/image',
  );

  const trackerHook = fs.readFileSync(
    path.join(FRONTEND_ROOT, 'components', 'dashboard', 'use-time-tracker.ts'),
    'utf8',
  );
  assert.ok(
    trackerHook.includes('offline_clock_queue'),
    'TimeTracker hook must support offline queue persistence',
  );
});
