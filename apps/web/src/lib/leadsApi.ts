import type { ApiError } from '../contracts/api';
import { ApiClientError, apiBaseUrl, postJson } from './apiClient';

export interface LeadPayload {
  tool_name: string;
  phone: string;
  email: string;
  target_country: string;
  target_intake: string;
  target_college: string;
  target_course: string;
  journey_stage: string;
}

export class LeadApiError extends ApiClientError {
  constructor(status: number, payload: ApiError) {
    super(status, payload);
    this.name = 'LeadApiError';
  }
}

export async function submitLead(payload: LeadPayload): Promise<{ status: string }> {
  return postJson<LeadPayload, { status: string }>({
    url: `${apiBaseUrl()}/api/v1/leads`,
    payload,
    ErrorClass: LeadApiError,
    messages: {
      rateLimited: 'Too many requests right now. Please try again in a moment.',
      serverError: 'Lead capture is temporarily unavailable. Please try again later.',
      httpError: 'Could not submit your details. Please check them and try again.',
      network: 'Could not reach the server. Check your connection and try again.',
    },
  });
}
