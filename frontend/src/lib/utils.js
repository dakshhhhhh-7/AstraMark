import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Safely extracts error messages from API response to prevent React crash when rendering.
 * Handles FastAPI/Pydantic validation errors which return arrays of objects.
 * Ensure always returns a string, preventing 'Objects are not valid as a React child'.
 */
export function extractErrorMessage(error, defaultMessage = 'An error occurred') {
  if (!error) return defaultMessage;

  if (typeof error === 'string') return error;

  const detail = error?.response?.data?.detail;

  if (!detail) {
    if (error?.message) return error.message;
    return defaultMessage;
  }

  // Handle FastAPI Pydantic validation errors (array of objects)
  if (Array.isArray(detail)) {
    return detail.map(err => {
      if (err.msg && err.loc) {
        const field = err.loc[err.loc.length - 1] || 'Field';
        return `${field}: ${err.msg}`;
      }
      return err.msg || JSON.stringify(err);
    }).join(', ');
  }

  // Handle case where detail is an object (unexpected but safe)
  if (typeof detail === 'object' && detail !== null) {
    return detail.msg || detail.message || JSON.stringify(detail);
  }

  // Default detail as string
  return String(detail);
}
