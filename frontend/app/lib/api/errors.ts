interface ApiErrorOptions {
  status: number;
  code?: string;
}

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, options: ApiErrorOptions = { status: 500 }) {
    super(message);
    Object.setPrototypeOf(this, new.target.prototype);
    this.name = "ApiError";
    this.status = options.status;
    this.code = options.code;
  }
}

export function buildApiError(
  status: number,
  payload: unknown,
  fallbackMessage = "Unexpected API error",
): ApiError {
  if (payload && typeof payload === "object" && !Array.isArray(payload)) {
    const { detail, message, error, code } = payload as {
      detail?: string;
      message?: string;
      error?: string;
      code?: string;
    };

    const composedMessage = detail ?? message ?? error ?? fallbackMessage;

    return new ApiError(composedMessage, { status, code });
  }

  return new ApiError(fallbackMessage, { status });
}
