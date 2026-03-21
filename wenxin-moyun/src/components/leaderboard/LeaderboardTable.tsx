import React, { useMemo, useState, Suspense, lazy, useCallback } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
} from '@tanstack/react-table';
import type {
  SortingState,
  ColumnFiltersState,
  VisibilityState,
} from '@tanstack/react-table';
import { 
  ChevronUp, 
  ChevronDown, 
  ChevronsUpDown,
  Download,
  Filter,
  Trophy,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight
} from 'lucide-react';
import { motion } from 'framer-motion';
import type { LeaderboardEntry, Model, VULCAScore47D } from '../../types/types';
import type { VULCAEvaluation, VULCAScore6D } from '../../types/vulca';
import { exportData } from '../../utils/dataExport';
import RouterLink from '../common/RouterLink';
import { getDimensionLabel } from '../../utils/vulca-dimensions';
import { vulcaDataManager } from '../../services/vulcaDataManager';

// 懒加载VULCA可视化组件
const VULCAVisualization = lazy(() => 
  import('../vulca/VULCAVisualization').then(module => ({
    default: module.VULCAVisualization
  }))
);

// VULCA数据显示组件
interface VULCADataDisplayProps {
  model: Model;
  score: number | null;
  convertToEvaluation: (model: Model) => Promise<VULCAEvaluation>;
  getDefaultDimensions: (scores: VULCAScore47D) => Array<{ id: string; name: string; description: string }>;
  calculate47DAverage: (scores: VULCAScore47D) => number | null;
}

const VULCADataDisplay: React.FC<VULCADataDisplayProps> = ({
  model,
  score,
  convertToEvaluation,
  getDefaultDimensions,
  calculate47DAverage
}) => {
  const [evaluation, setEvaluation] = useState<VULCAEvaluation | null>(null);
  const [dimensions, setDimensions] = useState<Array<{ id: string; name: string; description: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  React.useEffect(() => {
    const loadVulcaData = async () => {
      try {
        setLoading(true);
        const evalData = await convertToEvaluation(model);
        setEvaluation(evalData);
        setDimensions(getDefaultDimensions(evalData.scores47D));
        setError(null);
      } catch (err) {
        console.error('Error loading VULCA data:', err);
        setError('Failed to load VULCA data');
      } finally {
        setLoading(false);
      }
    };
    
    loadVulcaData();
  }, [model, convertToEvaluation, getDefaultDimensions]);
  
  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
          <div className="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 border-t-slate-700 dark:border-t-slate-500 rounded-full animate-spin" />
          Loading VULCA Analysis...
        </div>
      </div>
    );
  }
  
  if (error || !evaluation) {
    return (
      <div className="p-8 text-center text-red-500">
        {error || 'No VULCA data available for this model'}
      </div>
    );
  }
  
  const vulcaAverage = calculate47DAverage(evaluation.scores47D);
  
  return (
    <div className="space-y-4">
      {/* 分数说明 */}
      <div className="flex items-center justify-between p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
        <div className="flex items-center gap-6">
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Overall Score</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {score != null ? score.toFixed(3) : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">VULCA 47D Average</div>
            <div className="text-2xl font-bold text-amber-700 dark:text-amber-500">
              {vulcaAverage != null ? vulcaAverage.toFixed(1) : 'N/A'}
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 max-w-md">
          <p><strong>Overall Score</strong> is the model's comprehensive evaluation score.</p>
          <p><strong>VULCA 47D Average</strong> is the mean of all 47 dimension scores.</p>
        </div>
      </div>
      
      {/* VULCA可视化 */}
      <VULCAVisualization
        evaluations={[evaluation]}
        dimensions={dimensions}
        viewMode="47d"
        visualizationType="radar"
        culturalPerspective="eastern"
      />
    </div>
  );
};

