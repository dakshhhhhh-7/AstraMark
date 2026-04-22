import * as React from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import CountUp from "react-countup";
import { useInView } from "react-intersection-observer";
import { cn } from "@/lib/utils";
import {
  currencyCountUpConfig,
  percentageCountUpConfig,
  largeNumberCountUpConfig,
  animationTriggerConfig,
} from "@/lib/ui-config";

/**
 * AnimatedCounter - Animated number counter with intersection observer
 */
const AnimatedCounter = ({
  end,
  start = 0,
  duration = 2,
  prefix = "",
  suffix = "",
  decimals = 0,
  separator = ",",
  className,
  variant = "default",
}) => {
  const { ref, inView } = useInView(animationTriggerConfig.metrics);

  const configs = {
    currency: currencyCountUpConfig,
    percentage: percentageCountUpConfig,
    number: largeNumberCountUpConfig,
    default: { duration, decimals, separator, prefix, suffix },
  };

  const config = { ...configs[variant], start, end };

  return (
    <motion.div
      ref={ref}
      className={cn("font-bold", className)}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={inView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.5 }}
    >
      {inView && <CountUp {...config} />}
    </motion.div>
  );
};

/**
 * MetricCard - Premium card for displaying growth metrics
 */
const MetricCard = ({
  title,
  value,
  change,
  icon: Icon,
  variant = "default",
  className,
}) => {
  const { ref, inView } = useInView(animationTriggerConfig.card);

  const isPositive = change >= 0;
  const changeColor = isPositive ? "text-success" : "text-destructive";

  return (
    <motion.div
      ref={ref}
      className={cn(
        "glass-card rounded-2xl p-6 shadow-premium hover:shadow-glow transition-all duration-300",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="text-sm font-medium text-muted-foreground">{title}</div>
        {Icon && (
          <motion.div
            className="p-2 rounded-lg bg-primary/10"
            whileHover={{ scale: 1.1, rotate: 5 }}
          >
            <Icon className="h-5 w-5 text-primary" />
          </motion.div>
        )}
      </div>
      
      <div className="space-y-2">
        <AnimatedCounter
          end={value}
          variant={variant}
          className="text-3xl font-bold gradient-text"
        />
        
        {change !== undefined && (
          <motion.div
            className={cn("flex items-center gap-1 text-sm font-medium", changeColor)}
            initial={{ opacity: 0, x: -10 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ delay: 0.3 }}
          >
            <span>{isPositive ? "↑" : "↓"}</span>
            <span>{Math.abs(change)}%</span>
            <span className="text-muted-foreground">vs last week</span>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

/**
 * GrowthScore - Circular growth score display with animation
 */
const GrowthScore = ({ score, maxScore = 100, className }) => {
  const { ref, inView } = useInView(animationTriggerConfig.metrics);
  const percentage = (score / maxScore) * 100;

  return (
    <motion.div
      ref={ref}
      className={cn("relative inline-flex items-center justify-center", className)}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={inView ? { opacity: 1, scale: 1 } : {}}
      transition={{ duration: 0.5 }}
    >
      <svg width="200" height="200" className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx="100"
          cy="100"
          r="90"
          stroke="currentColor"
          strokeWidth="12"
          fill="none"
          className="text-muted"
        />
        {/* Progress circle */}
        <motion.circle
          cx="100"
          cy="100"
          r="90"
          stroke="url(#scoreGradient)"
          strokeWidth="12"
          fill="none"
          strokeLinecap="round"
          initial={{ strokeDashoffset: 565 }}
          animate={inView ? { strokeDashoffset: 565 - (565 * percentage) / 100 } : {}}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{
            strokeDasharray: 565,
          }}
        />
        <defs>
          <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#6366F1" />
            <stop offset="50%" stopColor="#A855F7" />
            <stop offset="100%" stopColor="#22D3EE" />
          </linearGradient>
        </defs>
      </svg>
      
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.div
          className="text-5xl font-bold gradient-text"
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 0.5 }}
        >
          {inView && <CountUp end={score} duration={1.5} />}
        </motion.div>
        <div className="text-sm text-muted-foreground mt-2">Growth Score</div>
      </div>
    </motion.div>
  );
};

export { AnimatedCounter, MetricCard, GrowthScore };
