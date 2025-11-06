'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import MatchResults from '@/components/MatchResults';
import { api } from '@/lib/api';

function MatchPageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasProfile, setHasProfile] = useState(false);

  useEffect(() => {
    checkProfile();
  }, []);

  const checkProfile = async () => {
    try {
      const response = await api.get('/profile');
      if (response.data && response.data.quiz_data) {
        setHasProfile(true);
      }
    } catch (err) {
      setHasProfile(false);
    }
  };

  const handleFindMatches = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/match');
      setMatches(response.data.matches || []);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to find matches. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Find Your Perfect Coach</h1>
          <p className="mt-2 text-gray-600">
            Our AI-powered matching engine will find the best coaches for your needs
          </p>
        </div>

        {!hasProfile ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">
              Complete Your Profile First
            </h3>
            <p className="mt-2 text-sm text-gray-500">
              To get personalized coach matches, you need to complete your profile and quiz.
            </p>
            <button
              onClick={() => router.push('/profile/client')}
              className="mt-6 px-6 py-3 text-base font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Complete Profile
            </button>
          </div>
        ) : (
          <>
            {matches.length === 0 && !loading && (
              <div className="bg-white rounded-lg shadow p-8 text-center">
                <svg
                  className="mx-auto h-16 w-16 text-blue-500"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <h3 className="mt-4 text-xl font-medium text-gray-900">
                  Ready to Find Your Matches?
                </h3>
                <p className="mt-2 text-gray-600">
                  Click the button below to discover coaches that match your profile and goals.
                </p>
                <button
                  onClick={handleFindMatches}
                  className="mt-6 px-8 py-3 text-lg font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Find My Matches
                </button>
              </div>
            )}

            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-6">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {(loading || matches.length > 0) && (
              <div className="bg-white rounded-lg shadow p-6">
                <MatchResults matches={matches} loading={loading} />
                
                {matches.length > 0 && !loading && (
                  <div className="mt-6 pt-6 border-t border-gray-200 text-center">
                    <button
                      onClick={handleFindMatches}
                      className="px-6 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
                    >
                      Refresh Matches
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function MatchPage() {
  return (
    <ProtectedRoute allowedRoles={['client']}>
      <MatchPageContent />
    </ProtectedRoute>
  );
}