/** Avatar with letter fallback for models without images. */
function TableModelAvatar({ src, name }: { src?: string; name: string }) {
  const [failed, setFailed] = React.useState(false);
  if (!src || failed) {
    return (
      <div className="w-10 h-10 rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 font-semibold text-sm select-none shadow-sm">
        {name.charAt(0).toUpperCase()}
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={name}
      className="w-10 h-10 rounded-lg shadow-sm group-hover:shadow-md transition-shadow"
      onError={() => setFailed(true)}
    />
  );
}

interface LeaderboardTableProps {
  data: LeaderboardEntry[];
  loading?: boolean;
  onRowClick?: (entry: LeaderboardEntry) => void;
  expandedVulcaModels?: Set<string>;
  onToggleVulca?: (modelId: string) => void;
}

const columnHelper = createColumnHelper<LeaderboardEntry>();

export default function LeaderboardTable({ 
  data, 
  loading, 
  onRowClick, 
  expandedVulcaModels = new Set(), 
  onToggleVulca 
}: LeaderboardTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});
  const [globalFilter, setGlobalFilter] = useState('');

  const parseJsonField = useCallback((value: unknown) => {
    if (!value) return null;
    if (typeof value === 'string') {
      try {
        return JSON.parse(value);
      } catch {
        return null;
      }
    }
    return value;
  }, []);

  const extractScores6D = useCallback((scores47D: VULCAScore47D | null | undefined): VULCAScore6D => {
    const defaultScores: VULCAScore6D = {
      creativity: 0,
      technique: 0,
      emotion: 0,
      context: 0,
      innovation: 0,
      impact: 0
    };
    if (!scores47D) return defaultScores;
    return {
      creativity: scores47D.creativity || scores47D.originality || scores47D.imagination || 0,
      technique: scores47D.technique || scores47D.precision || scores47D.skill_level || 0,
      emotion: scores47D.emotion || scores47D.emotional_depth || scores47D.affective_resonance || 0,
      context: scores47D.context || scores47D.relevance || scores47D.contextual_awareness || 0,
      innovation: scores47D.innovation || scores47D.uniqueness || scores47D.novelty || 0,
      impact: scores47D.impact || scores47D.influence || scores47D.significance || 0
    };
  }, []);

  const convertToEvaluation = useCallback(async (model: Model): Promise<VULCAEvaluation> => {
    const evaluation = await vulcaDataManager.getModelVULCAData(
      model.id.toString(),
      model.name || 'Unknown Model'
    );

    const rawScores = parseJsonField(model.vulca_scores_47d);
    if (rawScores && typeof rawScores === 'object' && Object.keys(rawScores).length > 0) {
      const numericScores = Object.fromEntries(
        Object.entries(rawScores as Record<string, unknown>).filter(([, value]) => typeof value === 'number')
      ) as VULCAScore47D;
      if (Object.keys(numericScores).length > 0) {
        evaluation.scores47D = numericScores;
        evaluation.scores6D = extractScores6D(numericScores);
      }
    }

    const culturalPerspectives = parseJsonField(model.vulca_cultural_perspectives);
    if (culturalPerspectives && typeof culturalPerspectives === 'object' && Object.keys(culturalPerspectives).length > 0) {
      const perspectives = culturalPerspectives as Record<string, unknown>;
      evaluation.culturalPerspectives = {
        western: typeof perspectives.western === 'number' ? perspectives.western : 0,
        eastern: typeof perspectives.eastern === 'number' ? perspectives.eastern : 0,
        african: typeof perspectives.african === 'number' ? perspectives.african : 0,
        latin_american: typeof perspectives.latin_american === 'number' ? perspectives.latin_american : 0,
        middle_eastern: typeof perspectives.middle_eastern === 'number' ? perspectives.middle_eastern : 0,
        south_asian: typeof perspectives.south_asian === 'number' ? perspectives.south_asian : 0,
        oceanic: typeof perspectives.oceanic === 'number' ? perspectives.oceanic : 0,
        indigenous: typeof perspectives.indigenous === 'number' ? perspectives.indigenous : 0,
      };
    }

    return evaluation;
  }, [extractScores6D, parseJsonField]);

  const getDefaultDimensions = useCallback((scores: VULCAScore47D | null | undefined) => {
    if (!scores || typeof scores !== 'object') return [];

    return Object.keys(scores).map(key => {
      const labelResult = getDimensionLabel(key);
      const properName = labelResult === key
        ? key.replace(/([a-z])([A-Z])/g, '$1 $2').replace(/^[a-z]/, c => c.toUpperCase())
        : labelResult;

      return {
        id: key,
        name: properName,
        description: `${properName} dimension`
      };
    });
  }, []);

  const calculate47DAverage = useCallback((scores: VULCAScore47D | null | undefined) => {
    if (!scores || typeof scores !== 'object') return null;
    const values = Object.values(scores).filter(v => typeof v === 'number');
    if (values.length === 0) return null;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }, []);

  // 定义表格列
  const columns = useMemo(() => [
    // 选择列
    columnHelper.display({
      id: 'select',
      size: 40,
      header: ({ table }) => (
        <div className="px-1">
          <input
            type="checkbox"
            aria-label="Select all rows"
            className="w-4 h-4 rounded border-gray-300 dark:border-gray-600"
            checked={table.getIsAllRowsSelected()}
            onChange={table.getToggleAllRowsSelectedHandler()}
          />
        </div>
      ),
      cell: ({ row }) => (
        <div className="px-1">
          <input
            type="checkbox"
            aria-label={`Select ${row.original.model?.name || 'row'}`}
            className="w-4 h-4 rounded border-gray-300 dark:border-gray-600"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
          />
        </div>
      ),
    }),

    // 排名列
    columnHelper.accessor('rank', {
      header: 'Rank',
      size: 80,
      cell: ({ getValue }) => {
        const rank = getValue();
        const getRankStyle = () => {
          if (rank === 1) return 'bg-gradient-to-r from-[#B8923D] to-[#8F7030] text-white';
          if (rank === 2) return 'bg-gradient-to-r from-gray-300 to-gray-500 text-white';
          if (rank === 3) return 'bg-gradient-to-r from-[#C87F4A] to-[#A06038] text-white';
          return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
        };
        
        return (
          <div className="flex justify-center">
            <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${getRankStyle()}`}>
              {rank <= 3 ? <Trophy className="w-4 h-4" /> : rank}
            </span>
          </div>
        );
      },
    }),

    // 模型信息列
    columnHelper.accessor('model.name', {
      id: 'model',
      header: 'Model',
      size: 250,
      cell: ({ row }) => {
        const model = row.original.model;
        return (
          <RouterLink 
            to={`/model/${model.id}`}
            className="flex items-center gap-3 group hover:text-slate-700 dark:hover:text-slate-500"
          >
            <TableModelAvatar src={model.avatar} name={model.name} />
            <div>
              <div className="font-medium">{model.name}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">{model.organization}</div>
            </div>
          </RouterLink>
        );
      },
      filterFn: (row, columnId, filterValue) => {
        const model = row.original.model;
        const searchLower = filterValue.toLowerCase();
        return model.name.toLowerCase().includes(searchLower) ||
               model.organization.toLowerCase().includes(searchLower);
      },
    }),

    // 综合分数列
    columnHelper.accessor('score', {
      header: 'Overall Score',
      size: 100,
      cell: ({ getValue }) => {
        const value = getValue();
        return (
          <div className="text-center font-semibold text-lg">
            {value != null ? value.toFixed(3) : 'N/A'}
          </div>
        );
      },
    }),

    // 各项指标列
    columnHelper.accessor('model.metrics.rhythm', {
      header: 'Poetry',
      size: 80,
      cell: ({ getValue }) => (
        <div className="text-center">{getValue()}</div>
      ),
    }),

    columnHelper.accessor('model.metrics.composition', {
      header: 'Painting',
      size: 80,
      cell: ({ getValue }) => (
        <div className="text-center">{getValue()}</div>
      ),
    }),

    columnHelper.accessor('model.metrics.narrative', {
      header: 'Narrative',
      size: 80,
      cell: ({ getValue }) => (
        <div className="text-center">{getValue()}</div>
      ),
    }),

    // 胜率列
    columnHelper.accessor('winRate', {
      header: 'Win Rate',
      size: 100,
      cell: ({ getValue }) => {
        const rate = getValue();
        const getColor = () => {
          if (rate >= 70) return 'text-[#5F8A50] dark:text-[#87A878]';
          if (rate >= 50) return 'text-slate-700 dark:text-slate-500';
          return 'text-gray-600 dark:text-gray-400';
        };
        
        return (
          <div className={`text-center font-medium ${getColor()}`}>
            {rate != null ? `${rate.toFixed(1)}%` : 'N/A'}
          </div>
        );
      },
    }),

    // 对战数列
    columnHelper.accessor('battles', {
      header: 'Battles',
      size: 80,
      cell: ({ getValue }) => (
        <div className="text-center">{getValue()}</div>
      ),
    }),

    // 趋势列
    columnHelper.accessor('change', {
      header: 'Trend',
      size: 80,
      cell: ({ getValue }) => {
        const change = getValue();
        if (change === 0) return <Minus className="w-4 h-4 text-gray-400 dark:text-gray-500 mx-auto" />;
        if (change > 0) {
          return (
            <div className="flex items-center justify-center gap-1 text-[#5F8A50] dark:text-[#87A878]">
              <TrendingUp className="w-4 h-4" />
              <span className="text-sm font-medium">{change}</span>
            </div>
          );
        }
        return (
          <div className="flex items-center justify-center gap-1 text-red-600 dark:text-red-400">
            <TrendingDown className="w-4 h-4" />
            <span className="text-sm font-medium">{Math.abs(change)}</span>
          </div>
        );
      },
    }),

    // 操作列
    columnHelper.display({
      id: 'actions',
      size: 150,
      header: '',
      cell: ({ row }) => {
        const modelId = row.original.model.id;
        const hasVulca = row.original.model.vulca_scores_47d != null;
        const isExpanded = expandedVulcaModels.has(modelId);
        
        return (
          <div className="flex items-center justify-center gap-2">
            {hasVulca && onToggleVulca && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleVulca(modelId);
                }}
                className="px-2 py-1 text-sm bg-amber-700 dark:bg-amber-600 text-white rounded-lg hover:bg-[#C87F4A] dark:hover:bg-amber-700 transition-colors flex items-center gap-1"
                title="View VULCA 47D Analysis"
              >
                47D
                {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </button>
            )}
            <RouterLink
              to={`/model/${modelId}`}
              className="px-3 py-1 text-sm bg-slate-700 dark:bg-slate-600 text-white rounded-lg hover:bg-slate-700 dark:hover:bg-slate-700 transition-colors"
            >
              View
            </RouterLink>
          </div>
        );
      },
    }),
  ], [expandedVulcaModels, onToggleVulca]);

  // 创建表格实例
  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  // 获取选中的行
  const selectedRows = table.getFilteredSelectedRowModel().rows;

  return (
    <div className="w-full space-y-4">
      {/* 工具栏 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 p-4 ios-glass liquid-glass-container rounded-lg border border-gray-200 dark:border-gray-700">
        {/* 搜索框 */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          <input
            type="text"
            aria-label="Search models"
            placeholder="Search models..."
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="px-3 py-2 ios-glass backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-600/40 focus:border-slate-600 dark:focus:border-slate-500"
          />
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-2">
          {selectedRows.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-2 px-3 py-1 bg-slate-50 dark:bg-slate-900/20 rounded-lg"
            >
              <span className="text-sm text-slate-700 dark:text-slate-500">
                {selectedRows.length} items selected
              </span>
              <button
                disabled
                className="text-sm text-slate-400 dark:text-slate-600 cursor-not-allowed"
                title="Compare feature coming soon"
              >
                Compare
              </button>
            </motion.div>
          )}

          {/* 导出按钮 */}
          <div className="relative group">
            <button className="flex items-center gap-2 px-3 py-2 min-h-[44px] bg-gray-100 dark:bg-[#1A1614] rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2 transition-colors">
              <Download className="w-4 h-4" />
              <span className="text-sm">Export</span>
            </button>
            <div className="absolute right-0 mt-2 w-32 ios-glass backdrop-blur-md border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
              <button
                onClick={() => exportData(data, 'csv')}
                className="w-full px-3 py-2 min-h-[44px] text-sm text-left hover:bg-gray-100/30 dark:hover:bg-gray-800 focus:outline-none focus:bg-gray-100/50 dark:focus:bg-gray-800 transition-colors flex items-center"
              >
                Export as CSV
              </button>
              <button
                onClick={() => exportData(data, 'json')}
                className="w-full px-3 py-2 min-h-[44px] text-sm text-left hover:bg-gray-100/30 dark:hover:bg-gray-800 focus:outline-none focus:bg-gray-100/50 dark:focus:bg-gray-800 transition-colors flex items-center"
              >
                Export as JSON
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 表格 */}
      <div className="leaderboard-table overflow-x-auto ios-glass liquid-glass-container rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="w-full">
          <caption className="sr-only">AI Models Rankings with scores and metrics</caption>
          <thead className="ios-glass backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
            {table.getHeaderGroups().map(headerGroup => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map(header => (
                  <th
                    key={header.id}
                    scope="col"
                    className="px-4 py-3 text-left text-sm font-medium text-gray-700 dark:text-gray-300"
                    style={{ width: header.getSize() }}
                  >
                    {header.isPlaceholder ? null : (
                      <div
                        className={
                          header.column.getCanSort()
                            ? 'cursor-pointer select-none flex items-center gap-1 hover:text-gray-900 dark:hover:text-gray-100'
                            : ''
                        }
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {header.column.getCanSort() && (
                          <>
                            {header.column.getIsSorted() === 'asc' && <ChevronUp className="w-4 h-4" />}
                            {header.column.getIsSorted() === 'desc' && <ChevronDown className="w-4 h-4" />}
                            {!header.column.getIsSorted() && <ChevronsUpDown className="w-4 h-4 opacity-30" />}
                          </>
                        )}
                      </div>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-8">
                  <div className="inline-flex items-center gap-2 text-gray-500 dark:text-gray-400">
                    <div className="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 border-t-slate-700 dark:border-t-slate-500 rounded-full animate-spin" />
                    Loading...
                  </div>
                </td>
              </tr>
            ) : table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No data
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map(row => {
                const modelId = row.original.model.id;
                const isExpanded = expandedVulcaModels?.has(modelId);
                const hasVulcaData = row.original.model.vulca_scores_47d != null;
                
                return (
                  <React.Fragment key={row.id}>
                    <tr 
                      className="hover:bg-gray-100/20 dark:hover:bg-gray-900 transition-colors cursor-pointer"
                      onClick={(e) => {
                        // 防止点击47D按钮时触发行点击
                        if (!(e.target as HTMLElement).closest('button')) {
                          onRowClick?.(row.original);
                        }
                      }}
                    >
                      {row.getVisibleCells().map(cell => (
                        <td 
                          key={cell.id}
                          className="px-4 py-3 text-sm text-gray-900 dark:text-gray-100"
                        >
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                    
                    {/* VULCA展开行 */}
                    {isExpanded && hasVulcaData && (
                      <tr className="vulca-visualization">
                        <td colSpan={columns.length} className="p-0">
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.3 }}
                            className="bg-gray-50 dark:bg-[#0F0D0C] border-t border-gray-200 dark:border-gray-700"
                          >
                            <div className="p-6">
                              <Suspense fallback={
                                <div className="flex items-center justify-center py-8">
                                  <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                                    <div className="w-4 h-4 border-2 border-gray-300 dark:border-gray-600 border-t-slate-700 dark:border-t-slate-500 rounded-full animate-spin" />
                                    Loading VULCA Analysis...
                                  </div>
                                </div>
                              }>
                                <VULCADataDisplay
                                  model={row.original.model}
                                  score={row.original.score}
                                  convertToEvaluation={convertToEvaluation}
                                  getDefaultDimensions={getDefaultDimensions}
                                  calculate47DAverage={calculate47DAverage}
                                />
                                    
                              </Suspense>
                            </div>
                          </motion.div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* 分页控制 */}
      <div className="flex flex-col sm:flex-row justify-between items-center gap-4 px-4">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} - {Math.min((table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize, data.length)} of {data.length}
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
            className="p-2.5 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronsLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="p-2.5 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          
          <span className="px-3 text-sm">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
          </span>
          
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="p-2.5 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
            className="p-2.5 min-w-[44px] min-h-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
