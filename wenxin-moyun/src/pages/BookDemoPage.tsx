import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Calendar,
  CheckCircle2,
  Building2,
  GraduationCap,
  Palette,
  Clock,
  Users,
  ArrowRight,
  Send,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { motion } from 'framer-motion';
import {
  IOSButton,
  IOSCard,
  IOSCardHeader,
  IOSCardContent,
} from '../components/ios';
import { leadsApi, type LeadSubmitData } from '../services/api';

const benefits = [
  {
    icon: CheckCircle2,
    title: '47D Framework Overview',
    desc: 'See how our 47-dimension evaluation works',
  },
  {
    icon: Users,
    title: '8 Cultural Perspectives',
    desc: 'Understand multi-perspective evaluation',
  },
  {
    icon: Clock,
    title: '30-Minute Session',
    desc: 'Quick intro tailored to your needs',
  },
];

type UseCase = 'ai_labs' | 'research' | 'museums' | 'enterprise' | 'other';

const useCases: { id: UseCase; icon: typeof Building2; title: string; desc: string; color: string }[] = [
  {
    id: 'ai_labs',
    icon: Building2,
    title: 'AI Labs',
    desc: 'Pre-release cultural audits',
    color: 'blue',
  },
  {
    id: 'research',
    icon: GraduationCap,
    title: 'Research',
    desc: 'Academic benchmarking',
    color: 'purple',
  },
  {
    id: 'museums',
    icon: Palette,
    title: 'Museums',
    desc: 'Cultural AI validation',
    color: 'orange',
  },
];

const timelineOptions = [
  { value: 'immediate', label: 'Immediate (This month)' },
  { value: '1-3_months', label: '1-3 months' },
  { value: '3-6_months', label: '3-6 months' },
  { value: 'exploring', label: 'Just exploring' },
];

const dataSensitivityOptions = [
  { value: 'public', label: 'Public' },
  { value: 'internal', label: 'Internal' },
  { value: 'confidential', label: 'Confidential' },
];

const deploymentOptions = [
  { value: 'public_demo', label: 'Public demo' },
  { value: 'private_workspace', label: 'Private workspace' },
  { value: 'on_prem', label: 'On-premise' },
];

interface FormData {
  name: string;
  email: string;
  organization: string;
  role: string;
  use_case: UseCase;
  timeline: string;
  data_sensitivity: string;
  deployment_preference: string;
  message: string;
}

interface FormErrors {
  name?: string;
  email?: string;
}

interface LeadErrorShape {
  response?: {
    data?: {
      detail?: string;
    };
  };
}

