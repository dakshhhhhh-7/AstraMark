// Framer Motion animation presets for AstraMark SaaS frontend

// Spring physics presets
export const springs = {
  // Gentle spring for smooth interactions
  gentle: {
    type: "spring",
    stiffness: 120,
    damping: 14,
    mass: 1,
  },
  // Bouncy spring for playful interactions
  bouncy: {
    type: "spring",
    stiffness: 300,
    damping: 20,
    mass: 1,
  },
  // Snappy spring for quick feedback
  snappy: {
    type: "spring",
    stiffness: 400,
    damping: 25,
    mass: 0.8,
  },
  // Smooth spring for elegant transitions
  smooth: {
    type: "spring",
    stiffness: 100,
    damping: 15,
    mass: 1.2,
  },
};

// Easing presets
export const easings = {
  easeInOut: [0.4, 0, 0.2, 1],
  easeOut: [0, 0, 0.2, 1],
  easeIn: [0.4, 0, 1, 1],
  sharp: [0.4, 0, 0.6, 1],
};

// Animation variants for common patterns
export const fadeInUp = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.2,
      ease: easings.easeIn,
    },
  },
};

export const fadeInDown = {
  initial: {
    opacity: 0,
    y: -20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    y: 20,
    transition: {
      duration: 0.2,
      ease: easings.easeIn,
    },
  },
};

export const fadeInLeft = {
  initial: {
    opacity: 0,
    x: -20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    x: 20,
    transition: {
      duration: 0.2,
      ease: easings.easeIn,
    },
  },
};

export const fadeInRight = {
  initial: {
    opacity: 0,
    x: 20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: 0.2,
      ease: easings.easeIn,
    },
  },
};

export const scaleIn = {
  initial: {
    opacity: 0,
    scale: 0.9,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.2,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.15,
      ease: easings.easeIn,
    },
  },
};

export const slideInUp = {
  initial: {
    y: "100%",
    opacity: 0,
  },
  animate: {
    y: 0,
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: easings.easeOut,
    },
  },
  exit: {
    y: "100%",
    opacity: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeIn,
    },
  },
};

// Staggered animation for lists
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeOut,
    },
  },
};

// Button hover and tap animations
export const buttonHover = {
  scale: 1.05,
  transition: {
    duration: 0.2,
    ease: easings.easeOut,
  },
};

export const buttonTap = {
  scale: 0.95,
  transition: {
    duration: 0.1,
    ease: easings.sharp,
  },
};

// Loading animations
export const pulse = {
  animate: {
    scale: [1, 1.05, 1],
    opacity: [0.7, 1, 0.7],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

export const spin = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: "linear",
    },
  },
};

// Particle effect for AI analysis
export const particleFloat = {
  animate: {
    y: [-10, 10, -10],
    x: [-5, 5, -5],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

// Growth metrics counter animation
export const countUp = {
  initial: {
    opacity: 0,
    scale: 0.8,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: easings.easeOut,
    },
  },
};

// Auto Mode toggle animation
export const toggleSlide = {
  initial: {
    x: 0,
  },
  animate: {
    x: 24, // Adjust based on toggle width
    transition: springs.snappy,
  },
};

// Live feed item animation
export const liveFeedItem = {
  initial: {
    opacity: 0,
    y: -20,
    scale: 0.95,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    x: 100,
    scale: 0.95,
    transition: {
      duration: 0.3,
      ease: easings.easeIn,
    },
  },
};

// Page transition animations
export const pageTransition = {
  initial: {
    opacity: 0,
    x: 20,
  },
  animate: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.4,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    x: -20,
    transition: {
      duration: 0.3,
      ease: easings.easeIn,
    },
  },
};

// Modal/Dialog animations
export const modalBackdrop = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

export const modalContent = {
  initial: {
    opacity: 0,
    scale: 0.95,
    y: 20,
  },
  animate: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: easings.easeOut,
    },
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: {
      duration: 0.2,
      ease: easings.easeIn,
    },
  },
};

// Celebration animation for achievements
export const celebration = {
  animate: {
    scale: [1, 1.2, 1],
    rotate: [0, 5, -5, 0],
    transition: {
      duration: 0.6,
      ease: "easeInOut",
    },
  },
};

// Utility function to create staggered animations
export const createStagger = (staggerDelay = 0.1, delayChildren = 0) => ({
  animate: {
    transition: {
      staggerChildren: staggerDelay,
      delayChildren,
    },
  },
});

// Utility function for reduced motion
export const respectsReducedMotion = (animation) => {
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return {
      initial: animation.animate || {},
      animate: animation.animate || {},
      exit: animation.animate || {},
    };
  }
  return animation;
};