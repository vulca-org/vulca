/**
 * Segmented control for selecting media type (image, video, 3D, sound).
 *
 * Currently only "Image" is enabled; other types show a "Coming Soon" badge.
 * Uses Art Professional color palette.
 */

interface MediaTypeOption {
  value: string;
  label: string;
  emoji: string;
  enabled: boolean;
}

const MEDIA_TYPES: MediaTypeOption[] = [
  { value: 'image', label: 'Image', emoji: '\u{1F5BC}\uFE0F', enabled: true },
  { value: 'video', label: 'Video', emoji: '\u{1F3AC}', enabled: false },
  { value: '3d_model', label: '3D Model', emoji: '\u{1F9CA}', enabled: false },
  { value: 'sound', label: 'Sound', emoji: '\u{1F3B5}', enabled: false },
];

interface Props {
  value: string;
  onChange: (type: string) => void;
  disabled?: boolean;
}

export default function MediaTypeSelector({ value, onChange, disabled }: Props) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Media Type
      </label>
      <div className="flex rounded-lg overflow-hidden border border-gray-300 dark:border-gray-600">
        {MEDIA_TYPES.map((opt) => {
          const isSelected = value === opt.value;
          const isDisabled = disabled || !opt.enabled;

          let className: string;
          if (isSelected && opt.enabled) {
            className = 'bg-[#C87F4A] text-white';
          } else if (!opt.enabled) {
            className = 'bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-500 cursor-not-allowed';
          } else {
            className = 'bg-white border-surface-container-high text-on-surface hover:bg-surface-container-low transition-colors';
          }

          return (
            <button
              key={opt.value}
              type="button"
              disabled={isDisabled}
              onClick={() => opt.enabled && onChange(opt.value)}
              className={`
                flex-1 flex flex-col items-center gap-0.5 px-2 py-2 text-xs font-medium
                transition-colors relative
                ${className}
                ${isDisabled ? 'opacity-80' : ''}
              `}
            >
              <span className="text-base">{opt.emoji}</span>
              <span>{opt.label}</span>
              {!opt.enabled && (
                <span className="text-[9px] text-[#B8923D] dark:text-[#B8923D] font-medium leading-tight">
                  Coming Soon
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
