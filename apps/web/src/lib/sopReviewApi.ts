import type { ApiError, SOPReviewRequest, SOPReviewResponse } from '../contracts/api';

export type SOPReviewMode = 'live' | 'mock';

export class SOPReviewApiError extends Error {
  readonly status: number;
  readonly payload: ApiError;

  constructor(status: number, payload: ApiError) {
    super(payload.message);
    this.name = 'SOPReviewApiError';
    this.status = status;
    this.payload = payload;
  }
}

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

function apiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_STUDY_ABROAD_API_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');
}

function endpointForMode(mode: SOPReviewMode): string {
  return `${apiBaseUrl()}/api/v1/sop/review${mode === 'mock' ? '/mock' : ''}`;
}

function fallbackError(status: number): ApiError {
  if (status === 429) {
    return {
      code: 'rate_limited',
      message: 'Live request rate limit exceeded. Please try again later or use demo mode.',
      details: [],
    };
  }

  if (status >= 500) {
    return {
      code: 'internal_error',
      message: 'The SOP review service is temporarily unavailable. Please try again later.',
      details: [],
    };
  }

  return {
    code: 'http_error',
    message: 'The SOP review request could not be completed.',
    details: [],
  };
}

function isApiError(value: unknown): value is ApiError {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<ApiError>;
  return typeof candidate.code === 'string' && typeof candidate.message === 'string' && Array.isArray(candidate.details);
}

async function parseError(response: Response): Promise<ApiError> {
  try {
    const payload: unknown = await response.json();
    if (isApiError(payload)) return payload;
  } catch {
    // Fall through to the safe frontend message below.
  }

  return fallbackError(response.status);
}

export async function submitSOPReview(payload: SOPReviewRequest, mode: SOPReviewMode): Promise<SOPReviewResponse> {
  let response: Response;

  try {
    response = await fetch(endpointForMode(mode), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new SOPReviewApiError(0, {
      code: 'network_error',
      message: 'Could not reach the SOP review API. Check that the backend is running and try again.',
      details: [],
    });
  }

  if (!response.ok) {
    throw new SOPReviewApiError(response.status, await parseError(response));
  }

  return response.json() as Promise<SOPReviewResponse>;
}
