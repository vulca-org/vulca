import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  Calendar,
  Shield,
  Lock,
  Eye,
  FileText,
  Users,
  Trash2,
  GitBranch,
  CheckCircle2,
  Server,
  Key,
  History,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
  IOSCardGrid,
  IOSSegmentedControl,
} from '../components/ios';
import DataEthicsPage from './DataEthicsPage';
import SOPPage from './SOPPage';

const securityFeatures = [
  {
    icon: Lock,
    title: 'Data Encryption',
    description: 'All data encrypted at rest (AES-256) and in transit (TLS 1.3)',
    items: [
      'AES-256 encryption at rest',
      'TLS 1.3 for all connections',
      'Encrypted database backups',
      'Key rotation policies',
    ],
  },
  {
    icon: Users,
    title: 'Access Control (RBAC)',
    description: 'Role-based access control for enterprise workspaces',
    items: [
      'Role-based permissions',
      'SSO/SAML integration',
      'MFA enforcement',
      'Session management',
    ],
  },
  {
    icon: History,
    title: 'Audit Logging',
    description: 'Comprehensive audit trails for all operations',
    items: [
      'Full operation history',
      'User activity logs',
      'Data access records',
      'Exportable audit reports',
    ],
  },
  {
    icon: Trash2,
    title: 'Data Deletion',
    description: 'Complete control over your data lifecycle',
    items: [
      'On-demand data deletion',
      'Automatic retention policies',
      'GDPR compliance support',
      'Deletion verification',
    ],
  },
  {
    icon: GitBranch,
    title: 'Version Control',
    description: 'Full traceability for reproducible results',
    items: [
      'Framework version tracking',
      'Dataset versioning',
      'Evaluation reproducibility',
      'Change history',
    ],
  },
  {
    icon: Server,
    title: 'Infrastructure',
    description: 'Enterprise-grade cloud infrastructure',
    items: [
      'SOC 2 compliant hosting',
      'Geographic data residency',
      'Regular penetration testing',
      '99.9% uptime SLA',
    ],
  },
];

const complianceItems = [
  { name: 'GDPR', status: 'Ready', desc: 'DPA available on request' },
  { name: 'SOC 2 Type II', status: 'In Progress', desc: 'Controls documentation available' },
  { name: 'ISO 27001', status: 'Planned', desc: 'Information security management' },
  { name: 'CCPA', status: 'Aligned', desc: 'Privacy controls aligned with CCPA principles' },
];

const TAB_KEYS = ['trust', 'data-ethics', 'sop'] as const;
const TAB_LABELS = ['Trust & Security', 'Data Ethics', 'SOP'];

