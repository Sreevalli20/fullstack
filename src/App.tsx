import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { InputForm } from './components/InputForm';
import { StoredFiles } from './components/StoredFiles';
import { WeatherChart } from './components/WeatherChart';
import { WeatherTable } from './components/WeatherTable';
import { ErrorAlert } from './components/ErrorAlert';
import { useWeatherData } from './hooks/useWeatherData';
import { Database, HardDrive, Layers, Activity } from 'lucide-react';

export function App() {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('theme') === 'dark' || false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const {
    health,
    files,
    activeFilename,
    activeFileContent,
    filesLoading,
    contentLoading,
    submitLoading,
    error,
    clearError,
    loadFiles,
    selectFile,
    handleSubmitStoreData,
  } = useWeatherData();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-200">
      
      {/* Navigation Header */}
      <Navbar
        health={health}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Error Alert Display */}
        {error && (
          <ErrorAlert
            message={error}
            onDismiss={clearError}
            title="S3 Storage & Weather API Notice"
          />
        )}

        {/* Top Metric Cards Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-xl shadow-xs flex flex-col justify-between">
            <div>
              <p className="text-slate-500 dark:text-slate-400 text-[11px] font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-blue-500" />
                Stored Weather Files
              </p>
              <p className="text-3xl font-light text-slate-900 dark:text-white font-mono">
                {files.length}
              </p>
            </div>
            <div className="mt-3 flex items-center text-xs text-emerald-600 dark:text-emerald-400 font-bold font-mono">
              <span>Syncing with S3 Bucket</span>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-xl shadow-xs flex flex-col justify-between">
            <div>
              <p className="text-slate-500 dark:text-slate-400 text-[11px] font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <HardDrive className="w-3.5 h-3.5 text-purple-500" />
                AWS S3 Bucket Target
              </p>
              <p className="text-sm font-bold text-slate-800 dark:text-slate-100 font-mono truncate" title={health?.s3_bucket || 'weather-data-bucket'}>
                {health?.s3_bucket || 'weather-data-bucket'}
              </p>
            </div>
            <div className="mt-3 flex items-center text-xs text-blue-600 dark:text-blue-400 font-bold font-mono">
              <span>Region: {health?.region || 'us-east-1'}</span>
            </div>
          </div>

          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-xl shadow-xs flex flex-col justify-between">
            <div>
              <p className="text-slate-500 dark:text-slate-400 text-[11px] font-bold uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-500" />
                Open-Meteo Latency
              </p>
              <p className="text-3xl font-light text-slate-900 dark:text-white font-mono">
                ~120 ms
              </p>
            </div>
            <div className="mt-3 flex items-center text-xs text-emerald-600 dark:text-emerald-400 font-bold font-mono">
              <span>Historical API: Online</span>
            </div>
          </div>

          <div className="bg-slate-900 dark:bg-slate-900 border border-slate-800 p-5 rounded-xl shadow-xs flex flex-col justify-between text-white">
            <p className="text-slate-400 text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              Engine Tech Stack
            </p>
            <div className="font-mono text-xs space-y-1 mt-2">
              <div className="flex justify-between border-b border-slate-800 py-0.5">
                <span className="text-slate-300">FastAPI</span>
                <span className="text-emerald-400 font-bold">v0.110</span>
              </div>
              <div className="flex justify-between border-b border-slate-800 py-0.5">
                <span className="text-slate-300">boto3</span>
                <span className="text-emerald-400 font-bold">AWS S3</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-slate-300">slowapi</span>
                <span className="text-emerald-400 font-bold">Limited</span>
              </div>
            </div>
          </div>

        </div>

        {/* Primary 2-Column Inputs & Files Browser */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-5">
            <InputForm
              onSubmit={handleSubmitStoreData}
              loading={submitLoading}
            />
          </div>
          <div className="lg:col-span-7">
            <StoredFiles
              files={files}
              activeFilename={activeFilename}
              onSelectFile={selectFile}
              onRefresh={loadFiles}
              loading={filesLoading}
            />
          </div>
        </div>

        {/* Weather Chart Visualization */}
        <WeatherChart
          weatherData={activeFileContent}
          loading={contentLoading}
          filename={activeFilename}
        />

        {/* Paginated Data Table */}
        <WeatherTable
          weatherData={activeFileContent}
          loading={contentLoading}
        />

        {/* System Footer Status Bar */}
        <footer className="bg-blue-600 dark:bg-blue-950/80 border border-blue-500/30 rounded-xl p-5 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-sm">
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 bg-white rounded-full animate-pulse"></div>
              <span className="text-xs font-bold uppercase tracking-wider">AWS S3 Backend Active</span>
            </div>
            <div className="flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 bg-blue-300 rounded-full"></div>
              <span className="text-xs font-bold uppercase tracking-wider font-mono">
                boto3 Credential Chain
              </span>
            </div>
          </div>
          <span className="font-mono text-xs text-blue-100 uppercase font-semibold">
            WeatherS3 Pro Dashboard v1.0.0
          </span>
        </footer>

      </main>
    </div>
  );
}

export default App;
