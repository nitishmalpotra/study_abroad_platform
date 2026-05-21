import type { ApiError, SOPReviewRequest, SOPReviewResponse } from '../contracts/api';
import { ApiClientError, apiBaseUrl, postJson, type ToolMode } from './apiClient';

export type SOPReviewMode = ToolMode;

export class SOPReviewApiError extends ApiClientError {
  constructor(status: number, payload: ApiError) {
    super(status, payload);
    this.name = 'SOPReviewApiError';
  }
}

function endpointForMode(mode: SOPReviewMode): string {
  return `${apiBaseUrl()}/api/v1/sop/review${mode === 'mock' ? '/mock' : ''}`;
}

export async function submitSOPReview(payload: SOPReviewRequest, mode: SOPReviewMode): Promise<SOPReviewResponse> {
  return postJson<SOPReviewRequest, SOPReviewResponse>({
    url: endpointForMode(mode),
    payload,
    ErrorClass: SOPReviewApiError,
    messages: {
      rateLimited: 'Live request rate limit exceeded. Please try again later or use demo mode.',
      serverError: 'The SOP review service is temporarily unavailable. Please try again later.',
      httpError: 'The SOP review request could not be completed.',
      network: 'Could not reach the SOP review API. Check that the backend is running and try again.',
    },
  });
}
