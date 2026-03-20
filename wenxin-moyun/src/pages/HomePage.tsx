import { Link } from 'react-router-dom';
import { Github, Terminal, Copy, Check, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { isGuestMode } from '../utils/guestSession';

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
    <div className="flex items-center gap-2 bg-gray-900 rounded-xl px-5 py-3 shadow-lg">
      <Terminal className="w-4 h-4 text-green-400 flex-shrink-0" />
      <code className="font-mono text-sm text-gray-100 select-all">{command}</code>
      <button
        onClick={handleCopy}
        className="ml-3 p-1.5 text-gray-400 hover:text-white transition-colors"
        aria-label="Copy command"
      >
        {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
      </button>
    </div>
  );
}

const fadeUp = {
  initial: { opacity: 0.01, y: 10 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.05 },
  transition: { duration: 0.6 },
};

export default function HomePage() {
  const guest = isGuestMode();

  return (
    <div className="-mx-4 sm:-mx-6">
      {/* ===== Hero with Background Image ===== */}
      <section className="min-h-[85vh] flex flex-col items-center justify-center px-4 sm:px-6 text-center relative overflow-hidden">
        {/* Hero background — from design HTML line 176-181 */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[120%] opacity-40">
            <div className="absolute inset-0 bg-gradient-to-b from-primary-500/10 to-transparent" />
            <img
              src="/images/hero-bg.jpg"
              alt=""
              className="w-full h-full object-cover"
              loading="eager"
              style={{ maskImage: 'linear-gradient(to bottom, black 20%, transparent 80%)', WebkitMaskImage: 'linear-gradient(to bottom, black 20%, transparent 80%)' }}
            />
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-3xl mx-auto relative z-10"
        >
          <h1 className="font-display text-6xl sm:text-7xl lg:text-8xl font-bold tracking-tight text-on-surface mb-6 leading-[0.95]">
            VULCA
          </h1>
          <p className="text-xl sm:text-2xl lg:text-3xl text-on-surface-variant mb-4 font-light">
            AI that understands{' '}
            <span className="font-semibold text-primary-500">cultural context</span>.
          </p>
          <p className="text-base text-on-surface-variant/70 mb-10 max-w-xl mx-auto">
            Beyond code and logic, VULCA perceives the nuance of human expression across global boundaries.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-10">
            <Link to="/canvas">
              <button className="bg-primary-500 text-white px-10 py-4 rounded-full font-semibold text-base hover:bg-primary-600 active:scale-95 transition-all shadow-lg shadow-primary-500/20 flex items-center gap-2">
                Try Canvas
                <ArrowRight className="w-5 h-5" />
              </button>
            </Link>
            <a href="https://github.com/vulca-org/vulca" target="_blank" rel="noopener noreferrer">
              <button className="bg-gray-900 text-white px-8 py-4 rounded-full font-semibold text-base hover:bg-gray-800 active:scale-95 transition-all flex items-center gap-2">
                <Github className="w-5 h-5" />
                GitHub
              </button>
            </a>
          </div>

          {/* Floating glass terminal preview */}
          <div className="bg-gray-900/80 backdrop-blur-2xl rounded-2xl p-5 text-left shadow-2xl max-w-lg mx-auto border border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="ml-2 text-[10px] text-gray-500 font-mono">vulca-pipeline</span>
            </div>
            <code className="font-mono text-[11px] text-gray-300 leading-relaxed block">
              <span className="text-blue-400">[SCOUT]</span> Analyzing &quot;水墨山水&quot; — tradition: chinese_xieyi<br/>
              <span className="text-blue-400">[DRAFT]</span> Generating 4 candidates via Gemini 3.1...<br/>
              <span className="text-green-400">[CRITIC]</span> L1: 0.92 | L2: 0.88 | L3: 0.95 | L4: 0.90 | L5: 0.87<br/>
              <span className="text-yellow-400">[QUEEN]</span> Decision: accept (weighted: 0.912)
            </code>
          </div>
        </motion.div>
      </section>

      {/* ===== Agent Pipeline ===== */}
      <section className="py-24 px-4 sm:px-6 bg-surface-container-low">
        <motion.div {...fadeUp} className="max-w-4xl mx-auto text-center">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-on-surface mb-4">
            The Agent Pipeline
          </h2>
          <p className="text-on-surface-variant max-w-2xl mx-auto mb-16">
            A multi-layered intelligence architecture designed to refine and validate every cultural nuance with surgical precision.
          </p>

          {/* Glass container with agents + connecting line */}
          <div className="relative bg-surface-container-lowest/60 backdrop-blur-xl rounded-3xl p-8 sm:p-10 shadow-ambient-lg mx-auto max-w-2xl">
            {/* Connecting gradient line (desktop) */}
            <div className="hidden sm:block absolute top-1/2 left-[15%] right-[15%] h-px -translate-y-4 bg-gradient-to-r from-transparent via-primary-200 to-transparent" />

            <div className="flex items-center justify-center gap-6 sm:gap-12 relative z-10">
              {[
                { icon: 'search', label: 'Scout', active: false },
                { icon: 'edit_note', label: 'Draft', active: false },
                { icon: 'spellcheck', label: 'Critic', active: false },
                { icon: 'auto_awesome', label: 'Queen', active: true },
              ].map((agent) => (
                <div key={agent.label} className="flex flex-col items-center gap-3">
                  <div className={`w-14 h-14 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center transition-all ${
                    agent.active
                      ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30 animate-pulse-glow'
                      : 'bg-surface-container-lowest text-on-surface-variant shadow-ambient-sm hover:scale-110 hover:shadow-ambient-md'
                  }`}>
                    <span className="material-symbols-outlined text-2xl">{agent.icon}</span>
                  </div>
                  <span className={`text-sm font-medium ${agent.active ? 'text-primary-500 font-bold' : 'text-on-surface-variant'}`}>
                    {agent.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </section>

      {/* ===== Create / Critique / Evolve ===== */}
      <section className="py-24 px-4 sm:px-6">
        <motion.div {...fadeUp} className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Create',
                desc: 'Generate cultural art that respects tradition. Each work is a dialogue between AI agents and human expression, adapting to any cultural tradition.',
                img: 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=600&q=80',
              },
              {
                title: 'Critique',
                desc: 'Our five-layer scoring system evaluates artwork beyond surface aesthetics, revealing a painting\'s true cultural resonance through L1-L5 analysis.',
                img: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=600&q=80',
              },
              {
                title: 'Evolve',
                desc: 'VULCA learns from every session. Cultural weights shift, few-shot references update, and tradition insights emerge — an intelligence that evolves.',
                img: 'https://images.unsplash.com/photo-1534972195531-d756b9bfa9f2?w=600&q=80',
              },
            ].map((card) => (
              <div key={card.title} className="group">
                <div className="aspect-[4/3] rounded-2xl overflow-hidden mb-6 bg-surface-container-high">
                  <img
                    src={card.img}
                    alt={card.title}
                    className="w-full h-full object-cover group-hover:scale-[1.03] transition-transform duration-700"
                    loading="lazy"
                  />
                </div>
                <h3 className="font-display text-2xl font-bold text-on-surface mb-3">{card.title}</h3>
                <p className="text-on-surface-variant text-sm leading-relaxed">{card.desc}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ===== Academic Trust ===== */}
      <section className="py-12 px-4 sm:px-6 bg-surface-container-low">
        <div className="max-w-3xl mx-auto flex flex-wrap justify-center items-center gap-4">
          {['EMNLP 2025', 'WiNLP 2025', 'arXiv'].map((venue) => (
            <span key={venue} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-container-lowest text-sm font-semibold text-on-surface-variant shadow-ambient-sm">
              <span className="w-2 h-2 rounded-full bg-success-500" />
              {venue}
            </span>
          ))}
        </div>
      </section>

      {/* ===== Get Started ===== */}
      <section className="py-24 px-4 sm:px-6">
        <motion.div {...fadeUp} className="max-w-3xl mx-auto text-center">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-on-surface mb-4">
            Ready to start?
          </h2>
          <p className="text-on-surface-variant mb-10">
            Deploy VULCA AI to your ecosystem in seconds with our CLI.
          </p>

          <div className="bg-gray-900/90 backdrop-blur-2xl rounded-2xl p-6 text-left mb-8 shadow-2xl border border-white/5">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="ml-2 text-[10px] text-gray-500 font-mono">terminal</span>
            </div>
            <code className="font-mono text-sm text-gray-100 leading-relaxed block">
              <span className="text-green-400">$</span> pip install vulca<br />
              <span className="text-green-400">$</span> vulca create &quot;水墨山水&quot; --tradition chinese_xieyi<br />
              <span className="text-green-400">$</span> vulca evaluate artwork.png
            </code>
          </div>

          <a href="https://github.com/vulca-org/vulca" target="_blank" rel="noopener noreferrer" className="text-primary-500 text-sm font-medium hover:underline">
            Read the full documentation →
          </a>
        </motion.div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="py-8 px-4 sm:px-6 bg-surface-container-low">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-on-surface-variant">
          <span className="font-bold text-on-surface">VULCA AI</span>
          <div className="flex items-center gap-6">
            <Link to="/about" className="hover:text-on-surface transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-on-surface transition-colors">Terms of Service</Link>
            <a href="https://github.com/vulca-org/vulca" target="_blank" rel="noopener noreferrer" className="hover:text-on-surface transition-colors">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
