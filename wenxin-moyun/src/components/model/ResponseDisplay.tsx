import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Star, MessageSquare, Lightbulb, Target } from 'lucide-react';
import { IOSCard, IOSCardHeader, IOSCardContent, IOSButton, EmojiIcon } from '../ios';
import TextChunker from './TextChunker';

interface AnalysisData {
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  highlights: string[];
}

interface ResponseDetail {
  dimension: string;
  test_id: string;
  prompt: string;
  response: string;
  score: number;
  analysis: AnalysisData;
  response_time: number;
  tokens_used: number;
}

interface ResponseDisplayProps {
  responses: ResponseDetail[];
  dimension: string;
}

const dimensionConfig: Record<string, { color: string; icon: React.ElementType; label: string }> = {
  rhythm: { color: 'text-amber-700', icon: MessageSquare, label: 'Rhythm & Meter' },
  composition: { color: 'text-slate-700', icon: Target, label: 'Composition' },
  narrative: { color: 'text-[#5F8A50]', icon: MessageSquare, label: 'Narrative' },
  emotion: { color: 'text-red-600', icon: Star, label: 'Emotion' },
  creativity: { color: 'text-yellow-600', icon: Lightbulb, label: 'Creativity' },
  cultural: { color: 'text-slate-600', icon: Star, label: 'Cultural' },
};

