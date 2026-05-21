import type { ApiError } from '../contracts/api';

export type ToolMode = 'live' | 'mock';

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

export function apiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_STUDY_ABROAD_API_URL ?? DEFAULT_API_BASE_URL).replace(/\/$/, '');
}

export class ApiClientError extends Error {
  readonly status: number;
  readonly payload: ApiError;

  constructor(status: number, payload: ApiError) {
    super(payload.message);
    this.name = 'ApiClientError';
    this.status = status;
    this.payload = payload;
  }
}

export type FallbackMessages = {
  rateLimited: string;
  serverError: string;
  httpError: string;
  network: string;
};

type ApiClientErrorConstructor = new (status: number, payload: ApiError) => ApiClientError;

function isApiError(value: unknown): value is ApiError {
  if (!value || typeof value !== 'object') return false;
  const candidate = value as Partial<ApiError>;
  return typeof candidate.code === 'string' && typeof candidate.message === 'string' && Array.isArray(candidate.details);
}

function fallbackError(status: number, messages: FallbackMessages): ApiError {
  if (status === 429) {
    return { code: 'rate_limited', message: messages.rateLimited, details: [] };
  }
  if (status >= 500) {
    return { code: 'internal_error', message: messages.serverError, details: [] };
  }
  return { code: 'http_error', message: messages.httpError, details: [] };
}

async function parseError(response: Response, messages: FallbackMessages): Promise<ApiError> {
  try {
    const payload: unknown = await response.json();
    if (isApiError(payload)) return payload;
  } catch {
    // Fall through to the safe frontend message below.
  }

  return fallbackError(response.status, messages);
}

export async function postJson<TRequest, TResponse>(options: {
  url: string;
  payload: TRequest;
  ErrorClass: ApiClientErrorConstructor;
  messages: FallbackMessages;
}): Promise<TResponse> {
  const { url, payload, ErrorClass, messages } = options;
  let response: Response;

  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new ErrorClass(0, { code: 'network_error', message: messages.network, details: [] });
  }

  if (!response.ok) {
    throw new ErrorClass(response.status, await parseError(response, messages));
  }

  return response.json() as Promise<TResponse>;
}
