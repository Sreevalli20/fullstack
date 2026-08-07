import { useState, useEffect, useCallback } from 'react';
import {
  WeatherFileInfo,
  WeatherFileContent,
  StoreWeatherDataRequest,
  HealthStatusResponse,
} from '../types/weather';
import {
  listWeatherFiles,
  getWeatherFileContent,
  storeWeatherData,
  fetchHealthStatus,
} from '../services/api';

export const useWeatherData = () => {
  const [health, setHealth] = useState<HealthStatusResponse | null>(null);
  const [files, setFiles] = useState<WeatherFileInfo[]>([]);
  const [activeFilename, setActiveFilename] = useState<string | null>(null);
  const [activeFileContent, setActiveFileContent] = useState<WeatherFileContent | null>(null);

  const [filesLoading, setFilesLoading] = useState<boolean>(false);
  const [contentLoading, setContentLoading] = useState<boolean>(false);
  const [submitLoading, setSubmitLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  // Fetch health status
  const loadHealth = useCallback(async () => {
    try {
      const data = await fetchHealthStatus();
      setHealth(data);
    } catch {
      // Ignore initial health check error silently if dev proxy is warming up
    }
  }, []);

  // Fetch list of files stored in S3
  const loadFiles = useCallback(async () => {
    setFilesLoading(true);
    try {
      const res = await listWeatherFiles();
      setFiles(res.files || []);
      // If there are files and none selected, auto-select the latest file
      if (res.files && res.files.length > 0 && !activeFilename) {
        selectFile(res.files[0].name);
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Failed to list weather files from S3.';
      setError(msg);
    } finally {
      setFilesLoading(false);
    }
  }, [activeFilename]);

  // Select and download content for a specific file
  const selectFile = useCallback(async (filename: string) => {
    setActiveFilename(filename);
    setContentLoading(true);
    clearError();
    try {
      const content = await getWeatherFileContent(filename);
      setActiveFileContent(content);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || `Failed to fetch payload for ${filename}`;
      setError(msg);
    } finally {
      setContentLoading(false);
    }
  }, []);

  // Submit form to fetch Open-Meteo & store in S3
  const handleSubmitStoreData = async (req: StoreWeatherDataRequest) => {
    setSubmitLoading(true);
    clearError();
    try {
      const res = await storeWeatherData(req);
      if (res.file) {
        await loadFiles();
        await selectFile(res.file);
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Error executing POST /store-weather-data';
      setError(msg);
    } finally {
      setSubmitLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
    loadFiles();
  }, [loadHealth, loadFiles]);

  return {
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
  };
};
