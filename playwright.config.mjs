import { defineConfig } from 'playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: 'buyer-browser.spec.mjs',
  workers: 1,
  retries: 0,
  timeout: 180_000,
  reporter: 'list',
  use: {
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1440, height: 1040 },
    baseURL: 'http://127.0.0.1:18765',
    serviceWorkers: 'block',
  },
  webServer: {
    command: 'python3 -m http.server 18765 --bind 127.0.0.1',
    url: 'http://127.0.0.1:18765',
    reuseExistingServer: false,
    timeout: 15_000,
    stderr: 'ignore',
  },
});
