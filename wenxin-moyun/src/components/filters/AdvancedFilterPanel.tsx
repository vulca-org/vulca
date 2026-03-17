import React, { useState, useRef, useEffect } from 'react';
import { Filter, ChevronDown, X, SlidersHorizontal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import MultiSelect from './MultiSelect';
import RangeSlider from './RangeSlider';
import DateRangePicker from './DateRangePicker';
import WeightSlider from './WeightSlider';
import { FilterTagGroup } from './FilterTag';

interface FilterConfig {
  organizations: string[];
  tags: string[];
  categories: string[];
}

interface FilterValues {
  organizations: string[];
  tags: string[];
  categories: string[];
  scoreRange: [number, number];
  winRateRange: [number, number];
  dateRange: [Date | null, Date | null];
  weights: Array<{
    name: string;
    key: string;
    value: number;
    color: string;
  }>;
}

interface AdvancedFilterPanelProps {
  config: FilterConfig;
  values: FilterValues;
  onChange: (values: FilterValues) => void;
  onReset?: () => void;
}

export default function AdvancedFilterPanel({
  config,
  values,
  onChange,
  onReset
}: AdvancedFilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'basic' | 'advanced' | 'weights'>('basic');
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const handleChange = <K extends keyof FilterValues>(key: K, value: FilterValues[K]) => {
    onChange({
      ...values,
      [key]: value
    });
  };

  const resetFilters = () => {
    if (onReset) {
      onReset();
    } else {
      onChange({
        organizations: [],
        tags: [],
        categories: [],
        scoreRange: [0, 100],
        winRateRange: [0, 100],
        dateRange: [null, null],
        weights: values.weights.map(w => ({ ...w, value: 100 / values.weights.length }))
      });
    }
    setIsOpen(false);
  };

  // 计算活动筛选数量
  const activeFilterCount = [
    values.organizations.length > 0,
    values.tags.length > 0,
    values.categories.length > 0,
    values.scoreRange[0] > 0 || values.scoreRange[1] < 100,
    values.winRateRange[0] > 0 || values.winRateRange[1] < 100,
    values.dateRange[0] !== null || values.dateRange[1] !== null,
    values.weights.some(w => Math.abs(w.value - 100 / values.weights.length) > 1)
  ].filter(Boolean).length;

  // 生成筛选标签数据
  const filterTags = [];
  if (values.organizations.length > 0) {
    filterTags.push({
      id: 'orgs',
      label: 'Organizations',
      value: values.organizations,
      color: 'slate' as const
    });
  }
  if (values.tags.length > 0) {
    filterTags.push({
      id: 'tags',
      label: 'Tags',
      value: values.tags,
      color: 'green' as const
    });
  }
  if (values.scoreRange[0] > 0 || values.scoreRange[1] < 100) {
    filterTags.push({
      id: 'score',
      label: 'Score',
      value: `${values.scoreRange[0]}-${values.scoreRange[1]}`,
      color: 'amber' as const
    });
  }

  const tabs = [
    { id: 'basic', label: 'Basic Filters', icon: Filter },
    { id: 'advanced', label: 'Advanced Filters', icon: SlidersHorizontal },
    { id: 'weights', label: 'Weight Adjustment', icon: SlidersHorizontal }
  ] as const;

  return (
    <div className="relative" ref={panelRef}>
      {/* 触发按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
          ${isOpen || activeFilterCount > 0
            ? 'bg-slate-600 text-white shadow-lg'
            : 'bg-white dark:bg-[#1A1614] text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }
        `}
      >
        <Filter className="w-4 h-4" />
        <span>Filter</span>
        {activeFilterCount > 0 && (
          <span className="ml-1 px-1.5 py-0.5 bg-neutral-50/20 rounded-full text-xs">
            {activeFilterCount}
          </span>
        )}
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* 筛选标签 */}
      {!isOpen && filterTags.length > 0 && (
        <div className="absolute top-full left-0 mt-2 z-40">
          <FilterTagGroup
            tags={filterTags}
            onRemove={(id) => {
              if (id === 'orgs') handleChange('organizations', []);
              if (id === 'tags') handleChange('tags', []);
              if (id === 'score') handleChange('scoreRange', [0, 100]);
            }}
            onClearAll={resetFilters}
          />
        </div>
      )}

      {/* 筛选面板 */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full left-0 mt-2 w-96 bg-white dark:bg-[#1A1614] border border-gray-200 dark:border-gray-700 rounded-lg shadow-xl z-50"
          >
            {/* 面板头部 */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Advanced Filters
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* 标签栏 */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium transition-all
                    ${activeTab === tab.id
                      ? 'text-slate-700 dark:text-slate-500 border-b-2 border-slate-700 dark:border-slate-500'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300'
                    }
                  `}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* 面板内容 */}
            <div className="p-4 max-h-96 overflow-y-auto">
              <AnimatePresence mode="wait">
                {activeTab === 'basic' && (
                  <motion.div
                    key="basic"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="space-y-4"
                  >
                    <MultiSelect
                      label="Organizations"
                      options={config.organizations}
                      value={values.organizations}
                      onChange={(value) => handleChange('organizations', value)}
                      placeholder="Select organizations..."
                    />
                    
                    <MultiSelect
                      label="Tags"
                      options={config.tags}
                      value={values.tags}
                      onChange={(value) => handleChange('tags', value)}
                      placeholder="Select tags..."
                    />
                    
                    <MultiSelect
                      label="Categories"
                      options={config.categories}
                      value={values.categories}
                      onChange={(value) => handleChange('categories', value)}
                      placeholder="Select categories..."
                    />
                  </motion.div>
                )}

                {activeTab === 'advanced' && (
                  <motion.div
                    key="advanced"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="space-y-4"
                  >
                    <RangeSlider
                      label="Score Range"
                      min={0}
                      max={100}
                      value={values.scoreRange}
                      onChange={(value) => handleChange('scoreRange', value)}
                      step={5}
                    />
                    
                    <RangeSlider
                      label="Win Rate Range"
                      min={0}
                      max={100}
                      value={values.winRateRange}
                      onChange={(value) => handleChange('winRateRange', value)}
                      step={5}
                      unit="%"
                    />
                    
                    <DateRangePicker
                      label="Update Time"
                      value={values.dateRange}
                      onChange={(value) => handleChange('dateRange', value)}
                      placeholder="Select time range..."
                    />
                  </motion.div>
                )}

                {activeTab === 'weights' && (
                  <motion.div
                    key="weights"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="space-y-4"
                  >
                    <WeightSlider
                      label="Ability Weight Adjustment"
                      weights={values.weights}
                      onChange={(weights) => handleChange('weights', weights)}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* 面板底部 */}
            <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={resetFilters}
                className="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300 transition-colors"
              >
                Reset All Filters
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-1.5 bg-slate-600 text-white text-sm font-medium rounded-lg hover:bg-slate-700 transition-colors"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
