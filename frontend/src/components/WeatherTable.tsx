import React, { useState } from 'react';
import { Download, ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react';
import { WeatherFileContent } from '../types/weather';
import { TableSkeleton } from './LoadingSkeletons';

interface WeatherTableProps {
  weatherData: WeatherFileContent | null;
  loading: boolean;
}

export const WeatherTable: React.FC<WeatherTableProps> = ({
  weatherData,
  loading,
}) => {
  const [pageSize, setPageSize] = useState<number>(10);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [sortAsc, setSortAsc] = useState<boolean>(true);

  if (loading) return <TableSkeleton />;
  if (!weatherData || !weatherData.daily || !weatherData.daily.time) return null;

  const rawTimes = weatherData.daily.time;
  const rawMax = weatherData.daily.temperature_2m_max || [];
  const rawMin = weatherData.daily.temperature_2m_min || [];
  const rawAppMax = weatherData.daily.apparent_temperature_max || [];
  const rawAppMin = weatherData.daily.apparent_temperature_min || [];

  let rows = rawTimes.map((dateStr, idx) => ({
    date: dateStr,
    maxTemp: rawMax[idx] ?? 'N/A',
    minTemp: rawMin[idx] ?? 'N/A',
    apparentMax: rawAppMax[idx] ?? 'N/A',
    apparentMin: rawAppMin[idx] ?? 'N/A',
  }));

  if (!sortAsc) {
    rows = [...rows].reverse();
  }

  const totalPages = Math.ceil(rows.length / pageSize) || 1;
  const startIndex = (currentPage - 1) * pageSize;
  const paginatedRows = rows.slice(startIndex, startIndex + pageSize);

  const handleExportCSV = () => {
    const headers = ['Date', 'Max Temp (°C)', 'Min Temp (°C)', 'Apparent Max (°C)', 'Apparent Min (°C)'];
    const csvContent = [
      headers.join(','),
      ...rows.map((r) => [r.date, r.maxTemp, r.minTemp, r.apparentMax, r.apparentMin].join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `weather_data_${weatherData.latitude}_${weatherData.longitude}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl shadow-xs">
      
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 dark:border-slate-800 gap-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 bg-slate-900 dark:bg-slate-100 rounded-sm"></span>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
            Daily Weather Data Table
          </h2>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          
          {/* Page Size Dropdown */}
          <div className="flex items-center gap-2 text-xs font-medium text-slate-600 dark:text-slate-400">
            <span>Rows:</span>
            <select
              value={pageSize}
              onChange={(e) => {
                setPageSize(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded px-2 py-1 text-xs text-slate-800 dark:text-slate-200 font-mono focus:outline-none"
            >
              <option value={10}>10 per page</option>
              <option value={20}>20 per page</option>
              <option value={50}>50 per page</option>
            </select>
          </div>

          {/* Export CSV Button */}
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1.5 px-3 py-1 bg-slate-900 dark:bg-blue-600 hover:bg-slate-800 dark:hover:bg-blue-500 text-white font-bold text-xs rounded-lg transition shadow-xs"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>

        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-500 dark:text-slate-400 font-bold">
              <th className="py-3 px-4">
                <button
                  onClick={() => setSortAsc(!sortAsc)}
                  className="flex items-center gap-1 hover:text-slate-900 dark:hover:text-white transition"
                >
                  <span>Date</span>
                  <ArrowUpDown className="w-3 h-3" />
                </button>
              </th>
              <th className="py-3 px-4 text-rose-600 dark:text-rose-400">Max Temp (°C)</th>
              <th className="py-3 px-4 text-blue-600 dark:text-blue-400">Min Temp (°C)</th>
              <th className="py-3 px-4 text-amber-600 dark:text-amber-400">Apparent Max (°C)</th>
              <th className="py-3 px-4 text-cyan-600 dark:text-cyan-400">Apparent Min (°C)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {paginatedRows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                <td className="py-2.5 px-4 font-bold text-slate-900 dark:text-slate-100">{row.date}</td>
                <td className="py-2.5 px-4 font-semibold text-slate-800 dark:text-slate-200">{row.maxTemp} °C</td>
                <td className="py-2.5 px-4 font-semibold text-slate-800 dark:text-slate-200">{row.minTemp} °C</td>
                <td className="py-2.5 px-4 text-slate-600 dark:text-slate-400">{row.apparentMax} °C</td>
                <td className="py-2.5 px-4 text-slate-600 dark:text-slate-400">{row.apparentMin} °C</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="flex items-center justify-between pt-4 mt-4 border-t border-slate-100 dark:border-slate-800 text-xs font-mono text-slate-500">
        <div>
          Showing {startIndex + 1} to {Math.min(startIndex + pageSize, rows.length)} of {rows.length} entries
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="p-1.5 rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="p-1.5 rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-30 disabled:cursor-not-allowed transition"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

    </div>
  );
};
