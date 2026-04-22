import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { useInView } from 'react-intersection-observer';
import CountUp from 'react-countup';
import { useUserStore, useDashboardStore } from '@/lib/store';
import { fadeInUp, countUp } from '@/lib/animations';
import { currencyCountUpConfig, percentageCountUpConfig } from '@/lib/ui-config';

// Test component to verify all dependencies are working
export const DependencyTest = () => {
  // Test Zustand store
  const { user, setUser } = useUserStore();
  const { metrics, setMetrics } = useDashboardStore();

  // Test React Query
  const { data, isLoading, error } = useQuery({
    queryKey: ['test'],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      return { message: 'React Query is working!' };
    },
  });

  // Test React Intersection Observer
  const { ref, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  // Test handlers
  const handleUpdateUser = () => {
    setUser({ name: 'Test User', email: 'test@example.com' });
  };

  const handleUpdateMetrics = () => {
    setMetrics({
      revenue: 125000,
      leads: 450,
      engagement: 85.5,
      growthScore: 92,
    });
  };

  return (
    <div className="p-8 space-y-8 bg-slate-900 text-white min-h-screen">
      <motion.div
        initial="initial"
        animate="animate"
        variants={fadeInUp}
        className="text-center"
      >
        <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          AstraMark Dependencies Test
        </h1>
        <p className="text-slate-300">
          Testing all installed dependencies for the $100M SaaS frontend
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Framer Motion Test */}
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="bg-slate-800 p-6 rounded-xl border border-slate-700"
        >
          <h3 className="text-xl font-semibold mb-2 text-indigo-400">
            Framer Motion ✅
          </h3>
          <p className="text-slate-300">
            Hover and click this card to see smooth animations in action.
          </p>
        </motion.div>

        {/* React Query Test */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-semibold mb-2 text-purple-400">
            React Query ✅
          </h3>
          {isLoading && <p className="text-yellow-400">Loading...</p>}
          {error && <p className="text-red-400">Error occurred</p>}
          {data && <p className="text-green-400">{data.message}</p>}
        </div>

        {/* Zustand Test */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-semibold mb-2 text-cyan-400">
            Zustand ✅
          </h3>
          <p className="text-slate-300 mb-2">
            User: {user?.name || 'Not set'}
          </p>
          <button
            onClick={handleUpdateUser}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors"
          >
            Update User
          </button>
        </div>

        {/* React CountUp Test */}
        <motion.div
          ref={ref}
          variants={countUp}
          initial="initial"
          animate={inView ? "animate" : "initial"}
          className="bg-slate-800 p-6 rounded-xl border border-slate-700"
        >
          <h3 className="text-xl font-semibold mb-2 text-emerald-400">
            React CountUp ✅
          </h3>
          <div className="space-y-2">
            <div>
              Revenue: <CountUp
                end={metrics.revenue || 125000}
                {...currencyCountUpConfig}
                className="text-emerald-400 font-bold"
              />
            </div>
            <div>
              Growth: <CountUp
                end={metrics.engagement || 85.5}
                {...percentageCountUpConfig}
                className="text-emerald-400 font-bold"
              />
            </div>
          </div>
        </motion.div>

        {/* React Intersection Observer Test */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-semibold mb-2 text-orange-400">
            Intersection Observer ✅
          </h3>
          <p className="text-slate-300">
            In view: {inView ? '👁️ Visible' : '🙈 Hidden'}
          </p>
          <p className="text-sm text-slate-400 mt-2">
            Scroll to see this component trigger animations
          </p>
        </div>

        {/* Combined Test */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h3 className="text-xl font-semibold mb-2 text-pink-400">
            All Systems ✅
          </h3>
          <button
            onClick={handleUpdateMetrics}
            className="px-4 py-2 bg-pink-600 hover:bg-pink-700 rounded-lg transition-colors mb-2"
          >
            Update Metrics
          </button>
          <p className="text-sm text-slate-400">
            Updates Zustand store and triggers CountUp animations
          </p>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="text-center p-6 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 rounded-xl border border-indigo-500/30"
      >
        <h2 className="text-2xl font-bold mb-2">🎉 All Dependencies Installed Successfully!</h2>
        <p className="text-slate-300">
          Ready to build the premium AstraMark $100M SaaS frontend experience
        </p>
      </motion.div>
    </div>
  );
};