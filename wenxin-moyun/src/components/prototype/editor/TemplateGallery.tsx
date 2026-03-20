/**
 * TemplateGallery — card-based template selector overlay.
 *
 * Replaces the <select> dropdown with a visual gallery showing
 * template name, description, node count, and mini pipeline preview.
 * Quick Evaluate is highlighted for new users.
 */

export interface TemplateInfo {
  id: string;
  name: string;
  description: string;
  nodeCount: number;
  nodes?: string[];
  isSaved?: boolean;
}

interface Props {
  templates: TemplateInfo[];
  activeTemplate: string;
  onSelect: (id: string) => void;
  onDelete?: (id: string) => void;
  onClose: () => void;
}

const RECOMMENDED = new Set(['quick_evaluate']);

function MiniPipeline({ nodes }: { nodes?: string[] }) {
  if (!nodes || nodes.length === 0) return null;
  return (
    <div className="flex items-center gap-0.5 mt-2">
      {nodes.map((n, i) => (
        <div key={`${n}-${i}`} className="flex items-center gap-0.5">
          <div
            className="w-2 h-2 rounded-full bg-[#C87F4A] dark:bg-[#C87F4A]"
            title={n}
          />
          {i < nodes.length - 1 && (
            <div className="w-3 h-px bg-gray-300 dark:bg-gray-600" />
          )}
        </div>
      ))}
    </div>
  );
}

function TemplateCard({
  template,
  active,
  onSelect,
  onDelete,
  recommended,
}: {
  template: TemplateInfo;
  active: boolean;
  onSelect: (id: string) => void;
  onDelete?: (id: string) => void;
  recommended?: boolean;
}) {
  return (
    <div
      onClick={() => onSelect(template.id)}
      className={[
        'p-3 rounded-lg border cursor-pointer transition-all hover:shadow-sm',
        active
          ? 'border-[#C87F4A] bg-[#f9f9ff] dark:bg-[#C87F4A]/10'
          : recommended
            ? 'border-[#C9C2B8] dark:border-[#4A433C] bg-[#f9f9ff]/50 dark:bg-[#C87F4A]/5'
            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
      ].join(' ')}
    >
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-900 dark:text-white">
          {template.name}
        </span>
        <span className="text-[10px] text-gray-400">{template.nodeCount} nodes</span>
      </div>
      <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">
        {template.description}
      </p>
      {recommended && (
        <span className="inline-block mt-1 text-[9px] font-semibold text-[#C87F4A] dark:text-[#DDA574] bg-[#C87F4A]/10 dark:bg-[#C87F4A]/15 px-1.5 py-0.5 rounded-full">
          Best for new users
        </span>
      )}
      <MiniPipeline nodes={template.nodes} />
      {onDelete && template.isSaved && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(template.id);
          }}
          className="mt-1 text-[10px] text-red-500 hover:text-red-700"
        >
          Delete
        </button>
      )}
    </div>
  );
}

export default function TemplateGallery({
  templates,
  activeTemplate,
  onSelect,
  onDelete,
  onClose,
}: Props) {
  const recommended = templates.filter((t) => RECOMMENDED.has(t.id));
  const standard = templates.filter(
    (t) => !t.isSaved && !RECOMMENDED.has(t.id),
  );
  const saved = templates.filter((t) => t.isSaved);

  return (
    <div
      className="absolute inset-0 z-30 bg-black/20 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="absolute left-4 top-14 w-80 max-h-[calc(100%-80px)] bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            Templates
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-lg leading-none"
          >
            &times;
          </button>
        </div>

        <div className="p-3 space-y-2">
          {recommended.length > 0 && (
            <>
              <div className="text-[10px] font-semibold text-[#C87F4A] dark:text-[#DDA574] uppercase tracking-wider">
                Recommended
              </div>
              {recommended.map((t) => (
                <TemplateCard
                  key={t.id}
                  template={t}
                  active={t.id === activeTemplate}
                  onSelect={onSelect}
                  recommended
                />
              ))}
            </>
          )}

          {standard.length > 0 && (
            <>
              <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mt-3">
                Standard
              </div>
              <div className="grid grid-cols-2 gap-2">
                {standard.map((t) => (
                  <TemplateCard
                    key={t.id}
                    template={t}
                    active={t.id === activeTemplate}
                    onSelect={onSelect}
                  />
                ))}
              </div>
            </>
          )}

          {saved.length > 0 && (
            <>
              <div className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mt-3">
                Saved
              </div>
              {saved.map((t) => (
                <TemplateCard
                  key={t.id}
                  template={t}
                  active={t.id === activeTemplate}
                  onSelect={onSelect}
                  onDelete={onDelete}
                />
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
