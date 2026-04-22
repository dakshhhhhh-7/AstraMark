import * as React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { particleFloat } from "@/lib/animations";

/**
 * ParticleEffect - Floating particles for AI analysis visualization
 */
const ParticleEffect = ({ count = 20, className }) => {
  const particles = Array.from({ length: count }, (_, i) => ({
    id: i,
    size: Math.random() * 8 + 4,
    x: Math.random() * 100,
    y: Math.random() * 100,
    delay: Math.random() * 2,
    duration: Math.random() * 3 + 2,
  }));

  return (
    <div className={cn("absolute inset-0 overflow-hidden pointer-events-none", className)}>
      {particles.map((particle) => (
        <motion.div
          key={particle.id}
          className="absolute rounded-full bg-gradient-primary opacity-60 blur-sm"
          style={{
            width: particle.size,
            height: particle.size,
            left: `${particle.x}%`,
            top: `${particle.y}%`,
          }}
          animate={{
            y: [-20, 20, -20],
            x: [-10, 10, -10],
            opacity: [0.3, 0.8, 0.3],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: particle.duration,
            repeat: Infinity,
            delay: particle.delay,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

/**
 * AIAnalysisEffect - Animated effect for AI processing visualization
 */
const AIAnalysisEffect = ({ className }) => {
  return (
    <div className={cn("relative w-full h-64 flex items-center justify-center", className)}>
      {/* Particle background */}
      <ParticleEffect count={30} />
      
      {/* Central glow */}
      <motion.div
        className="absolute w-32 h-32 rounded-full bg-gradient-primary opacity-30 blur-3xl"
        animate={{
          scale: [1, 1.5, 1],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      
      {/* Rotating rings */}
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="absolute border-2 border-primary/30 rounded-full"
          style={{
            width: 80 + i * 40,
            height: 80 + i * 40,
          }}
          animate={{
            rotate: 360,
            scale: [1, 1.1, 1],
          }}
          transition={{
            rotate: {
              duration: 3 + i,
              repeat: Infinity,
              ease: "linear",
            },
            scale: {
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3,
            },
          }}
        />
      ))}
      
      {/* Center icon/text */}
      <motion.div
        className="relative z-10 text-center"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
      >
        <div className="text-4xl font-bold gradient-text">AI</div>
        <motion.div
          className="text-sm text-muted-foreground mt-2"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Analyzing...
        </motion.div>
      </motion.div>
    </div>
  );
};

export { ParticleEffect, AIAnalysisEffect };
