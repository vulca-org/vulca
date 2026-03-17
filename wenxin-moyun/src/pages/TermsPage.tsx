import { Link } from 'react-router-dom';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  Scale,
  Shield,
  Users,
  CreditCard,
  Ban,
  RefreshCw,
  Gavel,
  Mail,
  Calendar,
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
} from '../components/ios';

const lastUpdated = 'January 20, 2026';

export default function TermsPage() {
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
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-amber-50 dark:bg-amber-900/20 rounded-full mb-6">
            <Scale className="w-5 h-5 text-amber-700 dark:text-amber-400" />
            <span className="text-sm font-medium text-amber-700 dark:text-amber-400">
              Terms of Service
            </span>
          </div>

          <h1 className="text-page-title mb-6">
            Terms of Service
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-4">
            Please read these terms carefully before using the VULCA platform.
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500">
            Last updated: {lastUpdated}
          </p>
        </motion.div>
      </section>

      {/* Quick Summary */}
      <section className="bg-amber-50 dark:bg-amber-900/20 -mx-4 px-4 py-12 rounded-2xl">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">
            Key Points
          </h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { icon: CheckCircle2, title: 'Fair Use', desc: 'Use our platform for legitimate evaluation purposes' },
              { icon: Shield, title: 'Your Data', desc: 'You retain ownership of your evaluation data' },
              { icon: CreditCard, title: 'Billing', desc: 'Clear pricing with no hidden fees' },
              { icon: Scale, title: 'Disputes', desc: 'Good faith resolution process' },
            ].map((item) => (
              <div key={item.title} className="text-center">
                <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900/30 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <item.icon className="w-6 h-6 text-amber-700 dark:text-amber-400" />
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
        {/* Section 1: Acceptance */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<FileText className="w-6 h-6 text-[#C87F4A]" />}
            title="1. Acceptance of Terms"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400">
              By accessing or using VULCA ("the Service"), you agree to be bound by these Terms of Service ("Terms"). If you are using the Service on behalf of an organization, you represent that you have authority to bind that organization to these Terms.
            </p>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              If you do not agree to these Terms, do not use the Service.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 2: Description of Service */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<CheckCircle2 className="w-6 h-6 text-[#C87F4A]" />}
            title="2. Description of Service"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              VULCA provides AI model evaluation services, including:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>Cultural understanding assessment across 47 dimensions and 8 cultural perspectives</li>
              <li>Benchmark evaluation using our curated artwork dataset</li>
              <li>Comparative analysis and diagnostic reports</li>
              <li>API access for programmatic evaluation</li>
              <li>Enterprise features including custom benchmarks and continuous monitoring</li>
            </ul>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              Service features may vary. See our GitHub repository for details.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 3: Account Terms */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Users className="w-6 h-6 text-[#C87F4A]" />}
            title="3. Account Terms"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>You must provide accurate and complete registration information.</li>
              <li>You are responsible for maintaining the security of your account credentials.</li>
              <li>You must be at least 16 years old to use the Service.</li>
              <li>One person or organization may not maintain multiple free accounts.</li>
              <li>You are responsible for all activity that occurs under your account.</li>
              <li>You must notify us immediately of any unauthorized access or security breach.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 4: Acceptable Use */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Shield className="w-6 h-6 text-[#C87F4A]" />}
            title="4. Acceptable Use"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              You agree to use the Service only for lawful purposes and in accordance with these Terms. You agree NOT to:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>Use the Service to evaluate models for illegal purposes or to develop harmful AI systems</li>
              <li>Attempt to gain unauthorized access to our systems or other users' accounts</li>
              <li>Reverse engineer, decompile, or attempt to extract source code from the Service</li>
              <li>Use automated tools to scrape or extract data beyond API rate limits</li>
              <li>Resell or redistribute evaluation reports without authorization</li>
              <li>Submit content that infringes intellectual property rights</li>
              <li>Interfere with or disrupt the integrity or performance of the Service</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 5: Prohibited Uses */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Ban className="w-6 h-6 text-[#C87F4A]" />}
            title="5. Prohibited Uses"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg mb-4">
              <p className="text-sm text-red-800 dark:text-red-300">
                The following uses are strictly prohibited and will result in immediate account termination:
              </p>
            </div>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>Evaluating models intended for surveillance or mass monitoring</li>
              <li>Developing AI systems designed to deceive or manipulate users</li>
              <li>Creating deepfakes or synthetic media for malicious purposes</li>
              <li>Any use that violates applicable export control laws</li>
              <li>Submitting evaluation content containing illegal material</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 6: Intellectual Property */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<FileText className="w-6 h-6 text-[#C87F4A]" />}
            title="6. Intellectual Property"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Our Property</h4>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              The Service, including the VULCA framework, benchmark datasets, evaluation algorithms, and documentation, is owned by VULCA and protected by intellectual property laws. The VULCA name, logo, and related marks are our trademarks.
            </p>

            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Your Property</h4>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              You retain ownership of all data you submit to the Service, including your model outputs and evaluation results. By using the Service, you grant us a limited license to process your data solely to provide the evaluation service.
            </p>

            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Report Usage</h4>
            <p className="text-gray-600 dark:text-gray-400">
              You may use evaluation reports for internal purposes and publications with proper attribution. Public disclosure of evaluation methodology requires citing VULCA as the evaluation platform.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 7: Payment Terms */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<CreditCard className="w-6 h-6 text-[#C87F4A]" />}
            title="7. Payment Terms"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Pricing:</strong> VULCA is open source under Apache 2.0. Self-hosted usage is free.</li>
              <li><strong>Billing:</strong> Paid plans are billed in advance on a monthly or annual basis.</li>
              <li><strong>Pilot Engagements:</strong> One-time payments are due upon signing the engagement agreement.</li>
              <li><strong>Refunds:</strong> We offer refunds within 14 days of purchase if you are not satisfied, provided no evaluation reports have been generated.</li>
              <li><strong>Taxes:</strong> Prices exclude applicable taxes, which will be added at checkout.</li>
              <li><strong>Late Payment:</strong> Accounts with overdue payments may have service access suspended.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 8: Service Modifications */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<RefreshCw className="w-6 h-6 text-[#C87F4A]" />}
            title="8. Service Modifications & Termination"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Our Rights</h4>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400 mb-4">
              <li>We may modify, suspend, or discontinue features with reasonable notice.</li>
              <li>We may terminate accounts that violate these Terms.</li>
              <li>We may refuse service to anyone for any reason.</li>
            </ul>

            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Your Rights</h4>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>You may cancel your subscription at any time through your account settings.</li>
              <li>You may request data export before account termination.</li>
              <li>Annual subscriptions may be refunded on a pro-rata basis for significant service changes.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 9: Disclaimer & Limitations */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<AlertTriangle className="w-6 h-6 text-[#C87F4A]" />}
            title="9. Disclaimers & Limitations"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg mb-4">
              <p className="text-sm text-yellow-800 dark:text-yellow-300">
                <strong>Important:</strong> Please read this section carefully as it limits our liability.
              </p>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED. WE DO NOT WARRANT THAT:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>The Service will be uninterrupted or error-free</li>
              <li>Evaluation results will be perfectly accurate or suitable for any specific purpose</li>
              <li>The Service will meet all your requirements</li>
            </ul>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, OUR TOTAL LIABILITY FOR ANY CLAIMS ARISING FROM THESE TERMS OR USE OF THE SERVICE SHALL NOT EXCEED THE AMOUNT YOU PAID US IN THE 12 MONTHS PRECEDING THE CLAIM.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 10: Indemnification */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Shield className="w-6 h-6 text-[#C87F4A]" />}
            title="10. Indemnification"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400">
              You agree to indemnify and hold harmless VULCA, its affiliates, and their respective officers, directors, employees, and agents from any claims, damages, or expenses (including reasonable attorneys' fees) arising from:
            </p>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400 mt-4">
              <li>Your use of the Service</li>
              <li>Your violation of these Terms</li>
              <li>Your violation of any third-party rights</li>
              <li>Content you submit to the Service</li>
            </ul>
          </IOSCardContent>
        </IOSCard>

        {/* Section 11: Governing Law */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Gavel className="w-6 h-6 text-[#C87F4A]" />}
            title="11. Governing Law & Disputes"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              These Terms are governed by the laws of Taiwan, without regard to conflict of law principles.
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              Any disputes arising from these Terms or use of the Service shall be resolved through:
            </p>
            <ol className="space-y-2 text-gray-600 dark:text-gray-400 mt-4 list-decimal list-inside">
              <li><strong>Good Faith Negotiation:</strong> Parties shall first attempt to resolve disputes informally.</li>
              <li><strong>Mediation:</strong> If negotiation fails, disputes may be submitted to mediation.</li>
              <li><strong>Arbitration:</strong> Unresolved disputes shall be settled by binding arbitration in Taipei, Taiwan.</li>
            </ol>
          </IOSCardContent>
        </IOSCard>

        {/* Section 12: Changes */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<Calendar className="w-6 h-6 text-[#C87F4A]" />}
            title="12. Changes to Terms"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <p className="text-gray-600 dark:text-gray-400">
              We may update these Terms from time to time. For material changes, we will provide at least 30 days notice via email or prominent notice on the Service. Your continued use of the Service after changes take effect constitutes acceptance of the revised Terms.
            </p>
            <p className="text-gray-600 dark:text-gray-400 mt-4">
              If you disagree with the changes, you may terminate your account before the new Terms take effect.
            </p>
          </IOSCardContent>
        </IOSCard>

        {/* Section 13: General */}
        <IOSCard variant="elevated">
          <IOSCardHeader
            emoji={<FileText className="w-6 h-6 text-[#C87F4A]" />}
            title="13. General Provisions"
          />
          <IOSCardContent className="prose dark:prose-invert max-w-none">
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li><strong>Entire Agreement:</strong> These Terms constitute the entire agreement between you and VULCA.</li>
              <li><strong>Severability:</strong> If any provision is found unenforceable, the remaining provisions remain in effect.</li>
              <li><strong>No Waiver:</strong> Failure to enforce any provision does not waive our right to enforce it later.</li>
              <li><strong>Assignment:</strong> You may not assign these Terms without our consent. We may assign our rights freely.</li>
              <li><strong>Force Majeure:</strong> We are not liable for failures due to circumstances beyond our reasonable control.</li>
            </ul>
          </IOSCardContent>
        </IOSCard>
      </section>

      {/* Contact */}
      <section className="bg-amber-50 dark:bg-amber-900/20 -mx-4 px-4 py-12 rounded-2xl text-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Questions About Terms?
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
          If you have questions about these Terms of Service, please contact us.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <a href="mailto:legal@vulcaart.art">
            <IOSButton variant="primary" size="lg" className="flex items-center gap-2">
              <Mail className="w-5 h-5" />
              legal@vulcaart.art
            </IOSButton>
          </a>
          <Link to="/privacy">
            <IOSButton variant="secondary" size="lg" className="flex items-center gap-2">
              <Shield className="w-5 h-5" />
              View Privacy Policy
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
