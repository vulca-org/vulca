/**
 * Metadata Tags Panel — Displays scout evidence and tradition tags.
 */

interface Props {
  evidence: Record<string, unknown> | null;
  tradition: string;
  riskTags?: string[];
}

export default function MetadataTagsPanel({ evidence, tradition, riskTags }: Props) {
  const tags: string[] = [];

  // Add tradition as tag
  if (tradition && tradition !== 'default') {
    tags.push(`#${tradition}`);
  }

  // Extract keywords from evidence
  if (evidence) {
    const keywords = evidence.keywords || evidence.key_terms || evidence.terms;
    if (Array.isArray(keywords)) {
      for (const kw of keywords.slice(0, 4)) {
        if (typeof kw === 'string') tags.push(`#${kw.replace(/\s+/g, '_')}`);
      }
    }
    // Extract samples/references
    const samples = evidence.samples || evidence.references;
    if (Array.isArray(samples) && samples.length > 0) {
      tags.push('#reference_art');
    }
  }

  // Add risk tags
  if (riskTags?.length) {
    for (const rt of riskTags.slice(0, 2)) {
      tags.push(`#${rt}`);
    }
  }

  // Fallback
  if (tags.length === 0) {
    tags.push('#heritage', '#cultural_analysis');
  }

  return (
    <div className="bg-surface-container-low rounded-xl p-4 mb-8">
      <h4 className="text-[10px] font-black uppercase tracking-widest text-outline mb-3">Metadata Tags</h4>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="px-2.5 py-1 bg-white text-[10px] font-bold text-on-surface-variant rounded-md shadow-ambient-sm"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
