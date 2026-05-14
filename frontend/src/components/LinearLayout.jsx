/*
Linear-Level Layout Component
Shared layout with sidebar and header for all authenticated pages
*/

import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  Sparkles, BarChart3, Target, Activity, Settings, 
  CreditCard, Rocket, Search, Zap, LogOut, BriefcaseIcon
} from 'lucide-react';

export default function LinearLayout({ children, title, subtitle, actions }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Overview', icon: BarChart3, path: '/astramark' },
    { name: 'Dashboard', icon: Activity, path: '/dashboard' },
    { name: 'AI Studio', icon: Sparkles, path: '/analysis' },
    { name: 'Business Analysis', icon: BriefcaseIcon, path: '/business-analysis' },
    { name: 'Campaigns', icon: Target, path: '/astramark' },
    { name: 'Automation', icon: Zap, path: '/astramark' },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-screen w-64 border-r border-white/5 bg-[#0A0A0A] flex flex-col z-50">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-white/5">
          <button onClick={() => navigate('/astramark')} className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="font-semibold text-lg">AstraMark</span>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navigation.map((item) => (
            <button
              key={item.name}
              onClick={() => navigate(item.path)}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                isActive(item.path)
                  ? 'bg-white/10 text-white' 
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.name}
            </button>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="p-3 border-t border-white/5 space-y-1">
          <button
            onClick={() => navigate('/settings')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive('/settings')
                ? 'bg-white/10 text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
          <button
            onClick={() => navigate('/pricing')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
              isActive('/pricing')
                ? 'bg-white/10 text-white'
                : 'text-white/60 hover:text-white hover:bg-white/5'
            }`}
          >
            <CreditCard className="w-4 h-4" />
            Billing
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 transition-all"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>

        {/* Upgrade card */}
        <div className="m-3 p-4 rounded-xl bg-gradient-to-br from-violet-500/10 to-purple-600/10 border border-violet-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Rocket className="w-4 h-4 text-violet-400" />
            <span className="text-sm font-semibold">Upgrade to Pro</span>
          </div>
          <p className="text-xs text-white/60 mb-3">
            Unlock unlimited campaigns and advanced AI features
          </p>
          <button 
            onClick={() => navigate('/pricing')}
            className="w-full py-2 px-3 rounded-lg bg-white text-black text-sm font-medium hover:bg-white/90 transition-all"
          >
            Upgrade Now
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-64 min-h-screen">
        {/* Header */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 sticky top-0 bg-[#0A0A0A]/80 backdrop-blur-xl z-40">
          <div>
            <h1 className="text-lg font-semibold">{title}</h1>
            {subtitle && <p className="text-sm text-white/50">{subtitle}</p>}
          </div>
          
          {actions && (
            <div className="flex items-center gap-3">
              {actions}
            </div>
          )}
        </header>

        {/* Content */}
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
