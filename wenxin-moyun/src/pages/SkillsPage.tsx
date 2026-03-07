import { useState, useMemo } from 'react';
import { Search, Plus, Package } from 'lucide-react';
import {
  IOSButton,
  IOSCardGrid,
  IOSSegmentedControl,
  IOSSheet,
} from '../components/ios';
import SkillCard from '../components/skills/SkillCard';
import type { SkillItem } from '../components/skills/SkillCard';
import SkillDetail from '../components/skills/SkillDetail';
import CreateSkillWizard from '../components/skills/CreateSkillWizard';

// ---------------------------------------------------------------------------
// Mock data
// ---------------------------------------------------------------------------

const mockSkills: SkillItem[] = [
  { id: '1', name: 'Brand Consistency', description: 'Evaluate visual consistency with brand guidelines including logo usage, typography, and color palette adherence.', tags: ['brand', 'design'], author: 'vulca', version: '1.0.0', upvotes: 42, downvotes: 3 },
  { id: '2', name: 'Audience Fit', description: 'Score content for target demographic appeal across 12 audience segments with cultural sensitivity.', tags: ['audience', 'marketing'], author: 'vulca', version: '1.0.0', upvotes: 38, downvotes: 5 },
  { id: '3', name: 'Trend Alignment', description: 'Match against current aesthetic trends with weekly sync from design trend databases.', tags: ['trends', 'design'], author: 'vulca', version: '1.0.0', upvotes: 29, downvotes: 2 },
  { id: '4', name: 'Accessibility Check', description: 'Verify content meets WCAG 2.1 AA standards for color contrast, text size, and interactive elements.', tags: ['accessibility', 'quality'], author: 'community', version: '1.0.0', upvotes: 55, downvotes: 1 },
  { id: '5', name: 'Emotional Resonance', description: 'Analyze the emotional impact of visual content across 8 dimensions including warmth, trust, and excitement.', tags: ['emotion', 'audience'], author: 'vulca', version: '1.0.0', upvotes: 33, downvotes: 4 },
  { id: '6', name: 'Performance Benchmark', description: 'Measure inference latency and resource consumption for model evaluation pipelines.', tags: ['performance', 'quality'], author: 'community', version: '1.2.0', upvotes: 21, downvotes: 0 },
];

// ---------------------------------------------------------------------------
// Filter segments
// ---------------------------------------------------------------------------

const TAG_FILTERS = ['All', 'brand', 'design', 'audience', 'marketing', 'trends', 'quality', 'emotion', 'performance', 'accessibility'];

// ---------------------------------------------------------------------------
// SkillsPage
// ---------------------------------------------------------------------------

export default function SkillsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [tagFilterIndex, setTagFilterIndex] = useState(0);
  const [selectedSkill, setSelectedSkill] = useState<SkillItem | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  const activeTag = TAG_FILTERS[tagFilterIndex];

  const filteredSkills = useMemo(() => {
    let result = mockSkills;

    // Filter by tag
    if (activeTag !== 'All') {
      result = result.filter((s) => s.tags.includes(activeTag));
    }

    // Filter by search
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.tags.some((t) => t.includes(q)) ||
          s.author.toLowerCase().includes(q)
      );
    }

    return result;
  }, [activeTag, searchQuery]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-gray-50 to-white dark:from-black dark:via-gray-900 dark:to-black">
      <div className="container mx-auto px-4 py-8 max-w-6xl">

        {/* Page header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-slate-700 to-amber-700 bg-clip-text text-transparent">
            Skill Marketplace
          </h1>
          <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Browse, discuss, and create evaluation skills for the VULCA platform. Each skill is a reusable evaluation module that can be composed into pipelines.
          </p>
        </div>

        {/* Search + Create row */}
        <div className="flex flex-col sm:flex-row gap-3 mb-5">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-500/40 transition"
            />
          </div>
          <IOSButton variant="primary" size="md" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-1.5" />
            Create Skill
          </IOSButton>
        </div>

        {/* Tag filter */}
        <div className="mb-6 overflow-x-auto pb-1 -mx-4 px-4">
          <IOSSegmentedControl
            segments={TAG_FILTERS}
            selectedIndex={tagFilterIndex}
            onChange={(index) => setTagFilterIndex(index)}
            size="compact"
            className="min-w-max"
          />
        </div>

        {/* Skills grid */}
        {filteredSkills.length > 0 ? (
          <IOSCardGrid columns={3} gap="md">
            {filteredSkills.map((skill) => (
              <SkillCard
                key={skill.id}
                skill={skill}
                onClick={() => setSelectedSkill(skill)}
              />
            ))}
          </IOSCardGrid>
        ) : (
          <div className="text-center py-16">
            <Package className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchQuery
                ? `No skills match "${searchQuery}".`
                : `No skills found for "${activeTag}" tag.`}
            </p>
            {searchQuery && (
              <IOSButton variant="text" size="sm" onClick={() => setSearchQuery('')} className="mt-3">
                Clear Search
              </IOSButton>
            )}
          </div>
        )}
      </div>

      {/* Detail sheet */}
      <IOSSheet
        visible={selectedSkill !== null}
        onClose={() => setSelectedSkill(null)}
        height="large"
      >
        {selectedSkill && (
          <SkillDetail
            skill={selectedSkill}
            onClose={() => setSelectedSkill(null)}
          />
        )}
      </IOSSheet>

      {/* Create wizard sheet */}
      <IOSSheet
        visible={showCreate}
        onClose={() => setShowCreate(false)}
        height="large"
      >
        <CreateSkillWizard onClose={() => setShowCreate(false)} />
      </IOSSheet>
    </div>
  );
}
