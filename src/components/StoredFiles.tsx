import React, { useState } from 'react';
import { Database, RefreshCw, Search, FileText, CheckCircle2 } from 'lucide-react';
import { WeatherFileInfo } from '../types/weather';
import { FileListSkeleton } from './LoadingSkeletons';

interface StoredFilesProps {
  files: WeatherFileInfo[];
  activeFilename: string | null;
  onSelectFile: (filename: string) => void;
  onRefresh: () => void;
  loading: boolean;
}

export const StoredFiles: React.FC<StoredFilesProps> = ({
  files,
  activeFilename,
  onSelectFile,
  onRefresh,
  loading,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFiles = files.filter((f) =>
    f.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-xl shadow-xs flex flex-col">
      
      {/* Header */}
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 bg-emerald-500 rounded-sm"></div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
            Stored S3 Weather Datasets
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded">
            {files.length} Object{files.length === 1 ? '' : 's'}
          </span>
          <button
            onClick={onRefresh}
            disabled={loading}
            className="p-1.5 text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
            title="Refresh S3 bucket object list"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Search Input */}
      <div className="relative mb-3">
        <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Filter S3 files by name or date..."
          className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg text-xs text-slate-800 dark:text-slate-200 font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        />
      </div>

      {/* File List Area */}
      <div className="flex-1 max-h-60 overflow-y-auto space-y-2 pr-1">
        {loading && files.length === 0 ? (
          <FileListSkeleton />
        ) : filteredFiles.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400 font-mono">
            {searchQuery ? 'No matching S3 objects found.' : 'No weather files stored in S3 yet.'}
          </div>
        ) : (
          filteredFiles.map((f) => {
            const isActive = activeFilename === f.name;
            return (
              <div
                key={f.name}
                onClick={() => onSelectFile(f.name)}
                className={`p-3 rounded-lg border cursor-pointer transition flex items-center justify-between group ${
                  isActive
                    ? 'bg-blue-50/80 dark:bg-blue-950/40 border-blue-400 dark:border-blue-700'
                    : 'bg-slate-50 dark:bg-slate-950 hover:bg-slate-100 dark:hover:bg-slate-800/80 border-slate-200 dark:border-slate-800'
                }`}
              >
                <div className="truncate pr-2 flex items-center gap-2.5">
                  <FileText className={`w-4 h-4 shrink-0 ${isActive ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400'}`} />
                  <div className="truncate">
                    <p className={`text-xs font-mono font-bold truncate ${isActive ? 'text-blue-900 dark:text-blue-200' : 'text-slate-800 dark:text-slate-200 group-hover:text-blue-600'}`}>
                      {f.name}
                    </p>
                    <p className="text-[10px] font-mono text-slate-400">
                      {formatDate(f.created_at)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-[10px] font-mono font-semibold text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2 py-0.5 rounded">
                    {formatSize(f.size)}
                  </span>
                  {isActive && <CheckCircle2 className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
