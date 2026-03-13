import { useLocation, Link, Navigate } from 'react-router-dom';
import {
  CheckCircle2,
  Mail,
  Clock,
  ArrowRight,
  FileText,
  Users,
  Calendar
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardContent,
} from '../components/ios';

interface LocationState {
  leadId: string;
  name: string;
  email: string;
}

const nextSteps = [
  {
    icon: Mail,
    title: 'Check your inbox',
    desc: 'You\'ll receive a confirmation email shortly',
    time: 'Within 5 minutes',
  },
  {
    icon: Calendar,
    title: 'We\'ll reach out',
    desc: 'Our team will contact you to schedule a demo',
    time: 'Within 24 hours',
  },
  {
    icon: Users,
    title: 'Meet with our team',
    desc: '30-minute personalized walkthrough of VULCA',
    time: 'At your convenience',
  },
];

const exploreLinks = [
  {
    icon: FileText,
    title: 'Read the Documentation',
    desc: 'Learn about our 47D evaluation framework',
    href: '/research',
  },
  {
    icon: Users,
    title: 'View Models',
    desc: 'See how top AI models perform',
    href: '/models',
  },
  {
    icon: ArrowRight,
    title: 'Try Canvas',
    desc: 'Create cultural art with AI',
    href: '/canvas',
  },
];

export default function DemoConfirmationPage() {
  const location = useLocation();
  const state = location.state as LocationState | null;

  // Redirect if no state (direct access)
  if (!state?.leadId) {
    return <Navigate to="/demo" replace />;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-12 py-8">
      {/* Success Header */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full mb-6">
          <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
        </div>

        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Thank You, {state.name.split(' ')[0]}!
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Your demo request has been received.
        </p>
      </motion.div>

      {/* Confirmation Details */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <IOSCard variant="elevated">
          <IOSCardContent className="p-6">
            <div className="flex items-center gap-4 p-4 bg-slate-50 dark:bg-slate-900/20 rounded-xl">
              <Mail className="w-6 h-6 text-slate-700 dark:text-slate-500" />
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Confirmation sent to
                </p>
                <p className="font-semibold text-gray-900 dark:text-white">
                  {state.email}
                </p>
              </div>
            </div>
          </IOSCardContent>
        </IOSCard>
      </motion.div>

      {/* What Happens Next */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          What Happens Next
        </h2>
        <div className="space-y-4">
          {nextSteps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="flex items-start gap-4 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-center justify-center w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-full flex-shrink-0">
                <span className="text-lg font-bold text-gray-600 dark:text-gray-300">
                  {index + 1}
                </span>
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <step.icon className="w-4 h-4 text-slate-600" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {step.title}
                  </h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {step.desc}
                </p>
                <div className="flex items-center gap-1 mt-2 text-xs text-gray-500 dark:text-gray-500">
                  <Clock className="w-3 h-3" />
                  {step.time}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* While You Wait */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          While You Wait
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {exploreLinks.map((link) => (
            <Link key={link.href} to={link.href}>
              <div className="h-full p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-slate-600 dark:hover:border-slate-600 transition-all group">
                <link.icon className="w-8 h-8 text-gray-400 group-hover:text-slate-600 mb-3 transition-colors" />
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1 group-hover:text-slate-700 dark:group-hover:text-slate-500 transition-colors">
                  {link.title}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {link.desc}
                </p>
              </div>
            </Link>
          ))}
        </div>
      </motion.div>

      {/* Back to Home */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className="text-center pt-8"
      >
        <Link to="/">
          <IOSButton variant="secondary" size="lg" className="inline-flex items-center gap-2">
            <ArrowRight className="w-5 h-5 rotate-180" />
            Back to Home
          </IOSButton>
        </Link>
      </motion.div>

      {/* Support Note */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.9 }}
        className="text-center text-sm text-gray-500 dark:text-gray-400"
      >
        <p>
          Questions? Contact us at{' '}
          <a
            href="mailto:support@vulcaart.art"
            className="text-slate-700 dark:text-slate-500 hover:underline"
          >
            support@vulcaart.art
          </a>
        </p>
      </motion.div>
    </div>
  );
}
