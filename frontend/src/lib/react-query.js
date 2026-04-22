import { QueryClient } from '@tanstack/react-query';

// Create a client with optimized settings for the AstraMark SaaS frontend
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes by default
      staleTime: 5 * 60 * 1000,
      // Keep data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
      // Retry failed requests 3 times
      retry: 3,
      // Retry with exponential backoff
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      // Refetch on window focus for real-time data
      refetchOnWindowFocus: true,
      // Refetch when coming back online
      refetchOnReconnect: true,
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
      // Show optimistic updates immediately
      onMutate: () => {
        // This can be overridden per mutation
      },
    },
  },
});

// Query keys factory for consistent key management
export const queryKeys = {
  // User-related queries
  user: {
    profile: ['user', 'profile'],
    subscription: ['user', 'subscription'],
    preferences: ['user', 'preferences'],
  },
  // Dashboard-related queries
  dashboard: {
    metrics: ['dashboard', 'metrics'],
    insights: ['dashboard', 'insights'],
    liveFeed: ['dashboard', 'liveFeed'],
    growthScore: ['dashboard', 'growthScore'],
  },
  // Business-related queries
  business: {
    setup: ['business', 'setup'],
    analysis: ['business', 'analysis'],
    content: ['business', 'content'],
    campaigns: ['business', 'campaigns'],
  },
  // Auto Mode queries
  autoMode: {
    status: ['autoMode', 'status'],
    actions: ['autoMode', 'actions'],
    performance: ['autoMode', 'performance'],
  },
};

// Helper function to invalidate related queries
export const invalidateQueries = (queryClient, keys) => {
  return queryClient.invalidateQueries({ queryKey: keys });
};

// Helper function for optimistic updates
export const optimisticUpdate = (queryClient, queryKey, updater) => {
  queryClient.setQueryData(queryKey, updater);
};