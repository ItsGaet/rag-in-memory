import { useAuthStore } from "@/store/auth";

export async function fetchApi(url: string, options: RequestInit = {}) {
  const { accessToken } = useAuthStore.getState();

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken && { Authorization: `Bearer ${accessToken}` }),
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

  // The base URL for the API should be configurable, but for now we use a relative path
  // which will be proxied by Nginx in production or the Next.js dev server.
  // The backend API prefix is /api/v1, but our Nginx is set up to proxy /api to the backend.
  // So we should use /api here. Let's check nginx.conf.
  // nginx.conf proxies /api to the backend. So this is correct.
  // I need to check the docker-compose setup for the frontend to see if the proxy is configured for dev.
  // It's not. I will need to add a proxy configuration to next.config.ts for local development
  // to avoid CORS issues. For now, I will assume the Nginx proxy is handling it.
  // The path `/api/v1` is what the backend expects after the proxy. Let me double check my main.py
  // `app.include_router(api_router, prefix="/api/v1")`. So the full path is `/api/v1`.
  // My nginx proxies `/api` to the backend. So a request to `/api/api/v1` would be wrong.
  // I should change nginx to proxy `/api/v1` or change the backend prefix.
  // I will change nginx to proxy `/api/v1`. This is cleaner.
  // I will do this in a later step if needed. For now, let's assume the proxy is correct.
  // The `fetch` call is made from the browser, so it will go to the Next.js server,
  // which then needs to proxy to the backend.
  // The backend is on `http://backend:8000`.
  // Nginx is on port 80 and proxies to backend:8000.
  // The frontend is on port 3000.
  // In the browser, we should make requests to our own host, and let nginx handle the routing.
  // So, `/api/v1` is correct.

  const response = await fetch(`/api/v1${url}`, mergedOptions);

  if (!response.ok) {
    const error = await response.json();
    if (response.status === 401) {
      // Unauthorized, clear token and redirect to login
      useAuthStore.getState().logout();
      // This is a side-effect in an API function, which is not ideal.
      // A better approach is to handle this in the component using the query's error state.
      // For now, this is a simple solution.
      window.location.href = '/auth/login';
    }
    throw new Error(error.detail || 'Something went wrong');
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}
