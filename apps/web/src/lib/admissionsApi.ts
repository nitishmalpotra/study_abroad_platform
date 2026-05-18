import type { AdmissionsPredictionRequest, AdmissionsPredictionResponse, ApiError } from '../contracts/api';

export type AdmissionsPredictionMode = 'live' | 'mock';

export class AdmissionsPredictionApiError extends Error {
  readonly status: number;
  readonly payload: ApiError;

  constructor(status: number, payload: ApiError) {
    super(payload.message);
    this.name = 'AdmissionsPredictionApiError';
    this.status = status;
    this.payload = payload;
  }
}

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

function apiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_STUDY_ABROAD_API_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');
}

function endpointForMode(mode: AdmissionsPredictionMode): string {
  return `${apiBaseUrl()}/api/v1/admissions/predict${mode === 'mock' ? '/mock' : ''}`;
}

function fallbackError(status: number): ApiError {
  if (status === 429) {
    return {
      code: 'rate_limited',
      message: 'Live prediction rate limit exceeded. Please try again later or use demo mode.',
      details: [],
    };
  }

  if (status >= 500) {
    return {
      code: 'internal_error',
      message: 'The admit predictor service is temporarily unavailable. Please try again later.',
      details: [],
    };
  }

  return {
    code: 'http_error',
    message: 'The admit prediction request could not be completed.',
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
    // Fall through to a safe frontend message.
  }

  return fallbackError(response.status);
}

export async function submitAdmissionsPrediction(
  payload: AdmissionsPredictionRequest,
  mode: AdmissionsPredictionMode,
): Promise<AdmissionsPredictionResponse> {
  let response: Response;

  try {
    response = await fetch(endpointForMode(mode), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new AdmissionsPredictionApiError(0, {
      code: 'network_error',
      message: 'Could not reach the admit predictor API. Check that the backend is running and try again.',
      details: [],
    });
  }

  if (!response.ok) {
    throw new AdmissionsPredictionApiError(response.status, await parseError(response));
  }

  return response.json() as Promise<AdmissionsPredictionResponse>;
}
