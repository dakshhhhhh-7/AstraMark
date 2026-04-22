import * as React from "react";
import { motion } from "framer-motion";
import { Button } from "./button";
import { cn } from "@/lib/utils";
import { buttonHover, buttonTap } from "@/lib/animations";

/**
 * AnimatedButton - Premium button with micro-interactions
 * Includes hover scale, tap feedback, and optional loading state
 */
const AnimatedButton = React.forwardRef(
  ({ className, children, loading = false, disabled, ...props }, ref) => {
    return (
      <motion.div
        whileHover={!disabled && !loading ? buttonHover : {}}
        whileTap={!disabled && !loading ? buttonTap : {}}
        className="inline-block"
      >
        <Button
          ref={ref}
          className={cn(className)}
          disabled={disabled || loading}
          {...props}
        >
          {loading ? (
            <div className="flex items-center gap-2">
              <motion.div
                className="h-4 w-4 border-2 border-current border-t-transparent rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              />
              <span>Processing...</span>
            </div>
          ) : (
            children
          )}
        </Button>
      </motion.div>
    );
  }
);
AnimatedButton.displayName = "AnimatedButton";

export { AnimatedButton };