export default function BookDemoPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    organization: '',
    role: '',
    use_case: 'other',
    timeline: '',
    data_sensitivity: '',
    deployment_preference: '',
    message: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleUseCaseSelect = (useCase: UseCase) => {
    setFormData((prev) => ({ ...prev, use_case: useCase }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const submitData: LeadSubmitData = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        organization: formData.organization.trim() || undefined,
        role: formData.role.trim() || undefined,
        use_case: formData.use_case,
        timeline: formData.timeline || undefined,
        message: formData.message.trim() || undefined,
        source_page: 'book_demo',
      };

      const response = await leadsApi.submitLead(submitData);

      if (response.success) {
        // Navigate to confirmation page with lead info
        navigate('/demo/confirmation', {
          state: {
            leadId: response.lead_id,
            name: formData.name,
            email: formData.email,
          },
        });
      }
    } catch (error) {
      const leadError = error as LeadErrorShape;
      console.error('Failed to submit lead:', error);
      setSubmitError(
        leadError.response?.data?.detail ||
          'Failed to submit your request. Please try again or contact us directly.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="pt-8 pb-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center max-w-3xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-slate-900/20 rounded-full mb-6">
            <Calendar className="w-5 h-5 text-slate-700 dark:text-slate-500" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-500">
              Schedule a Demo
            </span>
          </div>

          <h1 className="text-page-title mb-6">
            Book a Demo
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            See how VULCA can help you evaluate AI models for cultural understanding
          </p>
        </motion.div>
      </section>

      {/* Main Content */}
      <section className="grid lg:grid-cols-2 gap-12">
        {/* Left: Info */}
        <div className="space-y-8">
          {/* What to expect */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              What to Expect
            </h2>
            <div className="space-y-4">
              {benefits.map((benefit) => (
                <div key={benefit.title} className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-slate-100 dark:bg-slate-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
                    <benefit.icon className="w-5 h-5 text-slate-700 dark:text-slate-500" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {benefit.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{benefit.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Select use case */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              I'm interested in...
            </h2>
            <div className="space-y-3">
              {useCases.map((useCase) => (
                <button
                  key={useCase.id}
                  type="button"
                  onClick={() => handleUseCaseSelect(useCase.id)}
                  className={`w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all ${
                    formData.use_case === useCase.id
                      ? 'border-slate-600 bg-slate-50 dark:bg-slate-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <useCase.icon
                    className={`w-6 h-6 ${
                      useCase.color === 'blue'
                        ? 'text-slate-600'
                        : useCase.color === 'purple'
                          ? 'text-amber-600'
                          : 'text-orange-500'
                    }`}
                  />
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900 dark:text-white">{useCase.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{useCase.desc}</p>
                  </div>
                  {formData.use_case === useCase.id && (
                    <CheckCircle2 className="w-5 h-5 text-slate-600 ml-auto" />
                  )}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Additional links */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="pt-4"
          >
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Want to explore first?</p>
            <div className="flex flex-wrap gap-3">
              <Link to="/canvas">
                <IOSButton variant="secondary" size="sm" className="flex items-center gap-1">
                  Try Public Demo
                  <ArrowRight className="w-4 h-4" />
                </IOSButton>
              </Link>
              <Link to="/research">
                <IOSButton variant="secondary" size="sm" className="flex items-center gap-1">
                  Read Documentation
                </IOSButton>
              </Link>
            </div>
          </motion.div>
        </div>

        {/* Right: Form */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <IOSCard variant="elevated" className="overflow-hidden">
            <IOSCardHeader
              emoji={<Send className="w-6 h-6 text-slate-600" />}
              title="Request a Demo"
              subtitle="We'll respond within 24 hours • Or book directly via Cal.com"
            />
            <IOSCardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Name */}
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3 rounded-xl border ${
                      errors.name
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-200 dark:border-gray-700 focus:ring-slate-600'
                    } bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2`}
                    placeholder="Dr. Jane Smith"
                  />
                  {errors.name && (
                    <p className="mt-1 text-sm text-red-500 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.name}
                    </p>
                  )}
                </div>

                {/* Email */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Email <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-3 rounded-xl border ${
                      errors.email
                        ? 'border-red-500 focus:ring-red-500'
                        : 'border-gray-200 dark:border-gray-700 focus:ring-slate-600'
                    } bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2`}
                    placeholder="jane.smith@university.edu"
                  />
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-500 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      {errors.email}
                    </p>
                  )}
                </div>

                {/* Organization */}
                <div>
                  <label
                    htmlFor="organization"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Organization
                  </label>
                  <input
                    type="text"
                    id="organization"
                    name="organization"
                    value={formData.organization}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-600"
                    placeholder="Stanford University"
                  />
                </div>

                {/* Role */}
                <div>
                  <label
                    htmlFor="role"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Role / Title
                  </label>
                  <input
                    type="text"
                    id="role"
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-600"
                    placeholder="Research Scientist"
                  />
                </div>

                {/* Timeline */}
                <div>
                  <label
                    htmlFor="timeline"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    When do you need this?
                  </label>
                  <select
                    id="timeline"
                    name="timeline"
                    value={formData.timeline}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-600"
                  >
                    <option value="">Select timeline...</option>
                    {timelineOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Data Sensitivity */}
                <div>
                  <label
                    htmlFor="data_sensitivity"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Data Sensitivity Level
                  </label>
                  <select
                    id="data_sensitivity"
                    name="data_sensitivity"
                    value={formData.data_sensitivity}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-600"
                  >
                    <option value="">Select data sensitivity...</option>
                    {dataSensitivityOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Deployment Preference */}
                <div>
                  <label
                    htmlFor="deployment_preference"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Preferred Deployment
                  </label>
                  <select
                    id="deployment_preference"
                    name="deployment_preference"
                    value={formData.deployment_preference}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-600"
                  >
                    <option value="">Select deployment preference...</option>
                    {deploymentOptions.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Message */}
                <div>
                  <label
                    htmlFor="message"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Tell us more about your use case
                  </label>
                  <textarea
                    id="message"
                    name="message"
                    value={formData.message}
                    onChange={handleInputChange}
                    rows={4}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-slate-600 resize-none"
                    placeholder="What specific challenges are you looking to address with VULCA?"
                  />
                </div>

                {/* Submit Error */}
                {submitError && (
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-xl flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-800 dark:text-red-200">
                        Submission Failed
                      </p>
                      <p className="text-sm text-red-600 dark:text-red-300">{submitError}</p>
                    </div>
                  </div>
                )}

                {/* Submit Button */}
                <IOSButton
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full flex items-center justify-center gap-2"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Request Demo
                    </>
                  )}
                </IOSButton>

                {/* Cal.com Direct Booking */}
                <div className="text-center pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                    Prefer to book directly?
                  </p>
                  <a
                    href="https://cal.com/vulcaart/demo"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <IOSButton
                      type="button"
                      variant="secondary"
                      size="md"
                      className="w-full flex items-center justify-center gap-2"
                    >
                      <Calendar className="w-5 h-5" />
                      Schedule via Cal.com
                    </IOSButton>
                  </a>
                </div>
              </form>
            </IOSCardContent>
          </IOSCard>

          {/* Alternative contact */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Prefer email? Contact us at{' '}
              <a
                href="mailto:demo@vulcaart.art"
                className="text-slate-700 dark:text-slate-500 hover:underline"
              >
                demo@vulcaart.art
              </a>
            </p>
          </div>
        </motion.div>
      </section>

      {/* Trust indicators */}
      <section className="bg-gray-50 dark:bg-gray-900/50 -mx-4 px-4 py-8 rounded-2xl">
        <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-green-500" />
            No credit card required
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-600" />
            Response within 24 hours
          </div>
          <div className="flex items-center gap-2">
            <Users className="w-4 h-4 text-amber-600" />
            Tailored to your use case
          </div>
        </div>
      </section>
    </div>
  );
}
