/**
 * ProvenanceCard - Data Provenance Information Card
 *
 * Displays metadata about data source, version, license, and evaluation details
 *
 * @module components/trustlayer/ProvenanceCard
 */

import React from 'react';
import { motion } from 'framer-motion';
import {
  Database,
  Calendar,
  Shield,
  ExternalLink,
  Clock,
  Tag,
  GitBranch,
  FileCode,
} from 'lucide-react';
import { IOSCard } from '../ios';

interface ProvenanceCardProps {
  /** Data source name */
  source: string;
  /** Version string (e.g., "1.0.0") */
  version: string;
  /** Last updated date (ISO string or formatted) */
  lastUpdated: string;
  /** License identifier (e.g., "CC-BY-NC-SA 4.0") */
  license: string;
  /** DOI identifier (optional) */
  doi?: string;
  /** Algorithm name/version (optional) */
  algorithm?: string;
  /** Evaluation date (optional) */
  evaluationDate?: string;
  /** GitHub repository URL (optional) */
  github?: string;
  /** Paper citation URL (optional) */
  paperUrl?: string;
  /** Additional CSS classes */
  className?: string;
  /** Compact mode for smaller displays */
  compact?: boolean;
}

export const ProvenanceCard: React.FC<ProvenanceCardProps> = ({
  source,
  version,
  lastUpdated,
  license,
  doi,
  algorithm,
  evaluationDate,
  github,
  paperUrl,
  className = '',
  compact = false,
}) => {
  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  const InfoItem: React.FC<{
    icon: React.ReactNode;
    label: string;
    value: string;
    link?: string;
  }> = ({ icon, label, value, link }) => (
    <div className={`flex items-start gap-2 ${compact ? 'py-1' : 'py-2'}`}>
      <span className="text-gray-400 dark:text-gray-500 mt-0.5">{icon}</span>
      <div className="min-w-0">
        <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
        {link ? (
          <a
            href={link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-slate-600 hover:underline flex items-center gap-1"
          >
            {value}
            <ExternalLink className="w-3 h-3" />
          </a>
        ) : (
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {value}
          </p>
        )}
      </div>
    </div>
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <IOSCard variant="elevated" className={className}>
        <div className={compact ? 'p-3' : 'p-4'}>
          {/* Header */}
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-200 dark:border-gray-700">
            <Database className="w-5 h-5 text-slate-600" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Data Provenance
            </h3>
          </div>

          {/* Info Grid */}
          <div
            className={`grid ${
              compact ? 'grid-cols-2 gap-x-4' : 'grid-cols-2 md:grid-cols-3 gap-x-6'
            }`}
          >
            <InfoItem
              icon={<Tag className="w-4 h-4" />}
              label="Source"
              value={source}
            />
            <InfoItem
              icon={<GitBranch className="w-4 h-4" />}
              label="Version"
              value={version}
            />
            <InfoItem
              icon={<Calendar className="w-4 h-4" />}
              label="Last Updated"
              value={formatDate(lastUpdated)}
            />
            <InfoItem
              icon={<Shield className="w-4 h-4" />}
              label="License"
              value={license}
            />
            {algorithm && (
              <InfoItem
                icon={<FileCode className="w-4 h-4" />}
                label="Algorithm"
                value={algorithm}
              />
            )}
            {evaluationDate && (
              <InfoItem
                icon={<Clock className="w-4 h-4" />}
                label="Evaluated"
                value={formatDate(evaluationDate)}
              />
            )}
          </div>

          {/* Links Section */}
          {(doi || github || paperUrl) && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 flex flex-wrap gap-3">
              {doi && (
                <a
                  href={`https://doi.org/${doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-slate-600 hover:underline flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  DOI: {doi}
                </a>
              )}
              {github && (
                <a
                  href={github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-slate-600 hover:underline flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  GitHub
                </a>
              )}
              {paperUrl && (
                <a
                  href={paperUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-slate-600 hover:underline flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  Paper
                </a>
              )}
            </div>
          )}
        </div>
      </IOSCard>
    </motion.div>
  );
};

export default ProvenanceCard;
