import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, ChevronDown, ChevronUp, Car, FileText, DollarSign, History, AlertTriangle, Settings, Activity } from 'lucide-react';
import { get, post } from './apiClient'; // Assuming apiClient.js is in the same directory or adjust path

const App = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('vin'); // 'vin' or 'vrn'
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [healthStatus, setHealthStatus] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    aiInsights: true,
    valuations: false,
    history: false,
    recalls: false,
    specifications: false,
  });

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await get('/health'); // Use apiClient.get
        setHealthStatus(health.status);
      } catch (err) {
        // apiClient interceptor structures error as { status, detail }
        setHealthStatus('unhealthy');
        console.error("Health check error:", err.detail || 'Unknown error');
      }
    };
    checkHealth();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    setSelectedVehicle(null);

    try {
      const endpointPath = searchType === 'vin'
        ? `/vehicle/vin/${searchQuery.trim().toUpperCase()}`
        : `/vehicle/vrm/${searchQuery.trim().replace(/\s/g, '').toUpperCase()}`;
      
      const vehicle = await get(endpointPath); // Use apiClient.get
      setSelectedVehicle(vehicle);
    } catch (err) {
      // apiClient interceptor structures error as { status, detail }
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
      // Step 1: Call the refresh endpoint (Backend uses GET for this, so we use `get`)
      await get(`/vehicle/${vehicleId}/refresh-insights`); // Use apiClient.get

      // Step 2: Re-fetch the vehicle data to get updated insights
      const endpointPath = selectedVehicle.search_type === 'vin'
        ? `/vehicle/vin/${selectedVehicle.search_term}`
        : `/vehicle/vrm/${selectedVehicle.search_term}`;
      
      const updatedVehicle = await get(endpointPath); // Use apiClient.get
      setSelectedVehicle(updatedVehicle);

    } catch (err) {
      // apiClient interceptor structures error as { status, detail }
      setError(err.detail || 'Failed to refresh insights');
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const formatCurrency = (value) => {
    return value != null ? `£${Number(value).toLocaleString()}` : 'N/A';
  };

  const renderVehicleDetails = (vehicle) => {
    if (!vehicle || !vehicle.detailed_data || !vehicle.ai_insights) {
        return <p className="text-center text-red-500">Incomplete vehicle data received.</p>;
    }
    const { detailed_data, ai_insights } = vehicle;
    const { basic, valuations, history, recalls, specifications } = detailed_data;

    if (!basic) {
        return <p className="text-center text-red-500">Basic vehicle information is missing.</p>;
    }

    return (
      <div className="space-y-8">
        {/* Vehicle Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
          <div className="flex items-center gap-4 mb-4">
            <Car size={48} />
            <div>
              <h2 className="text-3xl font-bold">{basic.make || 'N/A'} {basic.model || 'N/A'}</h2>
              <p className="text-blue-100 text-lg">{basic.variant || 'N/A'} • {basic.year || 'N/A'}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-100 text-sm">VIN</p>
              <p className="font-semibold">{basic.vin || 'N/A'}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-100 text-sm">VRM</p>
              <p className="font-semibold">{basic.vrm || 'N/A'}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-100 text-sm">Status</p>
              <p className="font-semibold">{basic.vehicle_status || 'N/A'}</p>
            </div>
            <div className="bg-white/10 rounded-lg p-3">
              <p className="text-blue-100 text-sm">Fuel Type</p>
              <p className="font-semibold">{basic.fuel_type || 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* AI Insights */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Activity className="text-purple-600" size={24} />
                <h3 className="text-xl font-semibold text-gray-900">AI Insights</h3>
              </div>
              <button
                onClick={() => handleRefreshInsights(vehicle.vehicle_id)}
                disabled={loading}
                className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors disabled:opacity-50"
                title="Refresh AI Insights"
              >
                <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
              </button>
            </div>
          </div>
          <div className="p-6">
            <div className="prose max-w-none">
              <p className="text-gray-700 mb-6">{ai_insights.summary || 'Summary not available.'}</p>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Key Insights</h4>
                  {ai_insights.key_insights && ai_insights.key_insights.length > 0 ? (
                    <ul className="space-y-2">
                      {ai_insights.key_insights.map((insight, index) => (
                        <li key={index} className="text-gray-700 text-sm leading-relaxed">• {insight}</li>
                      ))}
                    </ul>
                  ) : <p className="text-gray-500 text-sm">No key insights available.</p>}
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Owner Advice</h4>
                  <p className="text-gray-700 text-sm leading-relaxed">{ai_insights.owner_advice || 'No owner advice available.'}</p>
                </div>
              </div>

              {ai_insights.attention_items && ai_insights.attention_items.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Attention Items</h4>
                  <div className="flex flex-wrap gap-2">
                    {ai_insights.attention_items.map((item, index) => (
                      <span key={index} className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full text-sm border border-orange-200">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid md:grid-cols-3 gap-6 mt-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Reliability</h4>
                  <div className="text-2xl font-bold text-blue-600 mb-1">{ai_insights.reliability_assessment?.score || 'N/A'}/10</div>
                  <p className="text-gray-600 text-sm">{ai_insights.reliability_assessment?.explanation || 'No explanation.'}</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Market Position</h4>
                  <p className="text-gray-600 text-sm">{ai_insights.value_assessment?.current_market_position || 'N/A'}</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Technical Highlights</h4>
                  {ai_insights.technical_highlights && ai_insights.technical_highlights.length > 0 ? (
                    <ul className="text-gray-600 text-sm space-y-1">
                      {ai_insights.technical_highlights.slice(0, 3).map((highlight, index) => ( 
                        <li key={index}>• {highlight}</li>
                      ))}
                    </ul>
                  ) : <p className="text-gray-600 text-sm">N/A</p>}
                </div>
              </div>
            </div>
            
            <div className="mt-6 pt-4 border-t border-gray-100">
              <p className="text-gray-500 text-xs">
                Generated: {ai_insights.generated_at ? new Date(ai_insights.generated_at).toLocaleString() : 'N/A'}
                {ai_insights.cached && ' (Cached)'}
              </p>
            </div>
          </div>
        </div>

        {/* Content Sections */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Basic Information */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="text-blue-600" size={20} />
                  <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>
                </div>
                <button
                  onClick={() => toggleSection('basic')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {expandedSections.basic ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>
            </div>
            {expandedSections.basic && (
              <div className="p-6">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div><span className="text-gray-500">Make:</span><span className="ml-2 font-medium">{basic.make || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Model:</span><span className="ml-2 font-medium">{basic.model || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Year:</span><span className="ml-2 font-medium">{basic.year || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Body Type:</span><span className="ml-2 font-medium">{basic.body_type || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Fuel Type:</span><span className="ml-2 font-medium">{basic.fuel_type || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Transmission:</span><span className="ml-2 font-medium">{basic.transmission || 'N/A'}</span></div>
                  <div><span className="text-gray-500">MOT Status:</span><span className={`ml-2 font-medium ${basic.mot_status === 'Valid' ? 'text-green-600' : 'text-red-600'}`}>{basic.mot_status || 'N/A'}</span></div>
                  <div><span className="text-gray-500">MOT Expiry:</span><span className="ml-2 font-medium">{basic.mot_expiry_date || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Tax Status:</span><span className={`ml-2 font-medium ${basic.tax_status === 'Taxed' ? 'text-green-600' : 'text-red-600'}`}>{basic.tax_status || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Tax Due:</span><span className="ml-2 font-medium">{basic.tax_due_date || 'N/A'}</span></div>
                </div>
              </div>
            )}
          </div>

          {/* Valuations */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <DollarSign className="text-green-600" size={20} />
                  <h3 className="text-lg font-semibold text-gray-900">Valuations</h3>
                </div>
                <button
                  onClick={() => toggleSection('valuations')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {expandedSections.valuations ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>
            </div>
            {expandedSections.valuations && (
              <div className="p-6">
                {valuations && valuations.length > 0 ? (
                  <div className="space-y-4">
                    {valuations.map((val, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-3">
                          <span className="font-medium text-gray-900">{val.valuation_date || 'N/A'}</span>
                          <span className="text-sm text-gray-500">{val.condition_grade || 'N/A'}</span>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div><span className="text-gray-500">Retail:</span><span className="ml-2 font-medium">{formatCurrency(val.retail_value)}</span></div>
                          <div><span className="text-gray-500">Trade:</span><span className="ml-2 font-medium">{formatCurrency(val.trade_value)}</span></div>
                          <div><span className="text-gray-500">Private:</span><span className="ml-2 font-medium">{formatCurrency(val.private_value)}</span></div>
                          <div><span className="text-gray-500">Auction:</span><span className="ml-2 font-medium">{formatCurrency(val.auction_value)}</span></div>
                        </div>
                        <div className="mt-2 text-xs text-gray-500">
                          Mileage: {val.mileage_at_valuation?.toLocaleString() || 'N/A'} • Source: {val.valuation_source || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No valuation data available</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Full Width Sections */}
        <div className="space-y-6">
          {/* History */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <History className="text-blue-600" size={20} />
                  <h3 className="text-lg font-semibold text-gray-900">History</h3>
                </div>
                <button
                  onClick={() => toggleSection('history')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {expandedSections.history ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>
            </div>
            {expandedSections.history && (
              <div className="p-6">
                {history && history.length > 0 ? (
                  <div className="space-y-4">
                    {history.map((record, index) => (
                      <div key={index} className="border-l-4 border-blue-200 pl-4 py-2">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className="font-medium text-gray-900">{record.event_type || 'N/A'}</span>
                            <span className="ml-2 text-gray-500">•</span>
                            <span className="ml-2 text-gray-600">{record.event_date || 'N/A'}</span>
                          </div>
                          {record.pass_fail && (
                            <span className={`px-2 py-1 rounded text-xs font-medium ${record.pass_fail === 'PASS' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                              {record.pass_fail}
                            </span>
                          )}
                        </div>
                        <p className="text-gray-700 text-sm">{record.event_description || 'No description.'}</p>
                        <div className="mt-2 text-xs text-gray-500">
                          Mileage: {record.mileage?.toLocaleString() || 'N/A'} • Location: {record.location || 'N/A'}
                          {record.cost && ` • Cost: £${record.cost}`}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No history records available</p>
                )}
              </div>
            )}
          </div>

          {/* Recalls */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="text-orange-600" size={20} />
                  <h3 className="text-lg font-semibold text-gray-900">Recalls</h3>
                </div>
                <button
                  onClick={() => toggleSection('recalls')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {expandedSections.recalls ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>
            </div>
            {expandedSections.recalls && (
              <div className="p-6">
                {recalls && recalls.length > 0 ? (
                  <div className="space-y-4">
                    {recalls.map((recall, index) => (
                      <div key={index} className="border border-orange-200 rounded-lg p-4 bg-orange-50">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-gray-900">{recall.recall_title || 'N/A'}</h4>
                          <span className="text-sm text-gray-500">{recall.recall_date || 'N/A'}</span>
                        </div>
                        <p className="text-gray-700 text-sm mb-2">{recall.recall_description || 'No description.'}</p>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${recall.recall_status === 'Complete' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {recall.recall_status || 'N/A'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Car className="mx-auto text-green-500 mb-2" size={32} /> 
                    <p className="text-green-600 font-medium">No recalls found</p>
                    <p className="text-gray-500 text-sm">This vehicle appears to have no outstanding recalls.</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Specifications */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100">
            <div className="p-6 border-b border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Settings className="text-gray-600" size={20} />
                  <h3 className="text-lg font-semibold text-gray-900">Specifications</h3>
                </div>
                <button
                  onClick={() => toggleSection('specifications')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                >
                  {expandedSections.specifications ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>
            </div>
            {expandedSections.specifications && (
              <div className="p-6">
                {specifications ? (
                  <div className="grid md:grid-cols-3 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Dimensions</h4>
                      <div className="space-y-2 text-sm">
                        <div><span className="text-gray-500">Length:</span><span className="ml-2">{specifications.length_mm || 'N/A'} mm</span></div>
                        <div><span className="text-gray-500">Width:</span><span className="ml-2">{specifications.width_mm || 'N/A'} mm</span></div>
                        <div><span className="text-gray-500">Height:</span><span className="ml-2">{specifications.height_mm || 'N/A'} mm</span></div>
                        <div><span className="text-gray-500">Wheelbase:</span><span className="ml-2">{specifications.wheelbase_mm || 'N/A'} mm</span></div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Performance</h4>
                      <div className="space-y-2 text-sm">
                        <div><span className="text-gray-500">Top Speed:</span><span className="ml-2">{specifications.top_speed_mph || 'N/A'} mph</span></div>
                        <div><span className="text-gray-500">0-60 mph:</span><span className="ml-2">{specifications.acceleration_0_60_mph || 'N/A'} s</span></div>
                        <div><span className="text-gray-500">Drive Type:</span><span className="ml-2">{specifications.drive_type || 'N/A'}</span></div>
                        <div><span className="text-gray-500">Max Towing:</span><span className="ml-2">{specifications.max_towing_weight_kg || 'N/A'} kg</span></div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-3">Capacity</h4>
                      <div className="space-y-2 text-sm">
                        <div><span className="text-gray-500">Fuel Tank:</span><span className="ml-2">{specifications.fuel_tank_capacity || 'N/A'} L</span></div>
                        <div><span className="text-gray-500">Boot:</span><span className="ml-2">{specifications.boot_capacity_litres || 'N/A'} L</span></div>
                        <div><span className="text-gray-500">Kerb Weight:</span><span className="ml-2">{specifications.kerb_weight_kg || 'N/A'} kg</span></div>
                        <div><span className="text-gray-500">Gross Weight:</span><span className="ml-2">{specifications.gross_weight_kg || 'N/A'} kg</span></div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-4">No specification data available</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Vehicle Insights</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get comprehensive vehicle information and AI-powered insights using VIN or VRM lookup
          </p>
        </div>

        {/* Health Status */}
        <div className="flex justify-center mb-8">
          <div className={`px-4 py-2 rounded-full text-sm font-medium ${
            healthStatus === 'healthy' 
              ? 'bg-green-100 text-green-800' 
              : healthStatus === 'unhealthy'
              ? 'bg-red-100 text-red-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            API Status: {healthStatus || 'Checking...'}
          </div>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8 max-w-2xl mx-auto">
          <form onSubmit={handleSearch} className="space-y-6">
            <div className="flex justify-center">
              <div className="bg-gray-100 rounded-lg p-1 flex">
                <label className={`px-6 py-2 rounded-md cursor-pointer transition-all font-medium ${
                  searchType === 'vin' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}>
                  <input type="radio" value="vin" checked={searchType === 'vin'} onChange={(e) => setSearchType(e.target.value)} className="sr-only" />
                  VIN Lookup
                </label>
                <label className={`px-6 py-2 rounded-md cursor-pointer transition-all font-medium ${
                  searchType === 'vrn' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}>
                  <input type="radio" value="vrn" checked={searchType === 'vrn'} onChange={(e) => setSearchType(e.target.value)} className="sr-only" />
                  VRN Lookup
                </label>
              </div>
            </div>

            <div className="relative">
              <input
                type="text"
                placeholder={searchType === 'vin' ? 'Enter 17-character VIN' : 'Enter Vehicle Registration Number'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                disabled={loading}
                className="w-full px-6 py-4 text-lg border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                <Search className="text-gray-400" size={24} />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !searchQuery.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 px-8 rounded-xl font-semibold text-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150 ease-in-out flex items-center justify-center"
            >
              {loading && !selectedVehicle ? ( // Show loading specific to main search when no vehicle is selected yet
                <>
                  <RefreshCw className="animate-spin mr-2" size={20} /> Searching...
                </>
              ) : (
                'Search Vehicle'
              )}
            </button>
          </form>
        </div>

        {/* Results Area */}
        <div className="mt-12">
          {loading && !selectedVehicle && ( 
            <div className="flex flex-col justify-center items-center py-10">
              <RefreshCw className="animate-spin text-blue-600" size={48} />
              <p className="mt-4 text-xl text-gray-700">Loading vehicle data...</p>
            </div>
          )}
          {error && !loading && (
            <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-6 rounded-lg shadow-md max-w-3xl mx-auto">
              <div className="flex">
                <div className="py-1"><AlertTriangle className="h-6 w-6 text-red-500 mr-3" /></div>
                <div>
                  <p className="font-bold">Error</p>
                  <p>{error}</p>
                </div>
              </div>
            </div>
          )}
          {selectedVehicle && ( // Render vehicle details if available, loading state for refresh is handled within renderVehicleDetails' refresh button
            renderVehicleDetails(selectedVehicle)
          )}
          {!loading && !error && !selectedVehicle && !searchQuery.trim() && (
             <div className="text-center text-gray-500 py-10">
                <Car size={64} className="mx-auto mb-4 text-gray-400" />
                <p className="text-lg">Enter a VIN or VRM to begin your search.</p>
                <p className="text-sm mt-2">Example VIN: SAMPLETESTVINURFY, Example VRM: AB05IYG</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;