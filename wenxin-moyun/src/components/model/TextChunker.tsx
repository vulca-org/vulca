import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { EmojiIcon } from '../ios';

interface TextChunk {
  id: string;
  content: string;
  type: 'paragraph' | 'sentence' | 'phrase';
  score?: number;
  isHighlighted: boolean;
  startIndex: number;
  endIndex: number;
}

interface TextChunkerProps {
  text: string;
  highlights: string[];
  onChunkClick?: (chunk: TextChunk) => void;
  className?: string;
}

const ScoreTooltip: React.FC<{ score: number; highlight: string }> = ({ score, highlight }) => (
  <span className="group relative inline-block">
    <mark className="bg-gradient-to-r from-yellow-200/90 to-amber-200/90 dark:from-yellow-600/40 dark:to-amber-600/40 px-1.5 py-0.5 rounded-md cursor-help border border-yellow-300/50 dark:border-yellow-500/30 backdrop-blur-sm">
      {highlight}
    </mark>
    <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 z-10 pointer-events-none">
      <div className="bg-black/90 dark:bg-white/90 text-white dark:text-black text-xs px-3 py-2 rounded-lg backdrop-blur-sm shadow-lg">
        评分: {score}/100
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-2 h-2 bg-black/90 dark:bg-white/90 rotate-45 -mt-1"></div>
      </div>
    </div>
  </span>
);

const getHighlightStyle = (score: number) => {
  // Using iOS system colors: #34C759 (green), #64748B (blue), #FF9500 (orange)
  if (score >= 90) return 'from-[#5F8A50]/10 to-[#5F8A50]/15 border-[#5F8A50]/30 dark:from-[#5F8A50]/15 dark:to-[#5F8A50]/20 dark:border-[#5F8A50]/20'; // 优秀 - Sage Green
  if (score >= 80) return 'from-slate-100/90 to-slate-200/90 border-slate-400/60 dark:from-slate-900/40 dark:to-slate-800/40 dark:border-slate-700/30'; // 良好 - Art Professional Slate
  if (score >= 70) return 'from-[#5F8A50]/5 to-[#5F8A50]/10 border-[#5F8A50]/20 dark:from-[#5F8A50]/10 dark:to-[#5F8A50]/15 dark:border-[#5F8A50]/15'; // 合格 - Light Sage Green
  return 'from-[#B8923D]/10 to-[#B8923D]/15 border-[#B8923D]/30 border-dashed dark:from-[#B8923D]/15 dark:to-[#B8923D]/10 dark:border-[#B8923D]/20'; // 待改进 - Amber Gold
};

