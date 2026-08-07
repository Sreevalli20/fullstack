export interface StoreWeatherDataRequest {
  latitude: number;
  longitude: number;
  start_date: string;
  end_date: string;
}

export interface StoreWeatherDataResponse {
  status: string;
  file: string;
}

export interface WeatherFileInfo {
  name: string;
  size: number;
  created_at: string;
}

export interface ListWeatherFilesResponse {
  files: WeatherFileInfo[];
}

export interface DailyUnits {
  time: string;
  temperature_2m_max: string;
  temperature_2m_min: string;
  apparent_temperature_max: string;
  apparent_temperature_min: string;
}

export interface DailyData {
  time: string[];
  temperature_2m_max: number[];
  temperature_2m_min: number[];
  apparent_temperature_max?: number[];
  apparent_temperature_min?: number[];
}

export interface WeatherFileContent {
  latitude: number;
  longitude: number;
  generationtime_ms?: number;
  utc_offset_seconds?: number;
  timezone?: string;
  elevation?: number;
  daily_units?: DailyUnits;
  daily: DailyData;
}

export interface HealthStatusResponse {
  status: string;
  service: string;
  storage_mode: string;
  s3_bucket: string;
  region: string;
}
