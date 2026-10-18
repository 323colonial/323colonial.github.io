import { defineConfig } from 'playwright/test';

export default defineConfig({
  testDir: './tests',
  testMatch: ['buyer-browser.spec.mjs', 'buyer-accessibility.spec.mjs', 'visitor-browser.spec.mjs'],
  workers: 2,
  retries: 0,
  timeout: 180_000,
  reporter: 'list',
  use: {
    browserName: process.env.PLAYWRIGHT_BROWSER || 'chromium',
    headless: true,
    viewport: { width: 1440, height: 1040 },
    baseURL: 'http://127.0.0.1:18765',
    serviceWorkers: 'block',
  },
  webServer: {
    // Python's default backlog of 5 resets asset requests from parallel browsers.
    command: `python3 -c "import runpy, socketserver; socketserver.TCPServer.request_queue_size = 128; runpy.run_module('http.server', run_name='__main__')" 18765 --bind 127.0.0.1`,
    url: 'http://127.0.0.1:18765',
    reuseExistingServer: false,
    timeout: 15_000,
    stderr: 'ignore',
  },
});
