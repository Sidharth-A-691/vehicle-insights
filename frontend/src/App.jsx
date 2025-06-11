import React, { useState, useEffect, useRef } from 'react';
import {
  Search, RefreshCw, ChevronDown, ChevronUp, Car, FileText, DollarSign, History, AlertTriangle, Settings, Activity,
  ShieldCheck, Zap, Lightbulb, TrendingUp, Cpu, Award, CheckCircle2, Sparkles, Info,
  UserCircle, LogOut, Power, Users, Shield, BarChart, CreditCard, Gavel
} from 'lucide-react';
import { get } from './apiClient';

// Navbar Component (unchanged)
const Navbar = ({ healthStatus }) => {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const profileRef = useRef(null);
  const navbarRef = useRef(null);

  const handleLogoClick = () => {
    const navElement = document.querySelector('nav');
    const currentNavbarHeight = navElement ? navElement.offsetHeight : 64;
    scrollToElement('search-section-top', currentNavbarHeight);
  };

  const toggleProfileDropdown = () => {
    setIsProfileOpen(!isProfileOpen);
  };

  const handleLogout = () => {
    console.log("User logged out");
    setIsProfileOpen(false);
    // Add actual logout logic here
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const getApiStatusIndicator = () => {
    if (healthStatus === 'healthy') return <span className="w-2 h-2 bg-emerald-500 rounded-full inline-block mr-2"></span>;
    if (healthStatus === 'unhealthy') return <span className="w-2 h-2 bg-rose-500 rounded-full inline-block mr-2"></span>;
    return <span className="w-2 h-2 bg-amber-500 rounded-full inline-block mr-2 animate-pulse"></span>;
  };

  return (
    <nav ref={navbarRef} className="bg-slate-800 shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center cursor-pointer" onClick={handleLogoClick}>
            <img src="/ust_logo.png" alt="UST Logo" width={30} height={30} />
            <span className="ml-3 font-semibold text-xl text-slate-200">VehicleIntel</span>
          </div>
          <div className="relative" ref={profileRef}>
            <button
              onClick={toggleProfileDropdown}
              className="p-2 rounded-full text-slate-300 hover:text-white hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 focus:ring-white"
            >
              <UserCircle size={26} />
            </button>
            {isProfileOpen && (
              <div className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none py-1">
                <div className="px-4 py-2 text-sm text-slate-700 border-b border-slate-200">
                  <p className="font-medium">Dummy User</p>
                  <p className="text-xs text-slate-500">dummy.user@example.com</p>
                </div>
                <div className="px-4 py-2 text-sm text-slate-700 flex items-center">
                  {getApiStatusIndicator()}
                  API: <span className="font-medium ml-1">{healthStatus ? healthStatus.charAt(0).toUpperCase() + healthStatus.slice(1) : 'Checking...'}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full text-left block px-4 py-2 text-sm text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                >
                  <LogOut size={16} className="inline mr-2 -mt-0.5" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

const scrollToElement = (elementId, navbarHeight = 64) => {
  const element = document.getElementById(elementId);
  if (element) {
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
    const offsetPosition = elementPosition - navbarHeight - 16;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });
  }
};

const App = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('vin');
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);

  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    valuations: true,
    history: true,
    recalls: true,
    specifications: true,
    cost_insights: true,
    ownership_history: true,
    theft_records: true,
    insurance_claims: true,
    mileage_records: true,
    finance_records: true,
    auction_records: true,
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await get('/health');
        setHealthStatus(health.status);
      } catch (err) {
        setHealthStatus('unhealthy');
        console.error("Health check error:", err.detail || 'Unknown error');
      }
    };
    checkHealth();
  }, []);

  useEffect(() => {
    if (selectedVehicle) {
      const navElement = document.querySelector('nav');
      const currentNavbarHeight = navElement ? navElement.offsetHeight : 64;
      const timer = setTimeout(() => {
        scrollToElement('vehicle-card-header', currentNavbarHeight);
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [selectedVehicle]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    setSelectedVehicle(null);

    const navElement = document.querySelector('nav');
    const currentNavbarHeight = navElement ? navElement.offsetHeight : 64;

    setTimeout(() => {
      scrollToElement('results-area', currentNavbarHeight);
    }, 100);

    try {
      const endpointPath = searchType === 'vin'
        ? `/vehicle/vin/${searchQuery.trim().toUpperCase()}`
        : `/vehicle/vrm/${searchQuery.trim().replace(/\s/g, '').toUpperCase()}`;
      
      const vehicle = await get(endpointPath);
      setSelectedVehicle(vehicle);
      setExpandedSections({ // Reset expanded sections on new search
        basic: true,
        valuations: true,
        history: true,
        recalls: true,
        specifications: true,
        cost_insights: true,
        ownership_history: true,
        theft_records: true,
        insurance_claims: true,
        mileage_records: true,
        finance_records: true,
        auction_records: true,
      });
    } catch (err) {
      setError(err.detail || 'Failed to fetch vehicle data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshInsights = async (vehicleId) => {
    if (!selectedVehicle) return;
    setLoading(true);
    setError(null);
    try {
      await get(`/vehicle/${vehicleId}/refresh-insights`);
      const endpointPath = selectedVehicle.search_type === 'vin'
        ? `/vehicle/vin/${selectedVehicle.search_term}`
        : `/vehicle/vrm/${selectedVehicle.search_term}`;
      
      const updatedVehicle = await get(endpointPath);
      setSelectedVehicle(updatedVehicle); 
    } catch (err) {
      setError(err.detail || 'Failed to refresh insights');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => {
      const newState = !prev[section];
      return { ...prev, [section]: newState };
    });
  };

  const formatCurrency = (value) => {
    return value != null ? `£${Number(value).toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : 'N/A';
  };

  const getReliabilityScoreColor = (score) => {
    if (score == null || isNaN(Number(score))) return 'text-slate-500';
    const numericScore = Number(score);
    if (numericScore >= 7) return 'text-emerald-600';
    if (numericScore >= 4) return 'text-amber-600';
    return 'text-rose-600';
  };

  const renderVehicleDetails = (vehicle) => {
    if (!vehicle || !vehicle.detailed_data || !vehicle.ai_insights) {
      return <p className="text-center text-red-600">Incomplete vehicle data received.</p>;
    }
    const { detailed_data, ai_insights } = vehicle;
    const { basic, valuations, history, recalls, specifications, ownership_history, theft_records, insurance_claims, mileage_records, finance_records, auction_records } = detailed_data;

    if (!basic) {
      return <p className="text-center text-red-600">Basic vehicle information is missing.</p>;
    }

    const keyInsightsFirstHalf = ai_insights.key_insights ? ai_insights.key_insights.slice(0, Math.ceil(ai_insights.key_insights.length / 2)) : [];
    const keyInsightsSecondHalf = ai_insights.key_insights ? ai_insights.key_insights.slice(Math.ceil(ai_insights.key_insights.length / 2)) : [];

    return (
      <div className="space-y-6">
        {/* Vehicle Card Header */}
        <div id="vehicle-card-header" className="bg-gradient-to-br from-slate-700 to-slate-800 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center gap-4 mb-4">
            <Car size={40} className="text-sky-300" />
            <div>
              <h2 className="text-2xl font-bold">{basic.make || 'N/A'} {basic.model || 'N/A'}</h2>
              <p className="text-slate-300 text-md">{basic.variant || 'N/A'} • {basic.year || 'N/A'}</p>
            </div>
          </div>
          <div className="flex flex-wrap md:flex-nowrap -mx-1.5 mt-5 gap-y-3 md:gap-x-1">
            <div className="bg-slate-600/50 rounded-lg p-3 px-1.5 w-1/2 md:w-1/4 mx-1.5 md:mx-0">
              <p className="text-slate-300 text-xs">VIN</p>
              <p className="font-semibold text-sm">{basic.vin || 'N/A'}</p>
            </div>
            <div className="bg-slate-600/50 rounded-lg p-3 px-1.5 w-1/2 md:w-1/4 mx-1.5 md:mx-0">
              <p className="text-slate-300 text-xs">VRM</p>
              <p className="font-semibold text-sm">{basic.vrm || 'N/A'}</p>
            </div>
            <div className="bg-slate-600/50 rounded-lg p-3 px-1.5 w-1/2 md:w-1/4 mx-1.5 md:mx-0">
              <p className="text-slate-300 text-xs">Status</p>
              <p className="font-semibold text-sm">{basic.vehicle_status || 'N/A'}</p>
            </div>
            <div className="bg-slate-600/50 rounded-lg p-3 px-1.5 w-1/2 md:w-1/4 mx-1.5 md:mx-0">
              <p className="text-slate-300 text-xs">Fuel Type</p>
              <p className="font-semibold text-sm">{basic.fuel_type || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* AI-Powered Insights (Full Width) */}
        <div className="bg-white rounded-xl shadow-xl border border-slate-200">
          <div className="p-4 sm:p-6 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sparkles className="text-sky-500" size={24} />
              <h3 className="text-xl font-semibold text-slate-800">AI-Powered Insights</h3>
            </div>
            <button
              onClick={() => handleRefreshInsights(vehicle.vehicle_id)}
              disabled={loading}
              className="p-2 text-slate-500 hover:text-sky-600 hover:bg-sky-100 rounded-md transition-colors disabled:opacity-50"
              title="Refresh AI Insights"
            >
              <RefreshCw size={18} className={loading && selectedVehicle ? 'animate-spin' : ''} />
            </button>
          </div>
          <div className="p-4 sm:p-6 space-y-6">
            <div className="p-4 bg-sky-50 border-l-4 border-sky-400 rounded-r-md">
              <div className="flex items-start">
                <Info size={20} className="mr-3 text-sky-500 flex-shrink-0 mt-0.5" />
                <p className="text-slate-700 leading-relaxed text-sm">
                  {ai_insights.summary || 'AI summary is currently unavailable.'}
                </p>
              </div>
            </div>
            
            <div className="flex flex-col md:flex-row gap-4">
              <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 hover:shadow-md transition-shadow md:w-1/3">
                <div className="flex items-center mb-1.5">
                  <ShieldCheck size={18} className="mr-2 text-sky-600" />
                  <h4 className="font-semibold text-slate-800 text-sm">Reliability</h4>
                </div>
                <div className={`text-3xl font-bold mb-1 ${getReliabilityScoreColor(ai_insights.reliability_assessment?.score)}`}>
                  {ai_insights.reliability_assessment?.score || 'N/A'}
                  <span className="text-base font-normal text-slate-500">/10</span>
                </div>
                <p className="text-slate-600 text-sm leading-snug">{ai_insights.reliability_assessment?.explanation || 'No explanation provided.'}</p>
              </div>
              <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 hover:shadow-md transition-shadow md:w-1/3">
                <div className="flex items-center mb-1.5">
                  <TrendingUp size={18} className="mr-2 text-emerald-600" />
                  <h4 className="font-semibold text-slate-800 text-sm">Market Position</h4>
                </div>
                <p className="text-slate-700 font-medium text-base mt-1">{ai_insights.value_assessment?.current_market_position || 'N/A'}</p>
                <div className="mt-2">
                  <div className="bg-slate-100 border border-slate-200 rounded p-2 text-xs text-slate-600">
                    {ai_insights.value_assessment?.factors_affecting_value || 'No factors provided.'}
                  </div>
                </div>
              </div>
              {/* Owner Advice moved here */}
              <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 hover:shadow-md transition-shadow md:w-1/3">
                <div className="flex items-center mb-1.5">
                  <Award size={18} className="mr-2 text-sky-600" />
                  <h4 className="font-semibold text-slate-800 text-sm">Owner Advice</h4>
                </div>
                <p className="text-slate-600 text-sm leading-snug">{ai_insights.owner_advice || 'No specific owner advice available.'}</p>
              </div>
            </div>

            {/* Key Insights (Split Side-by-Side) */}
            <div className="pt-4 border-t border-slate-100">
              <div className="flex items-center mb-2">
                <Lightbulb size={20} className="mr-2 text-amber-500" />
                <h4 className="font-semibold text-slate-800 text-md">Key Insights</h4>
              </div>
              {ai_insights.key_insights && ai_insights.key_insights.length > 0 ? (
                <div className="flex flex-col md:flex-row md:gap-x-6">
                  <div className="md:w-1/2">
                    <ul className="space-y-2">
                      {keyInsightsFirstHalf.map((insight, index) => (
                        <li key={`ki1-${index}`} className="flex items-start text-slate-600 text-sm leading-relaxed">
                          <CheckCircle2 size={16} className="mr-2 mt-1 text-emerald-500 flex-shrink-0" />
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="md:w-1/2">
                    {keyInsightsSecondHalf.length > 0 && (
                      <ul className="space-y-2 mt-2 md:mt-0">
                        {keyInsightsSecondHalf.map((insight, index) => (
                          <li key={`ki2-${index}`} className="flex items-start text-slate-600 text-sm leading-relaxed">
                            <CheckCircle2 size={16} className="mr-2 mt-1 text-emerald-500 flex-shrink-0" />
                            <span>{insight}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              ) : <p className="text-slate-500 text-sm pl-8">No key insights available.</p>}
            </div>
            
            {ai_insights.attention_items && ai_insights.attention_items.length > 0 && (
              <div className="pt-4 border-t border-slate-100">
                <div className="flex items-center mb-3">
                  <AlertTriangle size={20} className="mr-2 text-rose-500" />
                  <h4 className="font-semibold text-slate-800 text-md">Items Requiring Attention</h4>
                </div>
                <div className="flex flex-wrap gap-2 pl-8">
                  {ai_insights.attention_items.map((item, index) => (
                    <span key={index} className="bg-rose-50 text-rose-700 px-3 py-1 rounded-full text-xs border border-rose-200 font-medium">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {ai_insights.cost_insights && (
              <div className="pt-4 border-t border-slate-100">
                <div className="flex items-center mb-2">
                  <DollarSign size={20} className="mr-2 text-emerald-600" />
                  <h4 className="font-semibold text-slate-800 text-md">Cost Insights</h4>
                </div>
                <div className="text-slate-600 text-sm leading-relaxed pl-8">
                  <p><strong>Maintenance:</strong> {ai_insights.cost_insights.typical_maintenance || 'N/A'}</p>
                  <p className="mt-2"><strong>Insurance:</strong> {ai_insights.cost_insights.insurance_notes || 'N/A'}</p>
                  <p className="mt-2"><strong>Fuel Efficiency:</strong> {ai_insights.cost_insights.fuel_efficiency || 'N/A'}</p>
                </div>
              </div>
            )}
            <div className="mt-5 pt-3 border-t border-slate-100">
              <p className="text-slate-500 text-xs text-right">
                Insights generated: {ai_insights.generated_at ? new Date(ai_insights.generated_at).toLocaleString() : 'N/A'}
                {ai_insights.cached && ' (Cached)'}
              </p>
            </div>
          </div>
        </div>

        {/* Basic Info & Valuations (Side-by-side on lg) */}
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="bg-white rounded-xl shadow-lg border border-slate-200 lg:w-1/2">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('basic')}
            >
              <div className="flex items-center gap-3">
                <FileText className="text-sky-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Basic Information</h3>
              </div>
              {expandedSections.basic ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.basic && (
              <div className="p-4 sm:p-5">
                <div className="flex flex-wrap -mx-1.5 text-sm">
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Make:</span><span className="ml-2 font-medium text-slate-700">{basic.make || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Model:</span><span className="ml-2 font-medium text-slate-700">{basic.model || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Year:</span><span className="ml-2 font-medium text-slate-700">{basic.year || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Body Type:</span><span className="ml-2 font-medium text-slate-700">{basic.body_type || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Fuel Type:</span><span className="ml-2 font-medium text-slate-700">{basic.fuel_type || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Transmission:</span><span className="ml-2 font-medium text-slate-700">{basic.transmission || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">MOT Status:</span><span className={`ml-2 font-medium ${basic.mot_status === 'Valid' ? 'text-emerald-600' : 'text-rose-600'}`}>{basic.mot_status || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">MOT Expiry:</span><span className="ml-2 font-medium text-slate-700">{basic.mot_expiry_date || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Tax Status:</span><span className={`ml-2 font-medium ${basic.tax_status === 'Taxed' ? 'text-emerald-600' : 'text-rose-600'}`}>{basic.tax_status || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Tax Due:</span><span className="ml-2 font-medium text-slate-700">{basic.tax_due_date || 'N/A'}</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Engine Size:</span><span className="ml-2 font-medium text-slate-700">{basic.engine_size || 'N/A'} L</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Power:</span><span className="ml-2 font-medium text-slate-700">{basic.engine_power_hp || 'N/A'} HP</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">CO2 Emissions:</span><span className="ml-2 font-medium text-slate-700">{basic.co2_emissions || 'N/A'} g/km</span></div>
                  <div className="w-full sm:w-1/2 px-1.5 pb-3"><span className="text-slate-500">Insurance Group:</span><span className="ml-2 font-medium text-slate-700">{basic.insurance_group || 'N/A'}</span></div>
                </div>
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl shadow-lg border border-slate-200 lg:w-1/2">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('valuations')}
            >
              <div className="flex items-center gap-3">
                <DollarSign className="text-emerald-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Valuations</h3>
              </div>
              {expandedSections.valuations ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.valuations && (
              <div className="p-4 sm:p-5">
                {valuations && valuations.length > 0 ? (
                  <div className="space-y-3">
                    {valuations.map((val, index) => (
                      <div key={index} className="border border-slate-200 rounded-lg p-3 bg-slate-50/50">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-medium text-slate-800 text-sm">{val.valuation_date || 'N/A'}</span>
                          <span className="text-xs text-slate-500">{val.condition_grade || 'N/A'}</span>
                        </div>
                        <div className="flex flex-wrap -mx-2 text-sm">
                          <div className="w-1/2 px-2 pb-2"><span className="text-slate-500">Retail:</span><span className="ml-2 font-medium text-slate-700">{formatCurrency(val.retail_value)}</span></div>
                          <div className="w-1/2 px-2 pb-2"><span className="text-slate-500">Trade:</span><span className="ml-2 font-medium text-slate-700">{formatCurrency(val.trade_value)}</span></div>
                          <div className="w-1/2 px-2 pb-2"><span className="text-slate-500">Private:</span><span className="ml-2 font-medium text-slate-700">{formatCurrency(val.private_value)}</span></div>
                          <div className="w-1/2 px-2 pb-2"><span className="text-slate-500">Auction:</span><span className="ml-2 font-medium text-slate-700">{formatCurrency(val.auction_value)}</span></div>
                        </div>
                        <div className="mt-1.5 text-xs text-slate-500">
                          Mileage: {val.mileage_at_valuation?.toLocaleString() || 'N/A'} • Source: {val.valuation_source || 'N/A'} • Confidence: {(val.confidence_score * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-4 text-sm">No valuation data available</p>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Grid for History and Recalls */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* History Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('history')}
            >
              <div className="flex items-center gap-3">
                <History className="text-sky-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">History</h3>
              </div>
              {expandedSections.history ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.history && (
              <div className="p-4 sm:p-5">
                {history && history.length > 0 ? (
                  <div className="space-y-3">
                    {history.map((record, index) => (
                      <div key={index} className="border-l-4 border-sky-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <div>
                            <span className="font-medium text-slate-800 text-sm">{record.event_type || 'N/A'}</span>
                            <span className="ml-2 text-slate-400 text-xs">•</span>
                            <span className="ml-2 text-slate-600 text-sm">{record.event_date || 'N/A'}</span>
                          </div>
                          {record.pass_fail && (
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${record.pass_fail === 'PASS' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                              {record.pass_fail}
                            </span>
                          )}
                        </div>
                        <p className="text-slate-600 text-sm">{record.event_description || 'No description.'}</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Mileage: {record.mileage?.toLocaleString() || 'N/A'} • Location: {record.location || 'N/A'}
                          {record.cost && ` • Cost: ${formatCurrency(record.cost)}`}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-4 text-sm">No history records available</p>
                )}
              </div>
            )}
          </div>

          {/* Recalls Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('recalls')}
            >
              <div className="flex items-center gap-3">
                <AlertTriangle className="text-amber-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Recalls</h3>
              </div>
              {expandedSections.recalls ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.recalls && (
              <div className="p-4 sm:p-5">
                {recalls && recalls.length > 0 ? (
                  <div className="space-y-3">
                    {recalls.map((recall, index) => (
                      <div key={index} className="border border-amber-300 rounded-lg p-3 bg-amber-50">
                        <div className="flex justify-between items-start mb-1">
                          <h4 className="font-medium text-slate-800 text-sm">{recall.recall_title || 'N/A'}</h4>
                          <span className="text-xs text-slate-500">{recall.recall_date || 'N/A'}</span>
                        </div>
                        <p className="text-slate-600 text-sm mb-1.5">{recall.recall_description || 'No description.'}</p>
                        <div className="flex justify-between items-center">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${recall.recall_status === 'Complete' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                            {recall.recall_status || 'N/A'}
                          </span>
                          <span className="text-xs text-slate-500">Campaign: {recall.manufacturer_campaign || 'N/A'}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <ShieldCheck className="mx-auto text-emerald-500 mb-2" size={28} /> 
                    <p className="text-emerald-700 font-medium text-sm">No recalls found</p>
                    <p className="text-slate-500 text-xs">This vehicle appears to have no outstanding recalls.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Specifications Card (Full Width) */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200">
          <div
            className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
            onClick={() => toggleSection('specifications')}
          >
            <div className="flex items-center gap-3">
              <Settings className="text-slate-600" size={20} />
              <h3 className="text-md font-semibold text-slate-800">Specifications</h3>
            </div>
            {expandedSections.specifications ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
          </div>
          {expandedSections.specifications && (
            <div className="p-4 sm:p-5">
              {specifications ? (
                <div className="flex flex-wrap -mx-3"> {/* Use flex-wrap for responsiveness */}
                  <div className="w-full md:w-1/2 lg:w-1/4 px-3 pb-4">
                    <h4 className="font-medium text-slate-800 mb-2 text-sm">Dimensions</h4>
                    <div className="space-y-1.5 text-xs text-slate-600">
                      <div><span className="text-slate-500">Length:</span><span className="ml-2">{specifications.length_mm || 'N/A'} mm</span></div>
                      <div><span className="text-slate-500">Width:</span><span className="ml-2">{specifications.width_mm || 'N/A'} mm</span></div>
                      <div><span className="text-slate-500">Height:</span><span className="ml-2">{specifications.height_mm || 'N/A'} mm</span></div>
                      <div><span className="text-slate-500">Wheelbase:</span><span className="ml-2">{specifications.wheelbase_mm || 'N/A'} mm</span></div>
                    </div>
                  </div>
                  <div className="w-full md:w-1/2 lg:w-1/4 px-3 pb-4">
                    <h4 className="font-medium text-slate-800 mb-2 text-sm">Performance</h4>
                    <div className="space-y-1.5 text-xs text-slate-600">
                      <div><span className="text-slate-500">Top Speed:</span><span className="ml-2">{specifications.top_speed_mph || 'N/A'} mph</span></div>
                      <div><span className="text-slate-500">0-60 mph:</span><span className="ml-2">{specifications.acceleration_0_60_mph || 'N/A'} s</span></div>
                      <div><span className="text-slate-500">Drive Type:</span><span className="ml-2">{specifications.drive_type || 'N/A'}</span></div>
                      <div><span className="text-slate-500">Max Towing:</span><span className="ml-2">{specifications.max_towing_weight_kg || 'N/A'} kg</span></div>
                    </div>
                  </div>
                  <div className="w-full md:w-1/2 lg:w-1/4 px-3 pb-4">
                    <h4 className="font-medium text-slate-800 mb-2 text-sm">Capacity</h4>
                    <div className="space-y-1.5 text-xs text-slate-600">
                      <div><span className="text-slate-500">Fuel Tank:</span><span className="ml-2">{specifications.fuel_tank_capacity || 'N/A'} L</span></div>
                      <div><span className="text-slate-500">Boot:</span><span className="ml-2">{specifications.boot_capacity_litres || 'N/A'} L</span></div>
                      <div><span className="text-slate-500">Kerb Weight:</span><span className="ml-2">{specifications.kerb_weight_kg || 'N/A'} kg</span></div>
                      <div><span className="text-slate-500">Gross Weight:</span><span className="ml-2">{specifications.gross_weight_kg || 'N/A'} kg</span></div>
                    </div>
                  </div>
                  <div className="w-full md:w-1/2 lg:w-1/4 px-3 pb-4">
                    <h4 className="font-medium text-slate-800 mb-2 text-sm">Safety & Systems</h4>
                    <div className="space-y-1.5 text-xs text-slate-600">
                      <div><span className="text-slate-500">Airbags:</span><span className="ml-2">{specifications.airbags || 'N/A'}</span></div>
                      <div><span className="text-slate-500">ABS:</span><span className="ml-2">{specifications.abs ? 'Yes' : 'No'}</span></div>
                      <div><span className="text-slate-500">ESP:</span><span className="ml-2">{specifications.esp ? 'Yes' : 'No'}</span></div>
                      <div><span className="text-slate-500">Steering:</span><span className="ml-2">{specifications.steering_type || 'N/A'}</span></div>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-slate-500 text-center py-4 text-sm">No specification data available</p>
              )}
            </div>
          )}
        </div>

        {/* Grid for remaining data cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Ownership History Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('ownership_history')}
            >
              <div className="flex items-center gap-3">
                <Users className="text-sky-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Ownership History</h3>
              </div>
              {expandedSections.ownership_history ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.ownership_history && (
              <div className="p-4 sm:p-5">
                {ownership_history && ownership_history.length > 0 ? (
                  <div className="space-y-3">
                    {ownership_history.map((record, index) => (
                      <div key={index} className="border-l-4 border-sky-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium text-slate-800 text-sm">{record.change_type || 'N/A'}</span>
                          <span className="text-xs text-slate-500">{record.change_date || 'N/A'}</span>
                        </div>
                        <p className="text-slate-600 text-sm">From: {record.previous_owner_type || 'N/A'} ({record.previous_owner_postcode || 'N/A'})</p>
                        <p className="text-slate-600 text-sm">To: {record.new_owner_type || 'N/A'} ({record.new_owner_postcode || 'N/A'})</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Mileage: {record.mileage_at_change?.toLocaleString() || 'N/A'} • Source: {record.source || 'N/A'}
                          {record.sale_price && ` • Sale Price: ${formatCurrency(record.sale_price)}`}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-4 text-sm">No ownership history available</p>
                )}
              </div>
            )}
          </div>

          {/* Theft Records Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('theft_records')}
            >
              <div className="flex items-center gap-3">
                <Shield className="text-rose-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Theft Records</h3>
              </div>
              {expandedSections.theft_records ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.theft_records && (
              <div className="p-4 sm:p-5">
                {theft_records && theft_records.length > 0 ? (
                  <div className="space-y-3">
                    {theft_records.map((record, index) => (
                      <div key={index} className="border-l-4 border-rose-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium text-slate-800 text-sm">Theft Reported</span>
                          <span className="text-xs text-slate-500">{record.theft_date || 'N/A'}</span>
                        </div>
                        <p className="text-slate-600 text-sm">Recovered: {record.recovery_date || 'Not recovered'}</p>
                        <p className="text-slate-600 text-sm">Circumstances: {record.theft_circumstances || 'N/A'}</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Theft Location: {record.theft_location_postcode || 'N/A'} • Recovery Location: {record.recovery_location_postcode || 'N/A'}
                          <br />
                          Condition: {record.recovery_condition || 'N/A'} • Status: {record.current_status || 'N/A'}
                          <br />
                          Police Ref: {record.police_reference || 'N/A'} • Insurance Claim Ref: {record.insurance_claim_reference || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <ShieldCheck className="mx-auto text-emerald-500 mb-2" size={28} />
                    <p className="text-emerald-700 font-medium text-sm">No theft records found</p>
                    <p className="text-slate-500 text-xs">This vehicle has no reported theft incidents.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Insurance Claims Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('insurance_claims')}
            >
              <div className="flex items-center gap-3">
                <Shield className="text-amber-600" size={20} /> {/* Icon changed from Zap to Shield for consistency, or keep Zap if distinct meaning */}
                <h3 className="text-md font-semibold text-slate-800">Insurance Claims</h3>
              </div>
              {expandedSections.insurance_claims ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.insurance_claims && (
              <div className="p-4 sm:p-5">
                {insurance_claims && insurance_claims.length > 0 ? (
                  <div className="space-y-3">
                    {insurance_claims.map((claim, index) => (
                      <div key={index} className="border-l-4 border-amber-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium text-slate-800 text-sm">{claim.claim_type || 'N/A'}</span>
                          <span className="text-xs text-slate-500">{claim.claim_date || 'N/A'}</span>
                        </div>
                        <p className="text-slate-600 text-sm">{claim.description || 'No description.'}</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Claim Amount: {formatCurrency(claim.claim_amount)} • Settlement: {formatCurrency(claim.settlement_amount)}
                          <br />
                          Mileage: {claim.mileage_at_incident?.toLocaleString() || 'N/A'} • Location: {claim.incident_location_postcode || 'N/A'}
                          <br />
                          Fault: {claim.fault_claim ? 'Yes' : 'No'} • Total Loss: {claim.total_loss ? 'Yes' : 'No'} • Insurer: {claim.insurer || 'N/A'}
                          <br />
                          Reference: {claim.claim_reference || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <ShieldCheck className="mx-auto text-emerald-500 mb-2" size={28} />
                    <p className="text-emerald-700 font-medium text-sm">No insurance claims found</p>
                    <p className="text-slate-500 text-xs">This vehicle has no reported insurance claims.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Mileage Records Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('mileage_records')}
            >
              <div className="flex items-center gap-3">
                <BarChart className="text-sky-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Mileage Records</h3>
              </div>
              {expandedSections.mileage_records ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.mileage_records && (
              <div className="p-4 sm:p-5">
                {mileage_records && mileage_records.length > 0 ? (
                  <div className="space-y-3">
                    {mileage_records.map((record, index) => (
                      <div key={index} className="border-l-4 border-sky-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium text-slate-800 text-sm">{record.reading_date || 'N/A'}</span>
                          <span className={`text-xs font-medium ${record.discrepancy_flag ? 'text-rose-600' : 'text-emerald-600'}`}>
                            {record.discrepancy_flag ? 'Discrepancy' : 'Verified'}
                          </span>
                        </div>
                        <p className="text-slate-600 text-sm">Mileage: {record.mileage?.toLocaleString() || 'N/A'}</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Source: {record.source || 'N/A'} • Previous: {record.previous_mileage?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-4 text-sm">No mileage records available</p>
                )}
              </div>
            )}
          </div>

          {/* Finance Records Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('finance_records')}
            >
              <div className="flex items-center gap-3">
                <CreditCard className="text-amber-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Finance Records</h3>
              </div>
              {expandedSections.finance_records ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.finance_records && (
              <div className="p-4 sm:p-5">
                {finance_records && finance_records.length > 0 ? (
                  <div className="space-y-3">
                    {finance_records.map((record, index) => (
                      <div key={index} className="border-l-4 border-amber-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium text-slate-800 text-sm">{record.finance_type || 'N/A'}</span>
                          <span className="text-xs text-slate-500">{record.finance_start_date || 'N/A'}</span>
                        </div>
                        <p className="text-slate-600 text-sm">Company: {record.finance_company || 'N/A'}</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Start: {record.finance_start_date || 'N/A'} • End: {record.finance_end_date || 'N/A'}
                          <br />
                          Monthly Payment: {formatCurrency(record.monthly_payment)} • Settlement: {formatCurrency(record.settlement_figure)}
                          <br />
                          Outstanding: {record.outstanding_finance ? 'Yes' : 'No'} • Settlement Date: {record.settlement_date || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <ShieldCheck className="mx-auto text-emerald-500 mb-2" size={28} />
                    <p className="text-emerald-700 font-medium text-sm">No finance records found</p>
                    <p className="text-slate-500 text-xs">This vehicle has no reported finance agreements.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Auction Records Card */}
          <div className="bg-white rounded-xl shadow-lg border border-slate-200">
            <div
              className="p-4 sm:p-5 border-b border-slate-200 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
              onClick={() => toggleSection('auction_records')}
            >
              <div className="flex items-center gap-3">
                <Gavel className="text-sky-600" size={20} />
                <h3 className="text-md font-semibold text-slate-800">Auction Records</h3>
              </div>
              {expandedSections.auction_records ? <ChevronUp size={20} className="text-slate-500" /> : <ChevronDown size={20} className="text-slate-500" />}
            </div>
            {expandedSections.auction_records && (
              <div className="p-4 sm:p-5">
                {auction_records && auction_records.length > 0 ? (
                  <div className="space-y-3">
                    {auction_records.map((record, index) => (
                      <div key={index} className="border-l-4 border-sky-300 pl-3 py-1.5">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium text-slate-800 text-sm">{record.auction_house || 'N/A'}</span>
                          <span className="text-xs text-slate-500">{record.auction_date || 'N/A'}</span>
                        </div>
                        <p className="text-slate-600 text-sm">Lot: {record.lot_number || 'N/A'} • Condition: {record.condition_grade || 'N/A'}</p>
                        <div className="mt-1 text-xs text-slate-500">
                          Hammer Price: {formatCurrency(record.hammer_price)} • Guide: {formatCurrency(record.guide_price_low)} - {formatCurrency(record.guide_price_high)}
                          <br />
                          Mileage: {record.mileage_at_auction?.toLocaleString() || 'N/A'} • Seller: {record.seller_type || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-500 text-center py-4 text-sm">No auction records available</p>
                )}
              </div>
            )}
          </div>
        </div> {/* End of grid for remaining data cards */}
      </div>
    );
  };
  

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar healthStatus={healthStatus} />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div id="search-section-top" className="grid md:grid-cols-12 gap-8 items-center mb-8 md:mb-12">
          <div className="md:col-span-5 lg:col-span-6">
            <h1 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-3">Vehicle Insights</h1>
            <p className="text-lg text-slate-600">
              Access detailed vehicle data and AI-driven analysis using VIN or VRM.
            </p>
          </div>
          <div className="md:col-span-7 lg:col-span-6">
            <div className="bg-white rounded-xl shadow-xl border border-slate-200 p-6 sm:p-8">
              <form onSubmit={handleSearch} className="space-y-5">
                <div className="flex justify-center">
                  <div className="bg-slate-100 rounded-lg p-1 flex">
                    <label className={`px-4 py-2 sm:px-5 rounded-md cursor-pointer transition-all font-medium text-sm sm:text-base ${
                      searchType === 'vin' 
                        ? 'bg-white text-sky-600 shadow-sm' 
                        : 'text-slate-600 hover:text-slate-800'
                    }`}>
                      <input type="radio" value="vin" checked={searchType === 'vin'} onChange={(e) => setSearchType(e.target.value)} className="sr-only" />
                      VIN Lookup
                    </label>
                    <label className={`px-4 py-2 sm:px-5 rounded-md cursor-pointer transition-all font-medium text-sm sm:text-base ${
                      searchType === 'vrn' 
                        ? 'bg-white text-sky-600 shadow-sm' 
                        : 'text-slate-600 hover:text-slate-800'
                    }`}>
                      <input type="radio" value="vrn" checked={searchType === 'vrn'} onChange={(e) => setSearchType(e.target.value)} className="sr-only" />
                      VRM Lookup
                    </label>
                  </div>
                </div>
                <div className="relative">
                  <input
                    type="text"
                    placeholder={searchType === 'vin' ? 'Enter 17-character VIN' : 'Enter Vehicle Registration'}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    disabled={loading}
                    className="w-full px-5 py-3 text-base border border-slate-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent disabled:opacity-60 disabled:cursor-not-allowed"
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                    <Search className="text-slate-400" size={20} />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading || !searchQuery.trim()}
                  className="w-full bg-gradient-to-r from-sky-500 to-cyan-500 text-white py-3 px-6 rounded-lg font-semibold text-base hover:from-sky-600 hover:to-cyan-600 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-150 ease-in-out flex items-center justify-center shadow-md hover:shadow-lg"
                >
                  {loading && !selectedVehicle ? (
                    <>
                      <RefreshCw className="animate-spin mr-2" size={18} /> Searching...
                    </>
                  ) : (
                    'Search Vehicle'
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
        <div id="results-area" className="mt-6 sm:mt-8">
          {loading && !selectedVehicle && (
            <div className="flex flex-col justify-center items-center py-10">
              <RefreshCw className="animate-spin text-sky-600" size={40} />
              <p className="mt-4 text-lg text-slate-700">Loading vehicle data...</p>
            </div>
          )}
          {error && !loading && (
            <div className="bg-rose-50 border-l-4 border-rose-500 text-rose-700 p-4 sm:p-5 rounded-md shadow-md max-w-2xl mx-auto">
              <div className="flex">
                <div className="py-1"><AlertTriangle className="h-5 w-5 text-rose-500 mr-3" /></div>
                <div>
                  <p className="font-bold text-sm">Error</p>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}
          {selectedVehicle && (
            renderVehicleDetails(selectedVehicle)
          )}
          {!loading && !error && !selectedVehicle && (
            <div className="text-center text-slate-500 py-10">
              <Car size={56} className="mx-auto mb-4 text-slate-400" />
              <p className="text-md">Enter a VIN or VRM to begin your search.</p>
              <p className="text-xs mt-2">Example VIN: SAMPLETESTVINURFY, Example VRM: AB05IYG</p>
            </div>
          )}
        </div>
      </div>
      <footer className="text-center py-6 border-t border-slate-200 mt-12">
        <p className="text-sm text-slate-500">© {new Date().getFullYear()} VehicleIntel. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;