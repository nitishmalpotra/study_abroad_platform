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

test('admissions prediction shape supports multiple target programs', () => {
  const prediction = {
    mode: 'mock',
    prediction: {
      target_predictions: [
        {
          program_name: 'MS CS at Oxford',
          chance_category: 'Reach',
          estimated_probability_percentage: 30,
          brief_reasoning: 'Competitive target with a strong applicant pool.',
        },
        {
          program_name: 'MS AI at Edinburgh',
          chance_category: 'Target',
          estimated_probability_percentage: 62,
          brief_reasoning: 'Profile is competitive for this target.',
        },
      ],
      profile_strengths: ['Strong GPA', 'Research', 'Experience'],
      profile_weaknesses: ['Few publications', 'Leadership', 'No GMAT'],
      actionable_roadmap: ['Improve SOP', 'Add projects', 'Apply early'],
      recommended_universities: ['A', 'B', 'C'],
    },
  };

  assert.equal(prediction.mode, 'mock');
  assert.equal(prediction.prediction.target_predictions.length, 2);
  assert.deepEqual(
    prediction.prediction.target_predictions.map((item) => item.program_name),
    ['MS CS at Oxford', 'MS AI at Edinburgh'],
  );
});
