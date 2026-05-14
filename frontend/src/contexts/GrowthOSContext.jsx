import React, { createContext, useContext, useState, useEffect } from 'react';
import growthOSClient from '../lib/growthOSClient';
import { useAuth } from './AuthContext';

const GrowthOSContext = createContext();

export const useGrowthOS = () => {
  const context = useContext(GrowthOSContext);
  if (!context) {
    throw new Error('useGrowthOS must be used within GrowthOSProvider');
  }
  return context;
};

export const GrowthOSProvider = ({ children }) => {
  const { user } = useAuth();
  const [dailyActions, setDailyActions] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [autonomousStatus, setAutonomousStatus] = useState(null);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch daily actions
  const fetchDailyActions = async () => {
    if (!user?.id) return;
    
    try {
      setLoading(true);
      const data = await growthOSClient.getDailyActions(user.id);
      setDailyActions(data.actions || []);
    } catch (err) {
      console.error('Failed to fetch daily actions:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Fetch autonomous status
  const fetchAutonomousStatus = async () => {
    if (!user?.id) return;
    
    try {
      const data = await growthOSClient.getAutonomousStatus(user.id);
      setAutonomousStatus(data);
    } catch (err) {
      console.error('Failed to fetch autonomous status:', err);
    }
  };

  // Launch campaign
  const launchCampaign = async (campaignData) => {
    try {
      setLoading(true);
      const result = await growthOSClient.launchCampaign({
        ...campaignData,
        business_id: user.id,
      });
      setCampaigns(prev => [...prev, result.campaign]);
      return result;
    } catch (err) {
      console.error('Failed to launch campaign:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Enable autonomous mode
  const enableAutonomous = async (config) => {
    try {
      setLoading(true);
      const result = await growthOSClient.enableAutonomous({
        ...config,
        business_id: user.id,
      });
      setAutonomousStatus(result);
      return result;
    } catch (err) {
      console.error('Failed to enable autonomous mode:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Disable autonomous mode
  const disableAutonomous = async () => {
    try {
      setLoading(true);
      await growthOSClient.disableAutonomous(user.id);
      setAutonomousStatus({ enabled: false });
    } catch (err) {
      console.error('Failed to disable autonomous mode:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Generate viral content
  const generateViralContent = async (data) => {
    try {
      setLoading(true);
      const result = await growthOSClient.generateViralContent(data);
      return result;
    } catch (err) {
      console.error('Failed to generate viral content:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Analyze website
  const analyzeWebsite = async (data) => {
    try {
      setLoading(true);
      const result = await growthOSClient.analyzeWebsite(data);
      return result;
    } catch (err) {
      console.error('Failed to analyze website:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Predict revenue
  const predictRevenue = async (data) => {
    try {
      setLoading(true);
      const result = await growthOSClient.predictRevenue(data);
      return result;
    } catch (err) {
      console.error('Failed to predict revenue:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Initialize data on mount
  useEffect(() => {
    if (user?.id) {
      fetchDailyActions();
      fetchAutonomousStatus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  const value = {
    dailyActions,
    campaigns,
    autonomousStatus,
    competitors,
    loading,
    error,
    fetchDailyActions,
    fetchAutonomousStatus,
    launchCampaign,
    enableAutonomous,
    disableAutonomous,
    generateViralContent,
    analyzeWebsite,
    predictRevenue,
  };

  return (
    <GrowthOSContext.Provider value={value}>
      {children}
    </GrowthOSContext.Provider>
  );
};
