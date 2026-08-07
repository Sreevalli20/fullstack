import React, { useState } from 'react';
import { MapPin, Calendar, Database, RefreshCw, Send } from 'lucide-react';
import { StoreWeatherDataRequest } from '../types/weather';
import { LoadingSpinner } from './LoadingSpinner';

interface InputFormProps {
  onSubmit: (data: StoreWeatherDataRequest) => Promise<void>;
  loading: boolean;
}

const PRESET_LOCATIONS = [
  { name: 'San Francisco', lat: 37.7749, lon: -122.4194 },
  { name: 'New York', lat: 40.7128, lon: -74.0060 },
  { name: 'London', lat: 51.5074, lon: -0.1278 },
  { name: 'Tokyo', lat: 35.6762, lon: 139.6503 },
  { name: 'Sydney', lat: -33.8688, lon: 151.2093 },
];

export const InputForm: React.FC<InputFormProps> = ({ onSubmit, loading }) => {
  const today = new Date();
  const tenDaysAgo = new Date();
  tenDaysAgo.setDate(today.getDate() - 10);

  const [latitude, setLatitude] = useState<number>(37.7749);
  const [longitude, setLongitude] = useState<number>(-122.4194);
  const [startDate, setStartDate] = useState<string>(tenDaysAgo.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState<string>(today.toISOString().split('T')[0]);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleSelectPreset = (lat: number, lon: number) => {
    setLatitude(lat);
    setLongitude(lon);
    setValidationError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    // Coordinate validation
    if (latitude < -90 || latitude > 90) {
      setValidationError('Latitude must be between -90 and 90 degrees.');
      return;
    }
    if (longitude < -180 || longitude > 180) {
      setValidationError('Longitude must be between -180 and 180 degrees.');
      return;
    }

    // Date validation
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (isNaN(start.getTime()) || isNaN(end.getTime())) {
      setValidationError('Please select valid start and end dates.');
      return;
    }

    if (start > end) {
      setValidationError('Start date must be less than or equal to End date.');
      return;
    }

    const diffDays = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    if (diffDays > 31) {
      setValidationError(`Maximum allowed date range is 31 days. Current selection is ${diffDays} days.`);
      return;
    }

    await onSubmit({
      latitude,
      longitude,
      start_date: startDate,
      end_date: endDate,
    });
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl shadow-xs">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 bg-blue-600 rounded-sm"></div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
            Fetch Weather & Persist to S3
          </h2>
        </div>
        <span className="text-[10px] font-mono font-bold bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded border border-blue-100 dark:border-blue-900">
          POST /store-weather-data
        </span>
      </div>

      {/* Preset Location Shortcuts */}
      <div className="mb-4">
        <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Location Shortcuts</p>
        <div className="flex flex-wrap gap-1.5">
          {PRESET_LOCATIONS.map((loc) => (
            <button
              key={loc.name}
              type="button"
              onClick={() => handleSelectPreset(loc.lat, loc.lon)}
              className={`text-xs px-2.5 py-1 rounded-md font-mono transition border ${
                latitude === loc.lat && longitude === loc.lon
                  ? 'bg-blue-600 text-white border-blue-600 font-bold'
                  : 'bg-slate-50 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'
              }`}
            >
              📍 {loc.name}
            </button>
          ))}
        </div>
      </div>

      {/* Form Fields */}
      <form onSubmit={handleSubmit} className="space-y-4">
        
        {/* Coordinates Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-blue-500" />
              Latitude (-90 to 90)
            </label>
            <input
              type="number"
              step="any"
              value={latitude}
              onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
              required
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              placeholder="e.g. 37.7749"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-blue-500" />
              Longitude (-180 to 180)
            </label>
            <input
              type="number"
              step="any"
              value={longitude}
              onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
              required
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              placeholder="e.g. -122.4194"
            />
          </div>
        </div>

        {/* Date Range Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-emerald-500" />
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-emerald-500" />
              End Date (Max 31 days)
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
              className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-900 dark:text-slate-100 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            />
          </div>
        </div>

        {/* Validation Error Banner */}
        {validationError && (
          <div className="p-3 bg-amber-50 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-900/60 rounded-lg text-amber-800 dark:text-amber-300 text-xs font-mono">
            ⚠️ {validationError}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 bg-slate-900 dark:bg-blue-600 hover:bg-slate-800 dark:hover:bg-blue-500 text-white font-bold text-xs rounded-lg transition uppercase tracking-wider flex items-center justify-center gap-2 shadow disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <LoadingSpinner size="sm" label="Fetching & Uploading to S3..." />
          ) : (
            <>
              <Send className="w-4 h-4" />
              <span>Fetch & Store in AWS S3</span>
            </>
          )}
        </button>

      </form>
    </div>
  );
};
