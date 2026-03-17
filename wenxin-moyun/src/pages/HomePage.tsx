import { Link } from 'react-router-dom';
import { Github, Terminal, Copy, Check, ArrowRight, Paintbrush, Eye, RefreshCw } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { IOSButton, IOSCard, IOSCardContent } from '../components/ios';

function CopyableTerminal({ command }: { command: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(command);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = command;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-2 bg-gray-900 dark:bg-gray-950 rounded-xl px-5 py-3 shadow-lg border border-gray-700 dark:border-gray-600">
      <Terminal className="w-4 h-4 text-green-400 flex-shrink-0" />
      <code className="font-mono text-sm text-gray-100 select-all">{command}</code>
      <button
        onClick={handleCopy}
        className="ml-3 p-1.5 rounded-md hover:bg-gray-700 transition-colors text-gray-400 hover:text-white"
        aria-label="Copy command"
      >
        {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
      </button>
    </div>
  );
}

export default function HomePage() {
  return (
    <div className="-mx-4 sm:-mx-6">
      {/* ===== Section 1: Hero (100vh) ===== */}
      <section className="min-h-[90vh] flex flex-col items-center justify-center px-4 sm:px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-3xl mx-auto"
        >
          <h1 className="text-6xl sm:text-7xl font-bold tracking-tight text-gray-900 dark:text-white mb-6">
            VULCA
          </h1>
          <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-10 max-w-2xl mx-auto">
            AI that understands cultural context.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Link to="/canvas">
              <IOSButton
                variant="primary"
                size="lg"
                className="flex items-center gap-2 min-w-[160px] justify-center"
              >
                Try Canvas
                <ArrowRight className="w-5 h-5" />
              </IOSButton>
            </Link>
            <a
              href="https://github.com/vulca-org/vulca"
              target="_blank"
              rel="noopener noreferrer"
            >
              <IOSButton
                variant="secondary"
                size="lg"
                className="flex items-center gap-2 min-w-[160px] justify-center"
              >
                <Github className="w-5 h-5" />
                GitHub
              </IOSButton>
            </a>
          </div>

          <CopyableTerminal command="docker-compose up" />
        </motion.div>
      </section>

      {/* ===== Section 2: Product (100vh) ===== */}
      <section className="min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 bg-gray-50 dark:bg-gray-900/50">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto text-center"
        >
          {/* Canvas screenshot placeholder */}
          <div className="w-full aspect-video bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-800 dark:to-slate-700 rounded-2xl mb-10 flex items-center justify-center border border-slate-300 dark:border-slate-600">
            <span className="text-slate-500 dark:text-slate-400 text-lg font-medium">Canvas Preview</span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            9 agents. 8 traditions. One pipeline.
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
            Scout, Draft, Critic, and Queen collaborate to create and evaluate cultural art in real time.
          </p>
        </motion.div>
      </section>

      {/* ===== Section 3: Differentiators ===== */}
      <section className="py-24 px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="max-w-5xl mx-auto"
        >
          <div className="grid md:grid-cols-3 gap-8">
            <IOSCard variant="elevated" className="text-center p-8">
              <IOSCardContent>
                <Paintbrush className="w-10 h-10 text-[#C87F4A] mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Create</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Generate cultural art through multi-agent collaboration with 8 cultural traditions.
                </p>
              </IOSCardContent>
            </IOSCard>

            <IOSCard variant="elevated" className="text-center p-8">
              <IOSCardContent>
                <Eye className="w-10 h-10 text-[#5F8A50] mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Critique</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  47-dimension evaluation across 8 cultural perspectives with explainable diagnostics.
                </p>
              </IOSCardContent>
            </IOSCard>

            <IOSCard variant="elevated" className="text-center p-8">
              <IOSCardContent>
                <RefreshCw className="w-10 h-10 text-[#334155] mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Evolve</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  The system learns from feedback. Cultural weights evolve. Prompts get smarter.
                </p>
              </IOSCardContent>
            </IOSCard>
          </div>
        </motion.div>
      </section>

      {/* ===== Section 4: Academic Trust ===== */}
      <section className="py-16 px-4 sm:px-6 bg-gray-50 dark:bg-gray-900/50">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.3 }}
          className="max-w-3xl mx-auto text-center"
        >
          <div className="flex flex-wrap justify-center items-center gap-6 md:gap-12 text-lg font-semibold text-gray-700 dark:text-gray-300">
            <span>EMNLP 2025</span>
            <span className="text-gray-300 dark:text-gray-600">|</span>
            <span>WiNLP 2025</span>
            <span className="text-gray-300 dark:text-gray-600">|</span>
            <span>arXiv</span>
          </div>
        </motion.div>
      </section>

      {/* ===== Section 5: Get Started ===== */}
      <section className="py-24 px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
          className="max-w-3xl mx-auto text-center"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-8">
            Get Started
          </h2>

          <div className="bg-gray-900 dark:bg-gray-950 rounded-2xl p-6 text-left mb-10 border border-gray-700">
            <code className="font-mono text-sm text-gray-100 leading-relaxed block">
              <span className="text-green-400">$</span> git clone https://github.com/vulca-org/vulca.git<br />
              <span className="text-green-400">$</span> cd vulca<br />
              <span className="text-green-400">$</span> docker-compose up
            </code>
          </div>

          <a
            href="https://github.com/vulca-org/vulca"
            target="_blank"
            rel="noopener noreferrer"
          >
            <IOSButton
              variant="primary"
              size="lg"
              className="flex items-center gap-2 mx-auto"
            >
              <Github className="w-5 h-5" />
              Star on GitHub
            </IOSButton>
          </a>
        </motion.div>
      </section>
    </div>
  );
}
