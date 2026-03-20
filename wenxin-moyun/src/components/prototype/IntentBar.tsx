/**
 * IntentBar — compact intent input + image upload for the unified /canvas entry.
 *
 * Placed at the top of PrototypePage left panel.
 * - Text input for natural language intent
 * - Image upload (click or drag)
 * - Submit button
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { IOSCard, IOSCardContent, IOSButton } from '../ios';

export interface IntentBarProps {
  onSubmit: (intent: string, imageFile?: File) => void;
  /** Called whenever the intent text changes (for live tradition auto-matching). */
  onIntentChange?: (intent: string) => void;
  disabled?: boolean;
  /** Pre-fill value (e.g. from Gallery Fork URL params). */
  initialValue?: string;
}

export default function IntentBar({ onSubmit, onIntentChange, disabled = false, initialValue = '' }: IntentBarProps) {
  const [intent, setIntent] = useState(initialValue);
  // Sync when initialValue changes (e.g. Gallery Fork navigation)
  useEffect(() => {
    if (initialValue && initialValue !== intent) {
      setIntent(initialValue);
      onIntentChange?.(initialValue);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialValue]);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    if (!intent.trim() && !imageFile) return;
    onSubmit(intent.trim(), imageFile ?? undefined);
    setIntent('');
    setImageFile(null);
  }, [intent, imageFile, onSubmit]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit],
  );

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setImageFile(file);
    }
  }, []);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) setImageFile(file);
  }, []);

  return (
    <IOSCard variant="elevated" padding="md" animate={false}>
      <IOSCardContent>
        <div className="space-y-2">
          {/* Text input */}
          <textarea
            data-testid="intent-input"
            value={intent}
            onChange={(e) => { setIntent(e.target.value); onIntentChange?.(e.target.value); }}
            onKeyDown={handleKeyDown}
            placeholder="Describe your creation intent..."
            disabled={disabled}
            rows={2}
            className="w-full resize-none rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 px-3 py-2 text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:border-[#C87F4A] focus:outline-none focus:ring-1 focus:ring-[#C87F4A] disabled:opacity-50"
          />

          {/* Image upload zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={[
              'flex items-center gap-2 rounded-lg border border-dashed px-3 py-2 cursor-pointer transition-colors text-xs',
              dragActive
                ? 'border-[#C87F4A] bg-[#f9f9ff] dark:bg-[#C87F4A]/10'
                : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500',
              disabled ? 'opacity-50 pointer-events-none' : '',
            ].join(' ')}
          >
            <span className="text-gray-400 dark:text-gray-500">
              {imageFile ? imageFile.name : 'Drop image or click to upload (evaluate mode)'}
            </span>
            {imageFile && (
              <button
                onClick={(e) => { e.stopPropagation(); setImageFile(null); }}
                className="ml-auto text-gray-400 hover:text-red-500 text-sm"
              >
                ×
              </button>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          {/* Submit */}
          <IOSButton
            variant="primary"
            size="sm"
            onClick={handleSubmit}
            disabled={disabled || (!intent.trim() && !imageFile)}
            className="w-full"
            data-testid="intent-submit"
          >
            {imageFile ? 'Evaluate' : 'Create'}
          </IOSButton>
        </div>
      </IOSCardContent>
    </IOSCard>
  );
}
