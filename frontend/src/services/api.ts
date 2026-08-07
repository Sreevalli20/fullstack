import axios from 'axios';
import {
  StoreWeatherDataRequest,
  StoreWeatherDataResponse,
  ListWeatherFilesResponse,
  WeatherFileContent,
  HealthStatusResponse,
} from '../types/weather';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('API_BASE_URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 25000,
});

export const fetchHealthStatus = async (): Promise<HealthStatusResponse> => {
  const response = await api.get<HealthStatusResponse>('/health');
  return response.data;
};

export const storeWeatherData = async (
  data: StoreWeatherDataRequest
): Promise<StoreWeatherDataResponse> => {
  const response = await api.post<StoreWeatherDataResponse>('/store-weather-data', data);
  return response.data;
};

export const listWeatherFiles = async (): Promise<ListWeatherFilesResponse> => {
  const response = await api.get<ListWeatherFilesResponse>('/list-weather-files');
  return response.data;
};

export const getWeatherFileContent = async (
  filename: string
): Promise<WeatherFileContent> => {
  const encodedName = encodeURIComponent(filename);
  const response = await api.get<WeatherFileContent>(`/weather-file-content/${encodedName}`);
  return response.data;
};

export default api;
