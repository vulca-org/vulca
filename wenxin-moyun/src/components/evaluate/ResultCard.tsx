import { motion } from 'framer-motion';
import { Shield, AlertTriangle, CheckCircle2, Lightbulb } from 'lucide-react';
import { IOSCard, IOSCardContent } from '../ios';

export interface EvaluationResult {
  score: number;
  summary: string;
  riskLevel: 'low' | 'medium' | 'high';
  dimensions: { name: string; score: number }[];
  recommendations: string[];
  traditionUsed: string;
}

interface ResultCardProps {
  result: EvaluationResult;
}

const riskConfig = {
  low: {
    label: 'Low Risk',
    color: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    icon: CheckCircle2,
  },
  medium: {
    label: 'Medium Risk',
    color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    icon: AlertTriangle,
  },
  high: {
    label: 'High Risk',
    color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    icon: Shield,
  },
};

function getScoreColor(score: number): string {
  if (score > 0.7) return 'text-green-600 dark:text-green-400';
  if (score > 0.5) return 'text-orange-500 dark:text-orange-400';
  return 'text-red-500 dark:text-red-400';
}

function getBarColor(score: number): string {
  if (score > 0.7) return 'bg-green-500';
  if (score > 0.5) return 'bg-orange-400';
  return 'bg-red-500';
}

export const ResultCard: React.FC<ResultCardProps> = ({ result }) => {
  const risk = riskConfig[result.riskLevel];
  const RiskIcon = risk.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
    >
      <IOSCard variant="elevated" padding="lg">
        <IOSCardContent>
          {/* Score + Risk header */}
          <div className="flex items-start justify-between mb-6">
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                Overall Score
              </p>
              <span className={`text-5xl font-bold tracking-tight ${getScoreColor(result.score)}`}>
                {result.score.toFixed(2)}
              </span>
            </div>

            <span
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-full ${risk.color}`}
            >
              <RiskIcon className="w-3.5 h-3.5" />
              {risk.label}
            </span>
          </div>

          {/* Summary */}
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
            {result.summary}
          </p>

          {/* Dimension scores */}
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
              Dimension Scores
            </h4>
            <div className="space-y-2.5">
              {result.dimensions.map((dim) => (
                <div key={dim.name}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      {dim.name}
                    </span>
                    <span className={`text-xs font-semibold ${getScoreColor(dim.score)}`}>
                      {dim.score.toFixed(2)}
                    </span>
                  </div>
                  <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${dim.score * 100}%` }}
                      transition={{ duration: 0.6, delay: 0.2, ease: 'easeOut' }}
                      className={`h-full rounded-full ${getBarColor(dim.score)}`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          {result.recommendations.length > 0 && (
            <div className="mb-5">
              <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-1.5">
                <Lightbulb className="w-4 h-4 text-amber-500" />
                Recommendations
              </h4>
              <ul className="space-y-1.5">
                {result.recommendations.map((rec, i) => (
                  <li
                    key={i}
                    className="text-xs text-gray-600 dark:text-gray-400 pl-4 relative before:content-[''] before:absolute before:left-0 before:top-[7px] before:w-1.5 before:h-1.5 before:rounded-full before:bg-gray-300 dark:before:bg-gray-600"
                  >
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Tradition badge */}
          <div className="pt-4 border-t border-gray-100 dark:border-gray-800">
            <span className="text-xs text-gray-400 dark:text-gray-500 mr-2">Tradition:</span>
            <span className="inline-flex items-center px-2.5 py-1 text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-md">
              {result.traditionUsed}
            </span>
          </div>
        </IOSCardContent>
      </IOSCard>
    </motion.div>
  );
};

export default ResultCard;
