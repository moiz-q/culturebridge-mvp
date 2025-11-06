import Link from 'next/link';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

// Enable static generation for landing page (SSG)
export const dynamic = 'force-static';
export const revalidate = false; // Never revalidate, pure static

// Metadata for SEO
export const metadata = {
  title: 'CultureBridge - AI-Powered Intercultural Coaching Platform',
  description: 'Connect with expert intercultural coaches through our AI-powered matching platform. Get personalized guidance for your global journey.',
  keywords: 'intercultural coaching, expat support, cultural adaptation, global nomads',
};

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-5xl font-bold mb-6">
                Navigate New Cultures with Confidence
              </h1>
              <p className="text-xl mb-8 text-blue-100 max-w-3xl mx-auto">
                Connect with expert intercultural coaches through our AI-powered matching platform. 
                Get personalized guidance for your global journey.
              </p>
              <div className="flex justify-center space-x-4">
                <Link
                  href="/auth/signup"
                  className="px-8 py-3 text-lg font-medium text-blue-600 bg-white rounded-md hover:bg-gray-100"
                >
                  Get Started
                </Link>
                <Link
                  href="/coaches"
                  className="px-8 py-3 text-lg font-medium text-white border-2 border-white rounded-md hover:bg-blue-700"
                >
                  Browse Coaches
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Why Choose CultureBridge?
              </h2>
              <p className="text-xl text-gray-600">
                Everything you need for successful cultural adaptation
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <FeatureCard
                icon={
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                }
                title="AI-Powered Matching"
                description="Our intelligent algorithm analyzes 20+ factors to match you with the perfect coach for your unique needs and goals."
              />
              
              <FeatureCard
                icon={
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                }
                title="Expert Coaches"
                description="Connect with experienced intercultural coaches who understand the challenges of living and working abroad."
              />
              
              <FeatureCard
                icon={
                  <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                }
                title="Community Support"
                description="Join a vibrant community of expats, global nomads, and professionals sharing experiences and resources."
              />
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                How It Works
              </h2>
              <p className="text-xl text-gray-600">
                Get started in three simple steps
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <StepCard
                number="1"
                title="Complete Your Profile"
                description="Tell us about your background, goals, and preferences through our comprehensive quiz."
              />
              
              <StepCard
                number="2"
                title="Get Matched"
                description="Our AI analyzes your profile and recommends the best coaches for your needs."
              />
              
              <StepCard
                number="3"
                title="Start Coaching"
                description="Book sessions, connect with your coach, and begin your cultural adaptation journey."
              />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-blue-600 text-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Start Your Journey?
            </h2>
            <p className="text-xl mb-8 text-blue-100">
              Join thousands of professionals who have successfully adapted to new cultures.
            </p>
            <Link
              href="/auth/signup"
              className="inline-block px-8 py-3 text-lg font-medium text-blue-600 bg-white rounded-md hover:bg-gray-100"
            >
              Sign Up Now
            </Link>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

function FeatureCard({ icon, title, description }: any) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center">
      <div className="text-blue-600 flex justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function StepCard({ number, title, description }: any) {
  return (
    <div className="text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-600 text-white text-2xl font-bold mb-4">
        {number}
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
