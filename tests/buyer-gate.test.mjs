import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import YAML from 'yaml';

const pkg = JSON.parse(readFileSync('package.json', 'utf8'));
const workflow = YAML.parse(readFileSync('.github/workflows/publish.yml', 'utf8'));

test('buyer release checks include Python and Chromium, without unpublished tooling', () => {
  assert.match(pkg.scripts['test:buyer'] || '', /test:buyer:node/);
  assert.match(pkg.scripts['test:buyer'] || '', /test:buyer:python/);
  assert.match(pkg.scripts['test:buyer'] || '', /test:browser/);
  assert.match(pkg.scripts['test:buyer:python'] || '', /tests\/test_listing.py.*test_design.py/);
  for (const file of ['analytics', 'analytics-runtime', 'seasonal-assets', 'seasonal-runtime', 'seo', 'site-structure', 'publishing', 'buyer-gate']) {
    assert.ok(pkg.scripts['test:buyer:node'].includes(`tests/${file}.test.mjs`), file);
  }
  assert.doesNotMatch(pkg.scripts['test:buyer:node'], /walkthrough|impeccable-tooling|\*/);
  assert.match(pkg.scripts['test:tooling'] || '', /engine-probe.*node --test tests\/\*.test.mjs/);
  assert.equal(pkg.devDependencies.playwright, '1.64.0');
});

test('PRs validate, only main pushes/manual runs stage and deploy', () => {
  assert.ok(Object.hasOwn(workflow.on, 'pull_request'));
  assert.equal(workflow.jobs.build.if, undefined);
  const steps = workflow.jobs.build.steps;
  assert.ok(steps.some(s => s.run === 'npm run test:buyer'));
  assert.ok(steps.some(s => s.run === 'npx playwright install --with-deps chromium'));
  assert.ok(!steps.some(s => s.run === 'npm test'));
  const main = "github.ref == 'refs/heads/main' && github.event_name != 'pull_request'";
  assert.equal(workflow.jobs.deploy.if, main);
  for (const step of steps.filter(s => s.name === 'Stage buyer-only website' || s.uses?.startsWith('actions/upload-pages-artifact@'))) {
    assert.equal(step.if, main);
  }
  assert.equal(workflow.permissions.contents, 'read');
  assert.equal(workflow.jobs.deploy.needs, 'build');
});
