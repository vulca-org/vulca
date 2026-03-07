import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Image, X } from 'lucide-react';
import { IOSButton } from '../ios';

interface IntentInputProps {
  onSubmit: (intent: string, image?: File) => void;
  isLoading?: boolean;
}

const EXAMPLE_PROMPTS = [
  'Evaluate this Chinese ink painting',
  'Check brand consistency',
  'Analyze cultural sensitivity',
];

export const IntentInput: React.FC<IntentInputProps> = ({ onSubmit, isLoading = false }) => {
  const [intent, setIntent] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageSelect = useCallback((file: File) => {
    if (!file.type.startsWith('image/')) return;
    setImage(file);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target?.result as string);
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) handleImageSelect(file);
    },
    [handleImageSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const removeImage = useCallback(() => {
    setImage(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  }, []);

  const handleSubmit = () => {
    if (!intent.trim() && !image) return;
    onSubmit(intent.trim(), image ?? undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-2xl mx-auto"
    >
      {/* Intent textarea */}
      <div className="relative">
        <textarea
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe what you want to evaluate..."
          rows={3}
          disabled={isLoading}
          className="
            w-full px-4 py-3 text-base
            bg-white dark:bg-gray-900
            border border-gray-200 dark:border-gray-700
            rounded-xl
            text-gray-900 dark:text-white
            placeholder-gray-400 dark:placeholder-gray-500
            focus:outline-none focus:ring-2 focus:ring-slate-500/40 focus:border-slate-400
            transition-all duration-200
            resize-none
            disabled:opacity-50
          "
        />
      </div>

      {/* Image upload area */}
      <div className="mt-3">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleImageSelect(file);
          }}
        />

        <AnimatePresence mode="wait">
          {imagePreview ? (
            <motion.div
              key="preview"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="relative inline-block"
            >
              <img
                src={imagePreview}
                alt="Upload preview"
                className="h-24 w-24 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
              />
              <button
                type="button"
                onClick={removeImage}
                className="
                  absolute -top-2 -right-2
                  w-6 h-6 rounded-full
                  bg-red-500 text-white
                  flex items-center justify-center
                  shadow-md
                  hover:bg-red-600
                  transition-colors
                "
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="dropzone"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={() => fileInputRef.current?.click()}
              className={`
                flex items-center gap-3 px-4 py-3
                border-2 border-dashed rounded-xl
                cursor-pointer
                transition-all duration-200
                ${
                  isDragging
                    ? 'border-slate-500 bg-slate-50 dark:bg-slate-900/30'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }
              `}
            >
              <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gray-100 dark:bg-gray-800">
                {isDragging ? (
                  <Upload className="w-5 h-5 text-slate-500" />
                ) : (
                  <Image className="w-5 h-5 text-gray-400" />
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {isDragging ? 'Drop image here' : 'Upload an image'}
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  Drag & drop or click to browse
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Example prompt chips */}
      <div className="mt-4 flex flex-wrap gap-2">
        {EXAMPLE_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => setIntent(prompt)}
            disabled={isLoading}
            className="
              px-3 py-1.5 text-xs font-medium
              bg-gray-100 dark:bg-gray-800
              text-gray-600 dark:text-gray-400
              rounded-full
              hover:bg-gray-200 dark:hover:bg-gray-700
              hover:text-gray-900 dark:hover:text-gray-200
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
            "
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Submit button */}
      <div className="mt-5">
        <IOSButton
          variant="primary"
          size="lg"
          onClick={handleSubmit}
          disabled={isLoading || (!intent.trim() && !image)}
          className="w-full"
        >
          {isLoading ? 'Evaluating...' : 'Evaluate'}
        </IOSButton>
      </div>
    </motion.div>
  );
};

export default IntentInput;
