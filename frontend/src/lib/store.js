import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

// User store for authentication and profile data
export const useUserStore = create(
  persist(
    immer((set, get) => ({
      // State
      user: null,
      subscription: null,
      preferences: {
        theme: 'dark',
        notifications: true,
        autoMode: false,
      },
      isAuthenticated: false,
      
      // Actions
      setUser: (user) => set((state) => {
        state.user = user;
        state.isAuthenticated = !!user;
      }),
      
      setSubscription: (subscription) => set((state) => {
        state.subscription = subscription;
      }),
      
      updatePreferences: (newPreferences) => set((state) => {
        state.preferences = { ...state.preferences, ...newPreferences };
      }),
      
      logout: () => set((state) => {
        state.user = null;
        state.subscription = null;
        state.isAuthenticated = false;
      }),
      
      // Getters
      hasSubscription: () => {
        const { subscription } = get();
        return subscription && subscription.status === 'active';
      },
      
      canUseAutoMode: () => {
        const { subscription } = get();
        return subscription && ['pro', 'growth'].includes(subscription.tier);
      },
    })),
    {
      name: 'astramark-user-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        subscription: state.subscription,
        preferences: state.preferences,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Dashboard store for metrics and real-time data
export const useDashboardStore = create(
  immer((set, get) => ({
    // State
    metrics: {
      revenue: 0,
      leads: 0,
      engagement: 0,
      growthScore: 0,
    },
    insights: [],
    liveFeed: [],
    isLoading: false,
    lastUpdated: null,
    
    // Actions
    setMetrics: (metrics) => set((state) => {
      state.metrics = { ...state.metrics, ...metrics };
      state.lastUpdated = new Date().toISOString();
    }),
    
    setInsights: (insights) => set((state) => {
      state.insights = insights;
    }),
    
    addLiveFeedItem: (item) => set((state) => {
      state.liveFeed.unshift({
        ...item,
        id: Date.now(),
        timestamp: new Date().toISOString(),
      });
      // Keep only last 50 items
      if (state.liveFeed.length > 50) {
        state.liveFeed = state.liveFeed.slice(0, 50);
      }
    }),
    
    setLoading: (isLoading) => set((state) => {
      state.isLoading = isLoading;
    }),
    
    updateGrowthScore: (score) => set((state) => {
      state.metrics.growthScore = score;
    }),
    
    // Clear all dashboard data
    clearDashboard: () => set((state) => {
      state.metrics = { revenue: 0, leads: 0, engagement: 0, growthScore: 0 };
      state.insights = [];
      state.liveFeed = [];
      state.lastUpdated = null;
    }),
  }))
);

// Onboarding store for multi-step flow state
export const useOnboardingStore = create(
  persist(
    immer((set, get) => ({
      // State
      currentStep: 1,
      totalSteps: 3,
      businessSetup: {
        businessType: '',
        targetAudience: '',
        goals: [],
      },
      analysisResults: null,
      isCompleted: false,
      
      // Actions
      setCurrentStep: (step) => set((state) => {
        state.currentStep = Math.max(1, Math.min(step, state.totalSteps));
      }),
      
      nextStep: () => set((state) => {
        if (state.currentStep < state.totalSteps) {
          state.currentStep += 1;
        }
      }),
      
      previousStep: () => set((state) => {
        if (state.currentStep > 1) {
          state.currentStep -= 1;
        }
      }),
      
      updateBusinessSetup: (data) => set((state) => {
        state.businessSetup = { ...state.businessSetup, ...data };
      }),
      
      setAnalysisResults: (results) => set((state) => {
        state.analysisResults = results;
      }),
      
      completeOnboarding: () => set((state) => {
        state.isCompleted = true;
      }),
      
      resetOnboarding: () => set((state) => {
        state.currentStep = 1;
        state.businessSetup = {
          businessType: '',
          targetAudience: '',
          goals: [],
        };
        state.analysisResults = null;
        state.isCompleted = false;
      }),
      
      // Getters
      getProgress: () => {
        const { currentStep, totalSteps } = get();
        return (currentStep / totalSteps) * 100;
      },
      
      canProceed: () => {
        const { currentStep, businessSetup } = get();
        switch (currentStep) {
          case 1:
            return businessSetup.businessType && businessSetup.targetAudience;
          case 2:
            return true; // AI analysis step
          case 3:
            return true; // Results step
          default:
            return false;
        }
      },
    })),
    {
      name: 'astramark-onboarding-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);

// Auto Mode store for premium feature state
export const useAutoModeStore = create(
  immer((set, get) => ({
    // State
    isEnabled: false,
    isProcessing: false,
    lastAction: null,
    performance: {
      contentGenerated: 0,
      adsManaged: 0,
      emailsSent: 0,
      totalRevenue: 0,
    },
    
    // Actions
    enableAutoMode: () => set((state) => {
      state.isEnabled = true;
    }),
    
    disableAutoMode: () => set((state) => {
      state.isEnabled = false;
      state.isProcessing = false;
    }),
    
    setProcessing: (isProcessing) => set((state) => {
      state.isProcessing = isProcessing;
    }),
    
    recordAction: (action) => set((state) => {
      state.lastAction = {
        ...action,
        timestamp: new Date().toISOString(),
      };
      
      // Update performance metrics
      switch (action.type) {
        case 'content':
          state.performance.contentGenerated += 1;
          break;
        case 'ads':
          state.performance.adsManaged += 1;
          break;
        case 'email':
          state.performance.emailsSent += 1;
          break;
      }
      
      if (action.revenue) {
        state.performance.totalRevenue += action.revenue;
      }
    }),
    
    resetPerformance: () => set((state) => {
      state.performance = {
        contentGenerated: 0,
        adsManaged: 0,
        emailsSent: 0,
        totalRevenue: 0,
      };
    }),
  }))
);

// UI store for global UI state
export const useUIStore = create(
  immer((set, get) => ({
    // State
    sidebarOpen: false,
    mobileMenuOpen: false,
    notifications: [],
    isLoading: false,
    
    // Actions
    toggleSidebar: () => set((state) => {
      state.sidebarOpen = !state.sidebarOpen;
    }),
    
    toggleMobileMenu: () => set((state) => {
      state.mobileMenuOpen = !state.mobileMenuOpen;
    }),
    
    addNotification: (notification) => set((state) => {
      state.notifications.push({
        ...notification,
        id: Date.now(),
        timestamp: new Date().toISOString(),
      });
    }),
    
    removeNotification: (id) => set((state) => {
      state.notifications = state.notifications.filter(n => n.id !== id);
    }),
    
    setGlobalLoading: (isLoading) => set((state) => {
      state.isLoading = isLoading;
    }),
    
    clearNotifications: () => set((state) => {
      state.notifications = [];
    }),
  }))
);