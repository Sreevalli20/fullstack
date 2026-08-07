import React from 'react';

export const ChartSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl animate-pulse space-y-4">
    <div className="flex justify-between items-center pb-3 border-b border-slate-100 dark:border-slate-800">
      <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/3"></div>
      <div className="h-6 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
    </div>
    <div className="h-64 bg-slate-100 dark:bg-slate-800/50 rounded-lg flex items-end justify-between p-4 gap-2">
      {[40, 65, 45, 80, 55, 70, 60, 85, 50, 75].map((height, i) => (
        <div key={i} className="w-full bg-slate-200 dark:bg-slate-800 rounded-t" style={{ height: `${height}%` }}></div>
      ))}
    </div>
  </div>
);

export const FileListSkeleton: React.FC = () => (
  <div className="space-y-3 animate-pulse">
    {[1, 2, 3, 4].map((i) => (
      <div key={i} className="p-3 bg-slate-100 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-800 flex justify-between items-center">
        <div className="space-y-2 w-3/4">
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-5/6"></div>
          <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded w-1/3"></div>
        </div>
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-12"></div>
      </div>
    ))}
  </div>
);

export const TableSkeleton: React.FC = () => (
  <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl animate-pulse space-y-4">
    <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4"></div>
    <div className="space-y-2">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="h-10 bg-slate-100 dark:bg-slate-800/50 rounded flex items-center justify-between px-4">
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-20"></div>
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
          <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-16"></div>
        </div>
      ))}
    </div>
  </div>
);
