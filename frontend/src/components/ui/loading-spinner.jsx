import * as React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { spin, pulse } from "@/lib/animations";

/**
 * LoadingSpinner - Premium loading indicator with multiple variants
 */
const LoadingSpinner = ({ size = "md", variant = "spin", className }) => {
  const sizes = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
    xl: "h-16 w-16",
  };

  if (variant === "pulse") {
    return (
      <motion.div
        className={cn(
          "rounded-full bg-gradient-primary",
          sizes[size],
          className
        )}
        {...pulse}
      />
    );
  }

  if (variant === "dots") {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="h-3 w-3 rounded-full bg-primary"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1,
              repeat: Infinity,
              delay: i * 0.2,
            }}
          />
        ))}
      </div>
    );
  }

  // Default: spin variant
  return (
    <motion.div
      className={cn(
        "border-4 border-primary/30 border-t-primary rounded-full",
        sizes[size],
        className
      )}
      {...spin}
    />
  );
};

/**
 * LoadingOverlay - Full-screen loading overlay with spinner
 */
const LoadingOverlay = ({ message = "Loading..." }) => {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="flex flex-col items-center gap-4">
        <LoadingSpinner size="xl" />
        {message && (
          <motion.p
            className="text-lg text-muted-foreground"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {message}
          </motion.p>
        )}
      </div>
    </motion.div>
  );
};

export { LoadingSpinner, LoadingOverlay };
