import { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Trophy, Zap, Users, ChevronRight, Star } from 'lucide-react';
import RouterLink from '../common/RouterLink';
import type { LeaderboardEntry } from '../../types/types';

interface LeaderboardCardProps {
  entry: LeaderboardEntry;
  index: number;
  viewMode: 'card' | 'compact' | 'detailed';
  onHover?: (entry: LeaderboardEntry | null) => void;
}

/** Renders model avatar with a letter fallback when the image is missing or fails to load. */
function ModelAvatar({ src, name, size = 'md' }: { src?: string; name: string; size?: 'sm' | 'md' }) {
  const [failed, setFailed] = useState(false);
  const sizeClass = size === 'sm' ? 'w-10 h-10' : 'w-12 h-12';
  const textSize = size === 'sm' ? 'text-sm' : 'text-base';

  if (!src || failed) {
    return (
      <div className={`${sizeClass} rounded-lg bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300 font-semibold ${textSize} select-none`}>
        {name.charAt(0).toUpperCase()}
      </div>
    );
  }
  return (
    <img
      src={src}
      alt={name}
      className={`${sizeClass} rounded-lg object-cover shadow-sm`}
      onError={() => setFailed(true)}
    />
  );
}

export default function LeaderboardCard({ entry, index, viewMode, onHover }: LeaderboardCardProps) {
  const getRankStyle = (rank: number) => {
    if (rank === 1) return 'bg-gradient-to-r from-[#B8923D] via-[#A0802E] to-[#8F7030] text-white';
    if (rank === 2) return 'bg-gradient-to-r from-gray-300 via-gray-400 to-gray-500 text-white';
    if (rank === 3) return 'bg-gradient-to-r from-[#C87F4A] via-[#B46B3C] to-[#A06038] text-white';
    return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-4 h-4 text-[#5F8A50]" />;
    if (change < 0) return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-gray-400 dark:text-gray-500" />;
  };


  if (viewMode === 'compact') {
    return (
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.03 }}
        className="flex items-center justify-between p-3 ios-glass liquid-glass-container rounded-lg hover:shadow-md transition-all"
        onMouseEnter={() => onHover?.(entry)}
        onMouseLeave={() => onHover?.(null)}
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${getRankStyle(entry.rank)}`}>
            {entry.rank}
          </div>
          <ModelAvatar src={entry.model.avatar} name={entry.model.name} size="sm" />
          <div>
            <h4 className="font-semibold text-gray-800 dark:text-gray-200">{entry.model.name}</h4>
            <p className="text-xs text-gray-500 dark:text-gray-400">{entry.model.organization}</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-lg font-bold text-slate-700">{entry.score != null ? entry.score.toFixed(3) : 'N/A'}</span>
          {getTrendIcon(entry.change)}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      className={`
        ios-glass liquid-glass-container rounded-xl shadow-lg overflow-hidden
        hover:shadow-2xl transition-all duration-300 cursor-pointer
        ${viewMode === 'detailed' ? 'p-6' : 'p-4'}
      `}
      onMouseEnter={() => onHover?.(entry)}
      onMouseLeave={() => onHover?.(null)}
    >
      {/* Card Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            {/* Rank Badge */}
            <div className={`
              ${entry.rank <= 3 ? 'w-12 h-12' : 'w-10 h-10'}
              rounded-xl flex items-center justify-center font-bold shadow-md
              ${getRankStyle(entry.rank)}
            `}>
              {entry.rank <= 3 ? (
                <Trophy className="w-6 h-6" />
              ) : (
                <span className="text-lg">{entry.rank}</span>
              )}
            </div>
            
            {/* Model Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <ModelAvatar src={entry.model.avatar} name={entry.model.name} size="md" />
                <div>
                  <h3 className="font-bold text-lg text-gray-800 dark:text-gray-200">
                    {entry.model.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {entry.model.organization}
                  </p>
                </div>
              </div>
            </div>

            {/* Trend Indicator */}
            <div className="flex items-center gap-1">
              {getTrendIcon(entry.change)}
              {entry.change !== 0 && (
                <span className={`text-xs font-medium ${
                  entry.change > 0 ? 'text-[#5F8A50]' : 'text-red-500'
                }`}>
                  {Math.abs(entry.change)}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Score Display */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center p-3 ios-glass rounded-lg">
            <div className="text-2xl font-bold text-slate-700 dark:text-slate-300">
              {entry.score != null ? entry.score.toFixed(3) : 'N/A'}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
              <Star className="w-3 h-3" />
              Overall Score
            </div>
          </div>
          
          <div className="text-center p-3 ios-glass rounded-lg">
            <div className="text-2xl font-bold text-[#5F8A50] dark:text-[#87A878]">
              {entry.winRate != null ? `${entry.winRate.toFixed(0)}%` : 'N/A'}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
              <Zap className="w-3 h-3" />
              Win Rate
            </div>
          </div>
          
          <div className="text-center p-3 ios-glass rounded-lg">
            <div className="text-2xl font-bold text-slate-700 dark:text-slate-500">
              {entry.battles}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400 flex items-center justify-center gap-1">
              <Users className="w-3 h-3" />
              Battles
            </div>
          </div>
        </div>

        {/* Win Rate Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
            <span>Win Rate Distribution</span>
            <span>{entry.winRate != null ? `${entry.winRate.toFixed(1)}%` : 'N/A'}</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
            <motion.div
              initial={{ width: '0%' }}
              animate={{ width: `${entry.winRate}%` }}
              transition={{ delay: index * 0.05 + 0.2, duration: 0.8 }}
              className="h-full bg-[#5F8A50] rounded-full"
            />
          </div>
        </div>

        {/* Tags */}
        {viewMode === 'detailed' && (
          <div className="flex flex-wrap gap-2 mb-4">
            {entry.model.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Metrics Preview (for detailed view) */}
        {viewMode === 'detailed' && (
          <div className="grid grid-cols-3 gap-2 mb-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            {Object.entries({
              'Rhythm': entry.model.metrics.rhythm,
              'Composition': entry.model.metrics.composition,
              'Narrative': entry.model.metrics.narrative,
            }).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="text-xs text-gray-500 dark:text-gray-400">{key}</div>
                <div className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  {value}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action Button */}
        <RouterLink
          to={`/model/${entry.model.id}`}
          className="flex items-center justify-center gap-2 w-full py-2 bg-slate-700 hover:bg-slate-800 text-white rounded-lg transition-all duration-200 transform hover:scale-[1.02]"
        >
          <span className="text-sm font-medium">View Details</span>
          <ChevronRight className="w-4 h-4" />
        </RouterLink>
    </motion.div>
  );
}