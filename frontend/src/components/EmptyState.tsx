import React from 'react';
import { CloudRain, FileSpreadsheet } from 'lucide-react';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: 'cloud' | 'file';
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No Weather Data Selected',
  description = 'Submit coordinates using the form or select a stored file from the browser list to visualize temperatures.',
  icon = 'cloud',
  action,
}) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-10 rounded-xl text-center flex flex-col items-center justify-center space-y-3 shadow-sm">
      <div className="p-4 bg-blue-50 dark:bg-blue-950/40 border border-blue-100 dark:border-blue-900/40 rounded-full text-blue-600 dark:text-blue-400">
        {icon === 'cloud' ? <CloudRain className="w-8 h-8" /> : <FileSpreadsheet className="w-8 h-8" />}
      </div>
      <h3 className="text-base font-bold text-slate-800 dark:text-slate-100">{title}</h3>
      <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm font-sans">{description}</p>
      {action && <div className="pt-2">{action}</div>}
    </div>
  );
};
