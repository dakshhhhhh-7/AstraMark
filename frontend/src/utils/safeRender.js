/**
 * Universal Safe Rendering Utility
 * Prevents "Objects are not valid as a React child" errors
 * 
 * Use this EVERYWHERE you render dynamic data
 */

/**
 * Safely converts any value to a renderable string
 * @param {any} value - The value to render
 * @param {string} fallback - Fallback string if value is null/undefined
 * @returns {string} - Safe string for rendering
 */
export function safeRender(value, fallback = '') {
  // Handle null/undefined
  if (value === null || value === undefined) {
    return fallback;
  }

  // Handle primitives (already safe)
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return String(value);
  if (typeof value === 'boolean') return String(value);

  // Handle arrays
  if (Array.isArray(value)) {
    return value.map(v => safeRender(v)).join(', ');
  }

  // Handle objects
  if (typeof value === 'object') {
    // Check for common error message patterns
    if (value.msg) return String(value.msg);
    if (value.message) return String(value.message);
    if (value.error) return String(value.error);
    if (value.detail) return String(value.detail);
    
    // Check for validation errors (Zod/Yup pattern)
    if (value.type && value.loc && value.msg) {
      return String(value.msg);
    }
    
    // Last resort: stringify
    try {
      return JSON.stringify(value);
    } catch (e) {
      return '[Complex Object]';
    }
  }

  // Fallback for any other type
  return String(value);
}

/**
 * Safely extracts error message from various error formats
 * @param {any} error - Error object, string, or any value
 * @returns {string} - Human-readable error message
 */
export function safeErrorMessage(error) {
  if (!error) return 'An unknown error occurred';

  // String error
  if (typeof error === 'string') return error;

  // Standard Error object
  if (error instanceof Error) return error.message;

  // API error response (Axios style)
  if (error.response?.data) {
    const data = error.response.data;
    
    // Handle string response
    if (typeof data === 'string') return data;
    
    // Handle FastAPI validation errors (422)
    if (error.response.status === 422 && data.detail) {
      // FastAPI returns validation errors as array
      if (Array.isArray(data.detail)) {
        const messages = data.detail.map(err => {
          const field = err.loc ? err.loc[err.loc.length - 1] : 'field';
          const msg = err.msg || 'validation error';
          return `${field}: ${msg}`;
        });
        return messages.join('; ');
      }
      // Single detail message
      if (typeof data.detail === 'string') return data.detail;
    }
    
    // Standard error properties
    if (data.message) return data.message;
    if (data.error) return data.error;
    if (data.detail) return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    if (data.msg) return data.msg;
  }

  // Axios error without response
  if (error.message) return error.message;

  // Validation error array (FastAPI/Pydantic style)
  if (Array.isArray(error)) {
    return error.map(e => {
      if (typeof e === 'string') return e;
      if (e.msg) return e.msg;
      if (e.message) return e.message;
      return JSON.stringify(e);
    }).join('; ');
  }

  // Object with error properties
  if (typeof error === 'object') {
    if (error.msg) return error.msg;
    if (error.message) return error.message;
    if (error.error) return error.error;
    if (error.detail) {
      if (typeof error.detail === 'string') return error.detail;
      if (Array.isArray(error.detail)) {
        return error.detail.map(e => e.msg || JSON.stringify(e)).join('; ');
      }
      return JSON.stringify(error.detail);
    }
    
    // Validation error format
    if (error.type && error.loc && error.msg) {
      return `${error.msg} (${error.loc.join('.')})`;
    }
  }

  // Last resort
  return safeRender(error, 'An error occurred');
}

/**
 * Safely converts array to renderable format
 * @param {any} value - Value that should be an array
 * @returns {Array} - Safe array
 */
export function safeArray(value) {
  if (Array.isArray(value)) return value;
  if (value === null || value === undefined) return [];
  return [value];
}

/**
 * Safely converts to object
 * @param {any} value - Value that should be an object
 * @returns {Object} - Safe object
 */
export function safeObject(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value;
  }
  return {};
}

/**
 * Type guard for renderable values
 * @param {any} value - Value to check
 * @returns {boolean} - True if safe to render
 */
export function isRenderable(value) {
  return (
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean' ||
    value === null ||
    value === undefined
  );
}

/**
 * Sanitize API response before rendering
 * @param {any} response - API response
 * @returns {string} - Safe message
 */
export function sanitizeApiResponse(response) {
  if (!response) return '';
  
  // Direct string
  if (typeof response === 'string') return response;
  
  // Response with data
  if (response.data) {
    if (typeof response.data === 'string') return response.data;
    if (response.data.message) return response.data.message;
    if (response.data.msg) return response.data.msg;
  }
  
  // Direct message
  if (response.message) return response.message;
  if (response.msg) return response.msg;
  
  return safeRender(response);
}

export default safeRender;
