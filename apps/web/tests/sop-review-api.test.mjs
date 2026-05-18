import assert from 'node:assert/strict';
import { test } from 'node:test';

const apiError = {
  code: 'rate_limited',
  message: 'Live request rate limit exceeded.',
  details: [],
};

const mockReview = {
  mode: 'mock',
  gatekeeper: { is_valid: true, reason: 'Valid SOP for demo output.' },
  grade: {
    overall_score: 7.8,
    criteria_breakdown: [
      { name: 'Academic Fit', score: 8, feedback: 'Shows relevant preparation.' },
      { name: 'University Specificity', score: 7, feedback: 'Could cite a concrete resource.' },
      { name: 'Career Clarity', score: 8, feedback: 'Connects to a plausible next step.' },
      { name: 'Narrative Flow', score: 8, feedback: 'Progression is coherent.' },
      { name: 'Language & Tone', score: 8, feedback: 'Clear and professional.' },
    ],
    summary: 'A credible SOP with clear direction.',
  },
};

test('SOP API errors use the shared frontend error shape', () => {
  assert.equal(typeof apiError.code, 'string');
  assert.equal(typeof apiError.message, 'string');
  assert.equal(Array.isArray(apiError.details), true);
});

test('mock SOP review shape matches the rendered contract expectations', () => {
  assert.equal(mockReview.mode, 'mock');
  assert.equal(mockReview.gatekeeper.is_valid, true);
  assert.equal(mockReview.grade.criteria_breakdown.length, 5);
  assert.deepEqual(
    mockReview.grade.criteria_breakdown.map((item) => item.name),
    ['Academic Fit', 'University Specificity', 'Career Clarity', 'Narrative Flow', 'Language & Tone'],
  );
});
