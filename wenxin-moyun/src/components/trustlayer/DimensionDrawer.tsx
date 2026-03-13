/**
 * DimensionDrawer - Dimension Detail Information Drawer
 *
 * Shows detailed information about a dimension when clicked in visualizations
 * Uses IOSSheet for the sliding drawer effect
 *
 * @module components/trustlayer/DimensionDrawer
 */

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Layers, BookOpen, Scale, TrendingUp, Palette, Link2 } from 'lucide-react';
import { IOSSheet, IOSCard } from '../ios';
import {
  dimensionsService,
  type Dimension6D,
  type Dimension47D,
  type DimensionCategory,
} from '../../services/dimensions';

interface DimensionDrawerProps {
  /** Dimension ID or index to display */
  dimensionId: string | number | null;
  /** Whether the drawer is visible */
  visible: boolean;
  /** Callback when drawer is closed */
  onClose: () => void;
}

type DimensionData = {
  dimension: Dimension6D | Dimension47D;
  is47D: boolean;
  category?: DimensionCategory;
  parentDimension?: Dimension6D;
};

export const DimensionDrawer: React.FC<DimensionDrawerProps> = ({
  dimensionId,
  visible,
  onClose,
}) => {
  const [data, setData] = useState<DimensionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!dimensionId) {
      setData(null);
      return;
    }

    const loadDimension = async () => {
      setLoading(true);
      setError(null);

      try {
        await dimensionsService.load();

        // Try to find as 6D dimension first
        const dim6d = dimensionsService.getDimension6D(String(dimensionId));
        if (dim6d) {
          const category = dimensionsService.getCategory(dim6d.id);
          setData({
            dimension: dim6d,
            is47D: false,
            category,
          });
          setLoading(false);
          return;
        }

        // Try to find as 47D dimension
        const dim47d = dimensionsService.getDimension47D(dimensionId);
        if (dim47d) {
          const category = dimensionsService.getCategory(dim47d.category);
          // Find parent 6D dimension
          let parentDimension: Dimension6D | undefined;
          const dims6d = dimensionsService.getAllDimensions6D();
          for (const [, dim] of Object.entries(dims6d)) {
            if (dim.childDimensions.includes(dim47d.index)) {
              parentDimension = dim;
              break;
            }
          }
          setData({
            dimension: dim47d,
            is47D: true,
            category,
            parentDimension,
          });
          setLoading(false);
          return;
        }

        setError(`Dimension "${dimensionId}" not found`);
      } catch (err) {
        setError('Failed to load dimension data');
        console.error('DimensionDrawer load error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDimension();
  }, [dimensionId]);

  const InfoCard: React.FC<{
    icon: React.ReactNode;
    title: string;
    children: React.ReactNode;
  }> = ({ icon, title, children }) => (
    <IOSCard variant="flat" className="p-4">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <h4 className="font-semibold text-gray-900 dark:text-white">{title}</h4>
      </div>
      {children}
    </IOSCard>
  );

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-600" />
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          {error}
        </div>
      );
    }

    if (!data) {
      return (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          Select a dimension to view details
        </div>
      );
    }

    const { dimension, is47D, category, parentDimension } = data;
    const dim47d = is47D ? (dimension as Dimension47D) : null;
    const dim6d = is47D ? null : (dimension as Dimension6D);

    return (
      <div className="space-y-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center pb-4 border-b border-gray-200 dark:border-gray-700"
        >
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {dimension.name}
          </h2>
          <p className="text-lg text-gray-500 dark:text-gray-400">
            {dimension.name_zh}
          </p>
          {is47D && (
            <span className="inline-block mt-2 px-3 py-1 bg-slate-100 dark:bg-slate-900/30 text-slate-700 dark:text-slate-500 rounded-full text-sm">
              47D Sub-dimension
            </span>
          )}
          {!is47D && (
            <span className="inline-block mt-2 px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-500 rounded-full text-sm">
              6D Core Dimension
            </span>
          )}
        </motion.div>

        {/* Description */}
        <InfoCard
          icon={<BookOpen className="w-5 h-5 text-gray-500" />}
          title="Description"
        >
          <p className="text-gray-600 dark:text-gray-400">
            {dimension.description}
          </p>
        </InfoCard>

        {/* Category */}
        {category && (
          <InfoCard
            icon={<Palette className="w-5 h-5" style={{ color: category.color }} />}
            title="Category"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded-full"
                style={{ backgroundColor: category.color }}
              />
              <span className="font-medium text-gray-900 dark:text-white">
                {category.name}
              </span>
              <span className="text-gray-500 dark:text-gray-400">
                ({category.name_zh})
              </span>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {category.description}
            </p>
          </InfoCard>
        )}

        {/* Weight & Range */}
        <div className="grid grid-cols-2 gap-4">
          <InfoCard
            icon={<Scale className="w-5 h-5 text-amber-600" />}
            title="Weight"
          >
            <p className="text-3xl font-bold text-amber-600">
              {(dimension.weight * 100).toFixed(1)}%
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              of total score
            </p>
          </InfoCard>

          {dim6d?.range && (
            <InfoCard
              icon={<TrendingUp className="w-5 h-5 text-green-500" />}
              title="Score Range"
            >
              <p className="text-3xl font-bold text-green-500">
                {dim6d.range[0]} - {dim6d.range[1]}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                points
              </p>
            </InfoCard>
          )}

          {dim47d && (
            <InfoCard
              icon={<TrendingUp className="w-5 h-5 text-green-500" />}
              title="Index"
            >
              <p className="text-3xl font-bold text-green-500">
                #{dim47d.index}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                of 47 dimensions
              </p>
            </InfoCard>
          )}
        </div>

        {/* Parent Dimension (for 47D) */}
        {parentDimension && (
          <InfoCard
            icon={<Layers className="w-5 h-5 text-slate-600" />}
            title="Parent Dimension"
          >
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-slate-600" />
              <span className="font-medium text-gray-900 dark:text-white">
                {parentDimension.name}
              </span>
              <span className="text-gray-500 dark:text-gray-400">
                ({parentDimension.name_zh})
              </span>
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              This is a sub-dimension that contributes to the{' '}
              <strong>{parentDimension.name}</strong> score.
            </p>
          </InfoCard>
        )}

        {/* Child Dimensions (for 6D) */}
        {dim6d?.childDimensions && dim6d.childDimensions.length > 0 && (
          <InfoCard
            icon={<Layers className="w-5 h-5 text-orange-500" />}
            title={`Sub-dimensions (${dim6d.childDimensions.length})`}
          >
            <div className="flex flex-wrap gap-2">
              {dim6d.childDimensions.map(idx => {
                const subDim = dimensionsService.getDimension47D(idx);
                return subDim ? (
                  <span
                    key={idx}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs text-gray-700 dark:text-gray-300"
                  >
                    {subDim.name}
                  </span>
                ) : null;
              })}
            </div>
          </InfoCard>
        )}

        {/* Related Research */}
        <InfoCard
          icon={<Link2 className="w-5 h-5 text-gray-500" />}
          title="Related Research"
        >
          <p className="text-sm text-gray-600 dark:text-gray-400">
            This dimension is defined in the VULCA framework (EMNLP 2025 Findings).
            See the{' '}
            <a
              href="#/research"
              className="text-slate-600 hover:underline"
              onClick={onClose}
            >
              Papers
            </a>{' '}
            page for full methodology and citations.
          </p>
        </InfoCard>
      </div>
    );
  };

  return (
    <IOSSheet
      visible={visible}
      onClose={onClose}
      height="large"
      showHandle
      allowDismiss
    >
      <div className="p-4 pb-8 overflow-y-auto max-h-full">
        {renderContent()}
      </div>
    </IOSSheet>
  );
};

export default DimensionDrawer;
