import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { test } from 'node:test';
import vm from 'node:vm';
import ts from 'typescript';

function loadClient(relativePath, fetchImpl) {
  const source = readFileSync(join(process.cwd(), relativePath), 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
      esModuleInterop: true,
    },
  });
  const sandbox = {
    exports: {},
    module: { exports: {} },
    process,
    fetch: fetchImpl,
  };
  sandbox.exports = sandbox.module.exports;
  vm.runInNewContext(outputText, sandbox, { filename: relativePath });
  return sandbox.module.exports;
}

const sopPayload = {
  full_name: 'Ada Lovelace',
  mobile: '1234567890',
  university: 'Example University',
  intake: 'Fall 2026',
  country: 'UK',
  sop_text: Array.from({ length: 120 }, () => 'word').join(' '),
};

const admissionsPayload = {
  full_name: 'Ada Lovelace',
  target_intake: 'Fall 2026',
  target_country: 'United Kingdom',
  undergrad_degree_name: 'BSc Computer Science',
  cgpa: 8.5,
  cgpa_scale: 10,
  gre_score: 320,
  gmat_score: null,
  english_test: 'IELTS',
  english_score: 8,
  work_experience_months: 12,
  research_publications: 1,
  target_programs: ['MS CS at Oxford', 'MS AI at Edinburgh'],
};

test('SOP client posts live and mock requests to the configured API base URL', async () => {
  const calls = [];
  process.env.NEXT_PUBLIC_STUDY_ABROAD_API_URL = 'https://api.example.test/';
  const { submitSOPReview } = loadClient('src/lib/sopReviewApi.ts', async (url, init) => {
    calls.push({ url, init });
    return {
      ok: true,
      json: async () => ({
        mode: url.endsWith('/mock') ? 'mock' : 'live',
        gatekeeper: { is_valid: true, reason: 'ok' },
        grade: null,
      }),
    };
  });

  const live = await submitSOPReview(sopPayload, 'live');
  const mock = await submitSOPReview(sopPayload, 'mock');

  assert.equal(live.mode, 'live');
  assert.equal(mock.mode, 'mock');
  assert.deepEqual(
    calls.map((call) => call.url),
    [
      'https://api.example.test/api/v1/sop/review',
      'https://api.example.test/api/v1/sop/review/mock',
    ],
  );
  assert.equal(calls[0].init.method, 'POST');
  assert.deepEqual(JSON.parse(calls[0].init.body), sopPayload);
});

test('admissions client posts live and mock requests to the configured API base URL', async () => {
  const calls = [];
  process.env.NEXT_PUBLIC_STUDY_ABROAD_API_URL = 'https://api.example.test';
  const { submitAdmissionsPrediction } = loadClient(
    'src/lib/admissionsApi.ts',
    async (url, init) => {
      calls.push({ url, init });
      return {
        ok: true,
        json: async () => ({
          mode: url.endsWith('/mock') ? 'mock' : 'live',
          prediction: {
            target_predictions: [],
            profile_strengths: [],
            profile_weaknesses: [],
            actionable_roadmap: [],
            recommended_universities: [],
          },
        }),
      };
    },
  );

  await submitAdmissionsPrediction(admissionsPayload, 'live');
  await submitAdmissionsPrediction(admissionsPayload, 'mock');

  assert.deepEqual(
    calls.map((call) => call.url),
    [
      'https://api.example.test/api/v1/admissions/predict',
      'https://api.example.test/api/v1/admissions/predict/mock',
    ],
  );
  assert.deepEqual(JSON.parse(calls[1].init.body), admissionsPayload);
});

test('frontend API clients preserve structured backend errors and network failures', async () => {
  process.env.NEXT_PUBLIC_STUDY_ABROAD_API_URL = 'https://api.example.test';
  const structuredError = {
    code: 'validation_error',
    message: 'Request validation failed.',
    details: ['cgpa cannot exceed cgpa_scale.'],
  };
  const { submitAdmissionsPrediction, AdmissionsPredictionApiError } = loadClient(
    'src/lib/admissionsApi.ts',
    async () => ({
      ok: false,
      status: 422,
      json: async () => structuredError,
    }),
  );

  await assert.rejects(
    () => submitAdmissionsPrediction(admissionsPayload, 'live'),
    (error) => {
      assert.ok(error instanceof AdmissionsPredictionApiError);
      assert.equal(error.status, 422);
      assert.deepEqual(error.payload, structuredError);
      return true;
    },
  );

  const { submitSOPReview, SOPReviewApiError } = loadClient(
    'src/lib/sopReviewApi.ts',
    async () => {
      throw new Error('connect ECONNREFUSED');
    },
  );

  await assert.rejects(
    () => submitSOPReview(sopPayload, 'live'),
    (error) => {
      assert.ok(error instanceof SOPReviewApiError);
      assert.equal(error.status, 0);
      assert.equal(error.payload.code, 'network_error');
      return true;
    },
  );
});
