import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Copy, Check } from 'lucide-react';
import { IOSSegmentedControl, IOSCard, IOSCardContent } from '../ios';

interface CodeExportProps {
  intent: string;
  traditionUsed?: string;
}

const TAB_LABELS = ['Python', 'curl', 'YAML'];

function generatePython(intent: string, tradition: string): string {
  return `import requests

response = requests.post(
    "https://api.vulcaart.art/v1/evaluate",
    headers={"Authorization": "Bearer YOUR_API_KEY"},
    json={
        "intent": "${intent}",
        "tradition": "${tradition}",
        "image_url": "https://example.com/artwork.jpg",
    },
)

result = response.json()
print(f"Score: {result['score']}")
print(f"Risk:  {result['risk_level']}")`;
}

function generateCurl(intent: string, tradition: string): string {
  return `curl -X POST https://api.vulcaart.art/v1/evaluate \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "intent": "${intent}",
    "tradition": "${tradition}",
    "image_url": "https://example.com/artwork.jpg"
  }'`;
}

function generateYAML(intent: string, tradition: string): string {
  return `# VULCA Evaluation Config
evaluation:
  intent: "${intent}"
  tradition: "${tradition}"
  image_url: "https://example.com/artwork.jpg"

options:
  dimensions: all
  risk_analysis: true
  output_format: json`;
}

const generators: Record<number, (intent: string, tradition: string) => string> = {
  0: generatePython,
  1: generateCurl,
  2: generateYAML,
};

export const CodeExport: React.FC<CodeExportProps> = ({
  intent,
  traditionUsed = 'chinese_ink',
}) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [copied, setCopied] = useState(false);

  const code = generators[selectedTab](intent || 'Evaluate this artwork', traditionUsed);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = code;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [code]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className="w-full"
    >
      <IOSCard variant="elevated" padding="md">
        <IOSCardContent>
          {/* Tab switcher */}
          <div className="flex items-center justify-between mb-4">
            <IOSSegmentedControl
              segments={TAB_LABELS}
              selectedIndex={selectedTab}
              onChange={(index) => setSelectedTab(index)}
              size="compact"
            />

            <button
              type="button"
              onClick={handleCopy}
              className="
                inline-flex items-center gap-1.5 px-3 py-1.5
                text-xs font-medium
                text-gray-500 dark:text-gray-400
                hover:text-gray-700 dark:hover:text-gray-200
                hover:bg-gray-100 dark:hover:bg-gray-800
                rounded-md transition-all duration-200
              "
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-green-500" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  Copy
                </>
              )}
            </button>
          </div>

          {/* Code block */}
          <div className="relative rounded-lg bg-gray-950 dark:bg-gray-900 overflow-hidden">
            <pre className="p-4 overflow-x-auto text-xs leading-relaxed">
              <code className="text-gray-300 font-mono whitespace-pre">{code}</code>
            </pre>
          </div>
        </IOSCardContent>
      </IOSCard>
    </motion.div>
  );
};

export default CodeExport;
