// Configuration for additional UI libraries

// React CountUp configuration
export const countUpDefaults = {
  duration: 1.5,
  separator: ',',
  decimal: '.',
  prefix: '',
  suffix: '',
  useEasing: true,
  useGrouping: true,
  preserveValue: false,
};

// Currency formatting for Indian Rupees
export const currencyCountUpConfig = {
  ...countUpDefaults,
  prefix: '₹',
  duration: 2,
  separator: ',',
  useGrouping: true,
};

// Percentage formatting
export const percentageCountUpConfig = {
  ...countUpDefaults,
  suffix: '%',
  duration: 1,
  decimals: 1,
};

// Large number formatting (for metrics like leads, users)
export const largeNumberCountUpConfig = {
  ...countUpDefaults,
  duration: 1.5,
  separator: ',',
  useGrouping: true,
};

// React Intersection Observer configuration
export const intersectionObserverDefaults = {
  threshold: 0.1,
  triggerOnce: true,
  rootMargin: '0px 0px -50px 0px',
};

// Configuration for different animation triggers
export const animationTriggerConfig = {
  // For hero sections - trigger early
  hero: {
    threshold: 0.2,
    triggerOnce: true,
    rootMargin: '0px 0px -100px 0px',
  },
  // For cards and components - standard trigger
  card: {
    threshold: 0.1,
    triggerOnce: true,
    rootMargin: '0px 0px -50px 0px',
  },
  // For metrics and counters - trigger when mostly visible
  metrics: {
    threshold: 0.5,
    triggerOnce: true,
    rootMargin: '0px',
  },
  // For lists and grids - trigger early for stagger effect
  list: {
    threshold: 0.05,
    triggerOnce: true,
    rootMargin: '0px 0px -20px 0px',
  },
  // For footer and bottom content
  footer: {
    threshold: 0.1,
    triggerOnce: true,
    rootMargin: '0px 0px 50px 0px',
  },
};

// Utility functions for formatting numbers
export const formatCurrency = (value, locale = 'en-IN') => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

export const formatNumber = (value, locale = 'en-IN') => {
  return new Intl.NumberFormat(locale).format(value);
};

export const formatPercentage = (value, decimals = 1) => {
  return `${value.toFixed(decimals)}%`;
};

// Utility function to format large numbers with suffixes
export const formatLargeNumber = (value) => {
  if (value >= 1000000000) {
    return `${(value / 1000000000).toFixed(1)}B`;
  }
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toString();
};

// Custom hook for animated counters with intersection observer
export const useAnimatedCounter = (endValue, options = {}) => {
  const {
    duration = 2,
    startValue = 0,
    formatter = (value) => value,
    triggerConfig = animationTriggerConfig.metrics,
  } = options;

  return {
    endValue,
    duration,
    startValue,
    formatter,
    triggerConfig,
  };
};

// Presets for common counter types
export const counterPresets = {
  revenue: (value) => ({
    endValue: value,
    duration: 2.5,
    formatter: formatCurrency,
    triggerConfig: animationTriggerConfig.metrics,
  }),
  
  leads: (value) => ({
    endValue: value,
    duration: 1.5,
    formatter: formatNumber,
    triggerConfig: animationTriggerConfig.metrics,
  }),
  
  percentage: (value) => ({
    endValue: value,
    duration: 1,
    formatter: (val) => formatPercentage(val, 1),
    triggerConfig: animationTriggerConfig.metrics,
  }),
  
  growthScore: (value) => ({
    endValue: value,
    duration: 2,
    formatter: (val) => Math.round(val).toString(),
    triggerConfig: animationTriggerConfig.metrics,
  }),
  
  largeNumber: (value) => ({
    endValue: value,
    duration: 1.8,
    formatter: formatLargeNumber,
    triggerConfig: animationTriggerConfig.metrics,
  }),
};

// Configuration for responsive behavior
export const responsiveConfig = {
  // Breakpoints (matching Tailwind CSS)
  breakpoints: {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536,
  },
  
  // Animation adjustments for mobile
  mobile: {
    reducedMotion: true,
    fasterAnimations: true,
    smallerScales: true,
  },
  
  // Touch-friendly configurations
  touch: {
    minTouchTarget: 44, // 44px minimum touch target
    tapDelay: 100, // Delay for tap feedback
    swipeThreshold: 50, // Minimum swipe distance
  },
};

// Accessibility configurations
export const a11yConfig = {
  // Respect user's motion preferences
  respectReducedMotion: true,
  
  // Focus management
  focusRing: {
    width: 3,
    color: '#22D3EE', // Neon accent color
    offset: 2,
  },
  
  // Screen reader configurations
  screenReader: {
    announceChanges: true,
    liveRegionPolite: 'polite',
    liveRegionAssertive: 'assertive',
  },
  
  // High contrast support
  highContrast: {
    enabled: false, // Will be detected from system
    adjustments: {
      increaseContrast: 1.2,
      boldText: true,
    },
  },
};