/*
Settings Page - Linear-Level Design
*/

import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LinearLayout from '../components/LinearLayout';
import { User, Bell, Shield, CreditCard, Zap, Save } from 'lucide-react';
import { toast } from 'sonner';

export default function SettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState({
    name: user?.name || '',
    email: user?.email || '',
    company: '',
    website: '',
  });

  const handleSave = async () => {
    setSaving(true);
    toast.loading('Saving changes...');
    
    setTimeout(() => {
      setSaving(false);
      toast.success('Settings saved successfully!');
    }, 1500);
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'billing', name: 'Billing', icon: CreditCard },
  ];

  return (
    <LinearLayout 
      title="Settings" 
      subtitle="Manage your account and preferences"
    >
      <div className="grid grid-cols-4 gap-6">
        {/* Sidebar Tabs */}
        <div className="space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-white/10 text-white'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.name}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="col-span-3 space-y-6">
          {activeTab === 'profile' && (
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-1">Profile Information</h2>
                <p className="text-sm text-white/50">Update your personal details</p>
              </div>

              <div className="space-y-4 max-w-xl">
                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={profile.company}
                    onChange={(e) => setProfile({ ...profile, company: e.target.value })}
                    placeholder="Your company"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    Website
                  </label>
                  <input
                    type="url"
                    value={profile.website}
                    onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-6 py-3 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  <Save className="w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-1">Notification Preferences</h2>
                <p className="text-sm text-white/50">Manage how you receive updates</p>
              </div>

              <div className="space-y-4 max-w-xl">
                {[
                  { label: 'Email Notifications', description: 'Receive updates via email' },
                  { label: 'Campaign Alerts', description: 'Get notified about campaign performance' },
                  { label: 'AI Insights', description: 'Receive AI-generated recommendations' },
                  { label: 'Weekly Reports', description: 'Get weekly performance summaries' },
                ].map((item) => (
                  <div key={item.label} className="flex items-center justify-between p-4 rounded-lg bg-white/[0.02] border border-white/5">
                    <div>
                      <p className="font-medium">{item.label}</p>
                      <p className="text-sm text-white/50">{item.description}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-violet-500"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-1">Security Settings</h2>
                <p className="text-sm text-white/50">Manage your account security</p>
              </div>

              <div className="space-y-4 max-w-xl">
                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    Current Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    New Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-white/70">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    placeholder="••••••••"
                    className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 focus:border-white/20 outline-none transition-all"
                  />
                </div>

                <button
                  onClick={() => toast.success('Password updated successfully!')}
                  className="px-6 py-3 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all"
                >
                  Update Password
                </button>
              </div>
            </div>
          )}

          {activeTab === 'billing' && (
            <div className="p-6 rounded-xl border border-white/5 bg-white/[0.02]">
              <div className="mb-6">
                <h2 className="text-lg font-semibold mb-1">Billing & Subscription</h2>
                <p className="text-sm text-white/50">Manage your plan and payment methods</p>
              </div>

              <div className="p-6 rounded-xl bg-gradient-to-br from-violet-500/10 to-purple-600/10 border border-violet-500/20 mb-6">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="w-5 h-5 text-violet-400" />
                      <span className="font-semibold">Free Plan</span>
                    </div>
                    <p className="text-sm text-white/60">
                      Upgrade to unlock unlimited campaigns and advanced features
                    </p>
                  </div>
                  <button
                    onClick={() => window.location.href = '/pricing'}
                    className="px-6 py-3 rounded-lg bg-white text-black font-medium hover:bg-white/90 transition-all"
                  >
                    Upgrade Now
                  </button>
                </div>
              </div>

              <div className="text-center py-12">
                <CreditCard className="w-12 h-12 text-white/20 mx-auto mb-4" />
                <p className="text-white/50">No payment methods added</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </LinearLayout>
  );
}
