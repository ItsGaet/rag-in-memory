// A simple fetch wrapper for now.
// In a real app, you'd want to use a more robust solution
// with features like interceptors for adding auth tokens.

export async function fetchApi(url: string, options: RequestInit = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  const response = await fetch(`/api/v1${url}`, mergedOptions);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Something went wrong');
  }

  // For DELETE requests, there might not be a body
  if (response.status === 204) {
    return null;
  }

  return response.json();
}