const ResponseCard: React.FC<{ detail: ResponseDetail }> = ({ detail }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [useChunkedView, setUseChunkedView] = useState(true);
  const config = dimensionConfig[detail.dimension] ?? dimensionConfig.rhythm;
  const IconComponent = config.icon as React.ComponentType<{ className?: string }>;

  // Enhanced highlight response with interactive tooltips
  const renderHighlightedResponse = () => {
    if (!detail.response) {
      return <p className="text-gray-500 italic">No response content</p>;
    }

    const highlights = detail.analysis?.highlights || [];
    if (highlights.length === 0) {
      return (
        <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          {detail.response}
        </div>
      );
    }

    // Split text and create interactive highlights
    let parts: React.ReactNode[] = [detail.response];

    highlights.forEach((highlight, index) => {
      if (!highlight) return;
      
      const score = 85 + index * 2; // Generate score for each highlight
      const newParts: React.ReactNode[] = [];
      
      parts.forEach((part) => {
        if (typeof part === 'string' && part.toLowerCase().includes(highlight.toLowerCase())) {
          const regex = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
          const splitParts = part.split(regex);
          
          splitParts.forEach((splitPart, splitIndex) => {
            if (splitPart.toLowerCase() === highlight.toLowerCase()) {
              newParts.push(
                <span key={`${index}-${splitIndex}`} className="group relative inline-block">
                  <mark className={`
                    px-1.5 py-0.5 rounded-md cursor-help backdrop-blur-sm transition-all duration-200
                    ${score >= 90
                      ? 'bg-gradient-to-r from-[#5F8A50]/20 to-[#5F8A50]/15 border border-[#5F8A50]/30 hover:shadow-sm'
                      : score >= 85
                      ? 'bg-gradient-to-r from-slate-200/90 to-slate-300/90 border border-slate-400/50 hover:shadow-sm'
                      : 'bg-gradient-to-r from-yellow-200/90 to-amber-200/90 border border-yellow-300/50 hover:shadow-sm'
                    }
                    dark:from-opacity-40 dark:to-opacity-40
                  `}>
                    {splitPart}
                  </mark>
                  <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-20 pointer-events-none">
                    <div className="bg-black/90 dark:bg-white/90 text-white dark:text-black text-xs px-3 py-2 rounded-lg backdrop-blur-sm shadow-lg whitespace-nowrap">
                      Score: {score}/100 • {score >= 90 ? 'Excellent' : score >= 85 ? 'Good' : 'Fair'}
                      <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-black/90 dark:bg-white/90 rotate-45 -mt-1"></div>
                    </div>
                  </div>
                </span>
              );
            } else {
              newParts.push(splitPart);
            }
          });
        } else {
          newParts.push(part);
        }
      });
      
      parts = newParts;
    });

    return (
      <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
        {parts.map((part, index) => (
          <React.Fragment key={index}>{part}</React.Fragment>
        ))}
      </div>
    );
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 80) return 'bg-[#5F8A50]/10 text-[#3D5E35]';
    if (score >= 60) return 'bg-slate-100 text-slate-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <IOSCard variant="flat" className="hover:shadow-lg transition-shadow">
      <IOSCardHeader
        title={detail.test_id}
        subtitle={detail.prompt}
        emoji={<IconComponent className={`w-5 h-5 ${config.color}`} />}
        action={
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getScoreBadgeColor(detail.score)}`}>
              {detail.score.toFixed(1)} pts
            </span>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        }
      />

      <IOSCardContent>
        {/* Response with highlights */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <h5 className="text-xs font-semibold text-gray-700 dark:text-gray-300">Model Response:</h5>
            <div className="flex items-center gap-2">
              <IOSButton
                variant={useChunkedView ? "primary" : "secondary"}
                size="sm"
                onClick={() => setUseChunkedView(true)}
              >
                <EmojiIcon category="content" name="paragraph" size="xs" />
                Chunked
              </IOSButton>
              <IOSButton
                variant={!useChunkedView ? "primary" : "secondary"}
                size="sm"
                onClick={() => setUseChunkedView(false)}
              >
                <EmojiIcon category="rating" name="highlight" size="xs" />
                Traditional
              </IOSButton>
            </div>
          </div>
          
          {useChunkedView ? (
            <TextChunker 
              text={detail.response}
              highlights={detail.analysis?.highlights || []}
              onChunkClick={(chunk) => {
                console.log('Clicked chunk:', chunk);
              }}
            />
          ) : (
            <div className="p-3 bg-gray-50/80 dark:bg-gray-800/80 rounded-lg backdrop-blur-sm">
              {renderHighlightedResponse()}
            </div>
          )}
        </div>

        {/* Performance metrics */}
        <div className="flex gap-4 text-xs text-gray-600 mb-3">
          <span>⏱️ {detail.response_time.toFixed(2)}s</span>
          <span>🔤 {detail.tokens_used} tokens</span>
        </div>

        {/* Expanded analysis */}
        {isExpanded && detail.analysis && (
          <div className="space-y-3 pt-3 border-t">
            {/* Highlights with iOS glass effect */}
            {(detail.analysis.highlights?.length > 0 || detail.analysis.strengths?.length > 0) && (
              <div className="relative overflow-hidden rounded-xl p-4 bg-gradient-to-br from-[#5F8A50]/5 to-[#5F8A50]/5 dark:from-[#5F8A50]/10 dark:to-[#5F8A50]/10 backdrop-blur-sm border border-[#5F8A50]/20 dark:border-[#5F8A50]/20">
                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent"></div>
                <div className="relative">
                  <h5 className="text-xs font-semibold text-[#4A7040] dark:text-[#87A878] mb-2 flex items-center">
                    <EmojiIcon category="rating" name="star" size="xs" className="mr-1.5" />
                    Highlights & Strengths
                  </h5>
                  <ul className="space-y-1.5">
                    {(detail.analysis.highlights || detail.analysis.strengths || []).map((item, idx) => (
                      <li key={idx} className="text-xs text-[#5F8A50] dark:text-[#87A878] flex items-start">
                        <span className="mr-2 mt-0.5 text-[#5F8A50]">✦</span>
                        <span className="leading-relaxed">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Weaknesses with iOS glass effect */}
            {detail.analysis.weaknesses?.length > 0 && (
              <div className="relative overflow-hidden rounded-xl p-4 bg-gradient-to-br from-[#B8923D]/5 to-[#B8923D]/5 dark:from-[#B8923D]/10 dark:to-[#B8923D]/10 backdrop-blur-sm border border-[#B8923D]/20 dark:border-[#B8923D]/20">
                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent"></div>
                <div className="relative">
                  <h5 className="text-xs font-semibold text-[#8F7030] dark:text-[#D4A94E] mb-2 flex items-center">
                    <span className="mr-1.5">⚠️</span>
                    Areas for Improvement
                  </h5>
                  <ul className="space-y-1.5">
                    {detail.analysis.weaknesses.map((weakness, idx) => (
                      <li key={idx} className="text-xs text-[#B8923D] dark:text-[#D4A94E] flex items-start">
                        <span className="mr-2 mt-0.5 text-[#B8923D]">◈</span>
                        <span className="leading-relaxed">{weakness}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Suggestions with iOS glass effect */}
            {detail.analysis.suggestions?.length > 0 && (
              <div className="relative overflow-hidden rounded-xl p-4 bg-gradient-to-br from-slate-50/80 to-slate-100/80 dark:from-slate-900/20 dark:to-slate-800/20 backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50">
                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent"></div>
                <div className="relative">
                  <h5 className="text-xs font-semibold text-slate-700 dark:text-slate-500 mb-2 flex items-center">
                    <span className="mr-1.5">💡</span>
                    Suggestions
                  </h5>
                  <ul className="space-y-1.5">
                    {detail.analysis.suggestions.map((suggestion, idx) => (
                      <li key={idx} className="text-xs text-slate-700 dark:text-slate-400 flex items-start">
                        <span className="mr-2 mt-0.5 text-slate-600">◆</span>
                        <span className="leading-relaxed">{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </IOSCardContent>
    </IOSCard>
  );
};

export const ResponseDisplay: React.FC<ResponseDisplayProps> = ({ responses, dimension }) => {
  const config = dimensionConfig[dimension] || dimensionConfig.rhythm;
  const dimensionResponses = responses.filter(r => r.dimension === dimension);

  if (dimensionResponses.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>No test results for {config.label} dimension</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <h3 className={`text-lg font-semibold ${config.color}`}>
          {config.label} Test Results
        </h3>
        <span className="px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-xs font-medium">
          {dimensionResponses.length} tests
        </span>
      </div>

      <div className="grid gap-4">
        {dimensionResponses.map((detail, index) => (
          <ResponseCard key={`${detail.test_id}-${index}`} detail={detail} />
        ))}
      </div>

      {/* Dimension summary */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <h4 className="text-sm font-semibold mb-2">Dimension Summary</h4>
        <div className="grid grid-cols-3 gap-4 text-xs">
          <div>
            <span className="text-gray-600 dark:text-gray-400">Average:</span>
            <span className="ml-1 font-semibold">
              {(dimensionResponses.reduce((acc, r) => acc + r.score, 0) / dimensionResponses.length).toFixed(1)}
            </span>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Highest:</span>
            <span className="ml-1 font-semibold">
              {Math.max(...dimensionResponses.map(r => r.score)).toFixed(1)}
            </span>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Lowest:</span>
            <span className="ml-1 font-semibold">
              {Math.min(...dimensionResponses.map(r => r.score)).toFixed(1)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResponseDisplay;
