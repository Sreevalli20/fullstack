import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { WeatherFileContent } from '../types/weather';
import { ChartSkeleton } from './LoadingSkeletons';
import { EmptyState } from './EmptyState';

interface WeatherChartProps {
  weatherData: WeatherFileContent | null;
  loading: boolean;
  filename: string | null;
}

export const WeatherChart: React.FC<WeatherChartProps> = ({
  weatherData,
  loading,
  filename,
}) => {
  const [unit, setUnit] = useState<'C' | 'F'>('C');

  if (loading) return <ChartSkeleton />;
  if (!weatherData || !weatherData.daily || !weatherData.daily.time) {
    return <EmptyState title="No Chart Data" description="Select a weather payload file above to render interactive temperature charts." />;
  }

  const cToF = (celsius: number) => Number(((celsius * 9) / 5 + 32).toFixed(1));

  const chartData = weatherData.daily.time.map((dateStr, index) => {
    const tMax = weatherData.daily.temperature_2m_max?.[index] ?? 0;
    const tMin = weatherData.daily.temperature_2m_min?.[index] ?? 0;
    const appMax = weatherData.daily.apparent_temperature_max?.[index] ?? tMax;
    const appMin = weatherData.daily.apparent_temperature_min?.[index] ?? tMin;

    return {
      date: dateStr,
      maxTemp: unit === 'F' ? cToF(tMax) : tMax,
      minTemp: unit === 'F' ? cToF(tMin) : tMin,
      apparentMax: unit === 'F' ? cToF(appMax) : appMax,
      apparentMin: unit === 'F' ? cToF(appMin) : appMin,
    };
  });

  const unitLabel = unit === 'F' ? '°F' : '°C';

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl shadow-xs">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 dark:border-slate-800 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-blue-500 rounded-sm"></span>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
              Daily Temperature Trends
            </h2>
          </div>
          {filename && (
            <p className="text-xs font-mono text-slate-500 dark:text-slate-400 mt-1 truncate max-w-md">
              Source Payload: {filename}
            </p>
          )}
        </div>

        {/* Unit Switcher */}
        <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-800 p-1 rounded-lg self-start sm:self-auto border border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setUnit('C')}
            className={`px-3 py-1 rounded text-xs font-bold transition ${
              unit === 'C'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            °C (Celsius)
          </button>
          <button
            onClick={() => setUnit('F')}
            className={`px-3 py-1 rounded text-xs font-bold transition ${
              unit === 'F'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            °F (Fahrenheit)
          </button>
        </div>
      </div>

      {/* Recharts Container */}
      <div className="w-full h-80 pt-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: '#64748b' }}
              tickLine={false}
            />
            <YAxis
              unit={unitLabel}
              tick={{ fontSize: 11, fill: '#64748b' }}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '12px',
                fontFamily: 'monospace',
              }}
              formatter={(value: any) => [`${value} ${unitLabel}`, '']}
            />
            <Legend
              wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
            />
            <Line
              type="monotone"
              dataKey="maxTemp"
              name={`Max Temp (${unitLabel})`}
              stroke="#ef4444"
              strokeWidth={2.5}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="minTemp"
              name={`Min Temp (${unitLabel})`}
              stroke="#3b82f6"
              strokeWidth={2.5}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="apparentMax"
              name={`Apparent Max (${unitLabel})`}
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="apparentMin"
              name={`Apparent Min (${unitLabel})`}
              stroke="#06b6d4"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
};
