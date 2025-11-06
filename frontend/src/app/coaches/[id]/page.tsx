'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/lib/api';

function CoachDetailContent() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const [coach, setCoach] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (params.id) {
      fetchCoach();
    }
  }, [params.id]);

  const fetchCoach = async () => {
    try {
      const response = await api.get(`/coaches/${params.id}`);
      setCoach(response.data);
    } catch (err: any) {
      setError('Failed to load coach details');
    } finally {
      setLoading(false);
    }
  };

  const handleBookSession = () => {
    router.push(`/booking?coach_id=${params.id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !coach) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Coach not found'}</p>
          <button
            onClick={() => router.push('/coaches')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Back to Coaches
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => router.back()}
          className="mb-4 text-blue-600 hover:text-blue-700 flex items-center"
        >
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-8">
            <div className="flex items-start space-x-6">
              {coach.photo_url ? (
                <img
                  src={coach.photo_url}
                  alt={`${coach.first_name} ${coach.last_name}`}
                  className="w-32 h-32 rounded-full object-cover border-4 border-white"
                />
              ) : (
                <div className="w-32 h-32 rounded-full bg-white flex items-center justify-center border-4 border-white">
                  <span className="text-4xl text-gray-500">
                    {coach.first_name[0]}{coach.last_name[0]}
                  </span>
                </div>
              )}
              
              <div className="flex-1 text-white">
                <h1 className="text-3xl font-bold">
                  {coach.first_name} {coach.last_name}
                </h1>
                <div className="flex items-center mt-2">
                  <svg className="w-5 h-5 text-yellow-300 fill-current" viewBox="0 0 20 20">
                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                  </svg>
                  <span className="ml-2 text-lg">
                    {coach.rating.toFixed(1)} ({coach.total_sessions} sessions)
                  </span>
                </div>
                <div className="mt-4 text-2xl font-bold">
                  ${coach.hourly_rate}/hour
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Bio */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">About</h2>
              <p className="text-gray-700 whitespace-pre-line">{coach.bio}</p>
            </div>

            {/* Intro Video */}
            {coach.intro_video_url && (
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-3">Introduction Video</h2>
                <a
                  href={coach.intro_video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-700 flex items-center"
                >
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" />
                  </svg>
                  Watch Video
                </a>
              </div>
            )}

            {/* Expertise */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Expertise</h2>
              <div className="flex flex-wrap gap-2">
                {coach.expertise.map((exp: string, idx: number) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                  >
                    {exp}
                  </span>
                ))}
              </div>
            </div>

            {/* Languages */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Languages</h2>
              <div className="flex flex-wrap gap-2">
                {coach.languages.map((lang: string, idx: number) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800"
                  >
                    {lang}
                  </span>
                ))}
              </div>
            </div>

            {/* Countries */}
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">Countries of Experience</h2>
              <div className="flex flex-wrap gap-2">
                {coach.countries.map((country: string, idx: number) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800"
                  >
                    {country}
                  </span>
                ))}
              </div>
            </div>

            {/* Book Session Button */}
            {user?.role === 'client' && (
              <div className="pt-6 border-t border-gray-200">
                <button
                  onClick={handleBookSession}
                  className="w-full px-6 py-3 text-lg font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Book a Session
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CoachDetailPage() {
  return (
    <ProtectedRoute>
      <CoachDetailContent />
    </ProtectedRoute>
  );
}