const TextChunker: React.FC<TextChunkerProps> = ({ 
  text, 
  highlights = [], 
  onChunkClick, 
  className = '' 
}) => {
  const [activeChunk, setActiveChunk] = useState<string | null>(null);

  const chunks = useMemo(() => {
    if (!text || typeof text !== 'string') return [];

    // 智能分段算法
    const sentences = text.split(/[.!?。！？]\s+/).filter(s => s.trim().length > 0);
    const chunks: TextChunk[] = [];
    let currentIndex = 0;

    sentences.forEach((sentence, idx) => {
      const trimmedSentence = sentence.trim();
      if (trimmedSentence.length === 0) return;

      // 检查是否包含高亮内容
      const containsHighlight = highlights.some(h => 
        h && trimmedSentence.toLowerCase().includes(h.toLowerCase())
      );

      // 为高亮内容分配分数
      let score = undefined;
      if (containsHighlight) {
        score = 85 + Math.floor(Math.random() * 15); // 85-100之间的随机分数
      }

      const startIndex = currentIndex;
      const endIndex = currentIndex + trimmedSentence.length;

      chunks.push({
        id: `chunk-${idx}`,
        content: trimmedSentence,
        type: trimmedSentence.length > 100 ? 'paragraph' : 'sentence',
        score,
        isHighlighted: containsHighlight,
        startIndex,
        endIndex
      });

      currentIndex = endIndex + 2; // 加上分隔符的长度
    });

    return chunks;
  }, [text, highlights]);

  const renderChunkContent = (chunk: TextChunk) => {
    if (!chunk.isHighlighted || !chunk.score) {
      return chunk.content;
    }

    // 查找需要高亮的具体文本片段
    let content = chunk.content;
    highlights.forEach(highlight => {
      if (highlight && content.toLowerCase().includes(highlight.toLowerCase())) {
        const regex = new RegExp(`(${highlight})`, 'gi');
        const parts = content.split(regex);
        
        content = parts.map((part) => {
          if (part.toLowerCase() === highlight.toLowerCase()) {
            return `<highlight data-score="${chunk.score}">${part}</highlight>`;
          }
          return part;
        }).join('');
      }
    });

    // 渲染高亮内容
    const parts = content.split(/(<highlight data-score="\d+">.*?<\/highlight>)/g);
    return parts.map((part, index) => {
      const highlightMatch = part.match(/<highlight data-score="(\d+)">(.*?)<\/highlight>/);
      if (highlightMatch) {
        const score = parseInt(highlightMatch[1]);
        const text = highlightMatch[2];
        return (
          <ScoreTooltip key={index} score={score} highlight={text} />
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  if (!chunks.length) {
    return (
      <div className="text-gray-500 italic p-4 ios-glass rounded-lg">
        No content available for display
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center gap-2 mb-4">
        <EmojiIcon category="content" name="paragraph" size="sm" />
        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
          Text Analysis ({chunks.length} segments, {chunks.filter(c => c.isHighlighted).length} highlighted)
        </span>
      </div>

      <AnimatePresence>
        {chunks.map((chunk) => (
          <motion.div
            key={chunk.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className={`
              relative p-4 rounded-xl cursor-pointer transition-all duration-200 ease-out
              ${chunk.isHighlighted 
                ? `bg-gradient-to-r ${getHighlightStyle(chunk.score || 75)} backdrop-blur-sm shadow-sm hover:shadow-md`
                : 'bg-white/60 dark:bg-gray-800/60 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 hover:bg-slate-50/80 hover:border-slate-400/60 dark:hover:bg-slate-900/20'
              }
              ${activeChunk === chunk.id ? 'ring-2 ring-slate-500/50 shadow-lg scale-[1.02]' : ''}
            `}
            onClick={() => {
              setActiveChunk(activeChunk === chunk.id ? null : chunk.id);
              onChunkClick?.(chunk);
            }}
            whileHover={{ y: -1 }}
            whileTap={{ scale: 0.98 }}
          >
            {/* 高亮指示器 */}
            {chunk.isHighlighted && (
              <div className="absolute top-2 right-2 flex items-center gap-1">
                <EmojiIcon category="rating" name="star" size="xs" />
                {chunk.score && (
                  <span className="text-xs font-semibold text-gray-600 dark:text-gray-400">
                    {chunk.score}
                  </span>
                )}
              </div>
            )}

            {/* 内容 */}
            <div className="pr-12">
              <div className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                {renderChunkContent(chunk)}
              </div>
            </div>

            {/* 展开的详细信息 */}
            <AnimatePresence>
              {activeChunk === chunk.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="mt-3 pt-3 border-t border-gray-200/50 dark:border-gray-600/50"
                >
                  <div className="grid grid-cols-2 gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <div>
                      <span className="font-medium">Type:</span> {chunk.type}
                    </div>
                    <div>
                      <span className="font-medium">Length:</span> {chunk.content.length} chars
                    </div>
                    {chunk.score && (
                      <>
                        <div>
                          <span className="font-medium">Score:</span> {chunk.score}/100
                        </div>
                        <div>
                          <span className="font-medium">Quality:</span> {
                            chunk.score >= 90 ? 'Excellent' : 
                            chunk.score >= 80 ? 'Good' : 
                            chunk.score >= 70 ? 'Fair' : 'Needs Improvement'
                          }
                        </div>
                      </>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* 统计信息 */}
      <div className="mt-6 p-4 bg-gray-50/80 dark:bg-gray-800/80 rounded-lg backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-semibold text-gray-800 dark:text-gray-200">
              {chunks.length}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Total Segments</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-slate-700 dark:text-slate-500">
              {chunks.filter(c => c.isHighlighted).length}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">Highlighted</div>
          </div>
          <div>
            <div className="text-lg font-semibold text-[#5F8A50] dark:text-[#87A878]">
              {chunks.filter(c => c.score && c.score >= 85).length}
            </div>
            <div className="text-xs text-gray-600 dark:text-gray-400">High Quality</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextChunker;