export default function TrustPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get('tab');
  const initialIndex = TAB_KEYS.indexOf(tabParam as typeof TAB_KEYS[number]);
  const [selectedTab, setSelectedTab] = useState(initialIndex >= 0 ? initialIndex : 0);

  // Sync tab from URL search params
  useEffect(() => {
    const tab = searchParams.get('tab');
    const idx = TAB_KEYS.indexOf(tab as typeof TAB_KEYS[number]);
    if (idx >= 0 && idx !== selectedTab) {
      setSelectedTab(idx);
    }
  }, [searchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleTabChange = (index: number) => {
    setSelectedTab(index);
    if (index === 0) {
      setSearchParams({});
    } else {
      setSearchParams({ tab: TAB_KEYS[index] });
    }
  };

  return (
    <div className="space-y-20">
      {/* Hero */}
      <section className="pt-8 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 rounded-full mb-6">
            <Shield className="w-5 h-5 text-green-600 dark:text-green-400" />
            <span className="text-sm font-medium text-green-700 dark:text-green-400">
              Trust & Security
            </span>
          </div>

          <h1 className="text-page-title mb-6">
            Security Built In, Not Bolted On
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
            Enterprise-grade security, version control, and audit capabilities for confident AI evaluation
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/demo">
              <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Request Security Review
              </IOSButton>
            </Link>
            <a href="mailto:security@vulcaart.art">
              <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
                Contact Security Team
              </IOSButton>
            </a>
          </div>
        </motion.div>
      </section>

      {/* Tab Switcher */}
      <section className="flex justify-center">
        <IOSSegmentedControl
          segments={TAB_LABELS}
          selectedIndex={selectedTab}
          onChange={handleTabChange}
          size="large"
        />
      </section>

      {/* Tab Content */}
      {selectedTab === 0 && <TrustContent />}
      {selectedTab === 1 && <DataEthicsPage />}
      {selectedTab === 2 && <SOPPage />}
    </div>
  );
}

/* ---- Trust & Security tab content (original TrustPage body) ---- */
function TrustContent() {
  return (
    <>
      {/* Security Principles */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Our Security Principles
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {[
            {
              icon: Eye,
              title: 'Transparency',
              desc: 'Full visibility into how your data is processed and stored',
            },
            {
              icon: Lock,
              title: 'Defense in Depth',
              desc: 'Multiple layers of security controls at every level',
            },
            {
              icon: Key,
              title: 'Least Privilege',
              desc: 'Access granted only to what is absolutely necessary',
            },
          ].map((principle) => (
            <div key={principle.title} className="text-center">
              <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <principle.icon className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {principle.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {principle.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Security Features */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Security Features
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Enterprise-grade security for your evaluation data
          </p>
        </motion.div>

        <IOSCardGrid columns={3} gap="lg">
          {securityFeatures.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              viewport={{ once: true }}
            >
              <IOSCard variant="elevated" className="h-full">
                <IOSCardHeader
                  emoji={<feature.icon className="w-6 h-6 text-green-500" />}
                  title={feature.title}
                />
                <IOSCardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {feature.description}
                  </p>
                  <ul className="space-y-2">
                    {feature.items.map((item) => (
                      <li key={item} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </IOSCardContent>
              </IOSCard>
            </motion.div>
          ))}
        </IOSCardGrid>
      </section>

      {/* Compliance */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-16 rounded-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Compliance
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Meeting industry standards and regulations
          </p>
        </motion.div>

        <div className="max-w-2xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Standard
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900 dark:text-white">
                    Description
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {complianceItems.map((item) => (
                  <tr key={item.name}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                      {item.name}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        item.status === 'Ready' || item.status === 'Aligned'
                          ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                          : item.status === 'In Progress'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                      }`}>
                        {(item.status === 'Ready' || item.status === 'Aligned') && <CheckCircle2 className="w-3 h-3" />}
                        {item.status === 'In Progress' && <AlertCircle className="w-3 h-3" />}
                        {item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                      {item.desc}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Data Handling */}
      <section>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            Your Data, Your Control
          </h2>
        </motion.div>

        <div className="max-w-3xl mx-auto">
          <IOSCard variant="elevated">
            <IOSCardContent>
              <div className="space-y-6">
                {[
                  {
                    icon: FileText,
                    title: 'Data Processing',
                    desc: 'Your model outputs are processed only for evaluation. We do not use your data to train our systems.',
                  },
                  {
                    icon: Lock,
                    title: 'Data Isolation',
                    desc: 'Enterprise workspaces are fully isolated. Your data is never mixed with other customers.',
                  },
                  {
                    icon: Trash2,
                    title: 'Data Retention',
                    desc: 'You control retention periods. Delete your data at any time with full verification.',
                  },
                  {
                    icon: Server,
                    title: 'Data Residency',
                    desc: 'Choose where your data is stored. We support multiple geographic regions.',
                  },
                ].map((item) => (
                  <div key={item.title} className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
                      <item.icon className="w-5 h-5 text-green-600 dark:text-green-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                        {item.title}
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400">
                        {item.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </IOSCardContent>
          </IOSCard>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-green-50 dark:bg-green-900/20 -mx-4 px-4 py-12 rounded-2xl text-center">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Questions About Security?
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          Our security team is available to answer questions and provide detailed documentation
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/demo">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Request Security Review
            </IOSButton>
          </Link>
          <a href="mailto:security@vulcaart.art?subject=Security%20Documentation%20Request">
            <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Request Security Documentation
            </IOSButton>
          </a>
        </div>
        <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">
          Available documentation: DPA, RoPA, Sub-processor list, Security whitepaper
        </p>
      </section>
    </>
  );
}
