/**
 * CiteModal - Academic Citation Modal Component
 *
 * Supports multiple citation formats: BibTeX, RIS, CSL JSON, APA, MLA, Chicago, Harvard
 * Provides copy and download functionality
 *
 * @module components/trustlayer/CiteModal
 */

import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Copy, Check, Download, FileText, ExternalLink } from 'lucide-react';
import { IOSButton } from '../ios';
import {
  type Citation,
  type CitationFormat,
  generateCitation,
  getCitationFileExtension,
  copyToClipboard,
  downloadFile,
} from '../../utils/trustedExport';

interface CiteModalProps {
  citation: Citation;
  visible: boolean;
  onClose: () => void;
}

const FORMATS: { id: CitationFormat; label: string; description: string }[] = [
  { id: 'bibtex', label: 'BibTeX', description: 'LaTeX bibliography format' },
  { id: 'ris', label: 'RIS', description: 'Reference manager format' },
  { id: 'csl-json', label: 'CSL JSON', description: 'Citation Style Language' },
  { id: 'apa', label: 'APA', description: '7th edition' },
  { id: 'mla', label: 'MLA', description: '9th edition' },
  { id: 'chicago', label: 'Chicago', description: 'Author-Date style' },
  { id: 'harvard', label: 'Harvard', description: 'Harvard referencing' },
];

export const CiteModal: React.FC<CiteModalProps> = ({
  citation,
  visible,
  onClose,
}) => {
  const [format, setFormat] = useState<CitationFormat>('bibtex');
  const [copied, setCopied] = useState(false);
  const [formattedCitation, setFormattedCitation] = useState('');

  // Update formatted citation when format changes
  useEffect(() => {
    setFormattedCitation(generateCitation(citation, format));
  }, [citation, format]);

  const handleCopy = async () => {
    const success = await copyToClipboard(formattedCitation);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownload = () => {
    const extension = getCitationFileExtension(format);
    const filename = `${citation.key}${extension}`;
    const mimeType = format === 'csl-json' ? 'application/json' : 'text/plain';
    downloadFile(formattedCitation, filename, mimeType);
  };

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (visible) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [visible, onClose]);

  if (!visible) return null;

  const modalContent = (
    <AnimatePresence>
      {visible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 z-50 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <FileText className="w-5 h-5 text-slate-600" />
                Cite This Work
              </h2>
              <button
                onClick={onClose}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Paper Info */}
            <div className="px-4 py-3 bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800">
              <h3 className="font-medium text-sm line-clamp-2">{citation.title}</h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {citation.authors.join(', ')} ({citation.year})
              </p>
              {citation.doi && (
                <a
                  href={`https://doi.org/${citation.doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-slate-600 hover:underline flex items-center gap-1 mt-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  DOI: {citation.doi}
                </a>
              )}
            </div>

            {/* Format Tabs */}
            <div className="flex gap-1 p-3 border-b border-gray-200 dark:border-gray-800 overflow-x-auto scrollbar-hide">
              {FORMATS.map(f => (
                <button
                  key={f.id}
                  onClick={() => setFormat(f.id)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                    format === f.id
                      ? 'bg-slate-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                  title={f.description}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Citation Content */}
            <div className="flex-1 overflow-auto p-4">
              <pre className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 text-sm font-mono whitespace-pre-wrap break-all text-gray-800 dark:text-gray-200 leading-relaxed">
                {formattedCitation}
              </pre>
            </div>

            {/* Actions */}
            <div className="flex gap-3 p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
              <IOSButton
                variant="primary"
                onClick={handleCopy}
                className="flex-1"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-2" />
                    Copy to Clipboard
                  </>
                )}
              </IOSButton>
              <IOSButton variant="secondary" onClick={handleDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </IOSButton>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );

  return createPortal(modalContent, document.body);
};

export default CiteModal;
