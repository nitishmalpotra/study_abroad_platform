import type { AdmissionsPredictionRequest, AdmissionsPredictionResponse, ApiError } from '../contracts/api';
import { ApiClientError, apiBaseUrl, postJson, type ToolMode } from './apiClient';

export type AdmissionsPredictionMode = ToolMode;

export class AdmissionsPredictionApiError extends ApiClientError {
  constructor(status: number, payload: ApiError) {
    super(status, payload);
    this.name = 'AdmissionsPredictionApiError';
  }
}

function endpointForMode(mode: AdmissionsPredictionMode): string {
  return `${apiBaseUrl()}/api/v1/admissions/predict${mode === 'mock' ? '/mock' : ''}`;
}

export async function submitAdmissionsPrediction(
  payload: AdmissionsPredictionRequest,
  mode: AdmissionsPredictionMode,
): Promise<AdmissionsPredictionResponse> {
  return postJson<AdmissionsPredictionRequest, AdmissionsPredictionResponse>({
    url: endpointForMode(mode),
    payload,
    ErrorClass: AdmissionsPredictionApiError,
    messages: {
      rateLimited: 'Live prediction rate limit exceeded. Please try again later or use demo mode.',
      serverError: 'The admit predictor service is temporarily unavailable. Please try again later.',
      httpError: 'The admit prediction request could not be completed.',
      network: 'Could not reach the admit predictor API. Check that the backend is running and try again.',
    },
  });
}
