import { Link } from 'react-router-dom';
import {
  Shield,
  Eye,
  Lock,
  Database,
  UserCheck,
  Globe,
  Mail,
  Calendar,
  FileText,
  Server,
  Clock,
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
} from '../components/ios';

const lastUpdated = 'January 20, 2026';

export default function PrivacyPage() {
  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="pt-8 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-4xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-slate-900/20 rounded-full mb-6">
            <Shield className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-400">
              Privacy Policy
            </span>
          </div>

          <h1 className="text-page-title mb-6">
            Your Privacy Matters
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-4">
            We are committed to protecting your personal information and being transparent about how we collect, use, and share data.
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            Last updated: {lastUpdated}
          </p>
        </motion.div>
      </section>

      {/* Quick Summary */}
      <section className="bg-slate-50 dark:bg-slate-900/20 -mx-4 px-4 py-12 rounded-2xl">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">
            Privacy at a Glance
          </h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { icon: Database, title: 'Data Minimization', desc: 'We collect only what we need' },
              { icon: Lock, title: 'Encryption', desc: 'Your data is encrypted at rest and in transit' },
              { icon: UserCheck, title: 'Your Control', desc: 'Access, export, or delete your data anytime' },
              { icon: Globe, title: 'No Selling', desc: 'We never sell your personal data' },
            ].map((item) => (
              <div key={item.title} className="text-center">
                <div className="w-12 h-12 bg-slate-100 dark:bg-slate-900/30 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <item.icon className="w-6 h-6 text-slate-600 dark:text-slate-400" />
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{item.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="max-w-4xl mx-auto space-y-12">
        {/* Section 1: Information We Collect */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Database className="w-6 h-6 text-slate-600" />}
            title="1. Information We Collect"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mt-4 mb-2">Information You Provide</h4>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Account Information:</strong> Name, email address, organization name, and role when you create an account or request a demo.</li>
              <li><strong>Evaluation Data:</strong> AI model outputs and evaluation parameters you submit for analysis.</li>
              <li><strong>Communication:</strong> Messages you send to our support or sales teams.</li>
              <li><strong>Payment Information:</strong> Billing details processed securely through our payment providers.</li>
            </ul>

            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mt-6 mb-2">Information Collected Automatically</h4>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Usage Data:</strong> Pages visited, features used, and interaction patterns.</li>
              <li><strong>Device Information:</strong> Browser type, operating system, and device identifiers.</li>
              <li><strong>Log Data:</strong> IP addresses, access times, and referring URLs.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 2: How We Use Your Information */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Eye className="w-6 h-6 text-slate-600" />}
            title="2. How We Use Your Information"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Provide Services:</strong> Process evaluations, generate reports, and deliver our platform functionality.</li>
              <li><strong>Improve Our Platform:</strong> Analyze usage patterns to enhance features and user experience.</li>
              <li><strong>Communication:</strong> Send service updates, respond to inquiries, and provide customer support.</li>
              <li><strong>Security:</strong> Detect and prevent fraud, abuse, and security incidents.</li>
              <li><strong>Legal Compliance:</strong> Meet regulatory requirements and respond to legal requests.</li>
            </ul>
            <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-300 font-medium">
                <strong>Important:</strong> We do NOT use your evaluation data or model outputs to train our own AI systems. Your data is processed solely to provide the evaluation service you requested.
              </p>
            </div>
          </IOSCardContent>
        </IOSCard>

        {/* Section 3: Data Sharing */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Globe className="w-6 h-6 text-slate-600" />}
            title="3. Data Sharing"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              We do not sell your personal information. We may share data only in these limited circumstances:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Service Providers:</strong> Third-party vendors who help us operate our platform (hosting, analytics, payment processing) under strict confidentiality agreements.</li>
              <li><strong>Legal Requirements:</strong> When required by law, court order, or government request.</li>
              <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets, with notice to affected users.</li>
              <li><strong>With Your Consent:</strong> When you explicitly authorize sharing with specific third parties.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 4: Data Security */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Lock className="w-6 h-6 text-slate-600" />}
            title="4. Data Security"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              We implement industry-standard security measures to protect your data:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Encryption:</strong> AES-256 encryption at rest and TLS 1.3 for data in transit.</li>
              <li><strong>Access Controls:</strong> Role-based access with multi-factor authentication.</li>
              <li><strong>Infrastructure:</strong> SOC 2 compliant cloud hosting with regular security audits.</li>
              <li><strong>Monitoring:</strong> Continuous security monitoring and incident response procedures.</li>
            </ul>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              For more details, see our Trust &amp; Security documentation.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 5: Your Rights */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<UserCheck className="w-6 h-6 text-slate-600" />}
            title="5. Your Rights"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Depending on your location, you may have the following rights:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Access:</strong> Request a copy of your personal data.</li>
              <li><strong>Correction:</strong> Update or correct inaccurate information.</li>
              <li><strong>Deletion:</strong> Request deletion of your personal data.</li>
              <li><strong>Portability:</strong> Export your data in a machine-readable format.</li>
              <li><strong>Restriction:</strong> Limit how we process your data.</li>
              <li><strong>Objection:</strong> Object to certain processing activities.</li>
            </ul>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              To exercise these rights, contact us at <a href="mailto:privacy@vulcaart.art" className="text-slate-600 dark:text-slate-400 hover:underline">privacy@vulcaart.art</a>.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 6: Data Retention */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Clock className="w-6 h-6 text-slate-600" />}
            title="6. Data Retention"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Account Data:</strong> Retained while your account is active and for up to 30 days after deletion request.</li>
              <li><strong>Evaluation Data:</strong> Retained according to your plan settings. Enterprise customers can configure custom retention periods.</li>
              <li><strong>Usage Logs:</strong> Retained for up to 12 months for security and analytics purposes.</li>
              <li><strong>Legal Records:</strong> May be retained longer if required by law or for legitimate business purposes.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 7: International Transfers */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Server className="w-6 h-6 text-slate-600" />}
            title="7. International Data Transfers"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400">
              Your data may be processed in countries outside your residence. We ensure appropriate safeguards are in place:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400 mt-4">
              <li>Standard Contractual Clauses (SCCs) approved by the European Commission</li>
              <li>Data Processing Agreements (DPAs) with all sub-processors</li>
              <li>Enterprise customers can request specific data residency options</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 8: Cookies */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<FileText className="w-6 h-6 text-slate-600" />}
            title="8. Cookies and Tracking"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              We use cookies and similar technologies for:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Essential Cookies:</strong> Required for platform functionality (authentication, security).</li>
              <li><strong>Analytics Cookies:</strong> Help us understand usage patterns and improve our service.</li>
              <li><strong>Preference Cookies:</strong> Remember your settings and preferences.</li>
            </ul>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              You can manage cookie preferences through your browser settings.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 9: Children's Privacy */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<UserCheck className="w-6 h-6 text-slate-600" />}
            title="9. Children's Privacy"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400">
              VULCA is not intended for use by individuals under 16 years of age. We do not knowingly collect personal information from children. If you believe a child has provided us with personal information, please contact us immediately.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 10: Changes */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Calendar className="w-6 h-6 text-slate-600" />}
            title="10. Changes to This Policy"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400">
              We may update this Privacy Policy from time to time. We will notify you of material changes by posting the updated policy on our website and, for significant changes, by email to registered users. Your continued use of VULCA after changes constitutes acceptance of the updated policy.
            </p>
          </IOSCardContent>
        </IOSCard>
      </section>

      {/* Contact */}
      <section className="bg-slate-50 dark:bg-slate-900/20 -mx-4 px-4 py-12 rounded-2xl text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Questions About Privacy?
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          We're here to help. Contact our privacy team for any questions or to exercise your data rights.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a href="mailto:privacy@vulcaart.art">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              privacy@vulcaart.art
            </IOSButton>
          </a>
          <Link to="/">
            <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              Back to Home
            </IOSButton>
          </Link>
        </div>
        <p className="mt-6 text-sm text-gray-500 dark:text-gray-400">
          VULCA Team • Based in Asia-Pacific • Serving customers worldwide
        </p>
      </section>
    </div>
  );
}
