'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import CoachCard from '@/components/CoachCard';
import { api } from '@/lib/api';

const LANGUAGES = ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Mandarin', 'Japanese'];
const COUNTRIES = ['United States', 'United Kingdom', 'Germany', 'France', 'Spain', 'Italy', 'Japan', 'China'];
const EXPERTISE = ['Career Transition', 'Cultural Adaptation', 'Leadership Development', 'Family Relocation'];

function CoachesListContent() {
  const { user } = useAuth();
  const [coaches, setCoaches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [selectedCountries, setSelectedCountries] = useState<string[]>([]);
  const [selectedExpertise, setSelectedExpertise] = useState<string[]>([]);
  const [minRate, setMinRate] = useState<number>(25);
  const [maxRate, setMaxRate] = useState<number>(500);

  useEffect(() => {
    fetchCoaches();
  }, [selectedLanguages, selectedCountries, selectedExpertise, minRate, maxRate]);

  const fetchCoaches = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedLanguages.length > 0) params.append('languages', selectedLanguages.join(','));
      if (selectedCountries.length > 0) params.append('countries', selectedCountries.join(','));
      if (selectedExpertise.length > 0) params.append('expertise', selectedExpertise.join(','));
      params.append('min_rate', minRate.toString());
      params.append('max_rate', maxRate.toString());

      const response = await api.get(`/coaches?${params.toString()}`);
      setCoaches(response.data.coaches || []);
    } catch (err: any) {
      setError('Failed to load coaches');
    } finally {
      setLoading(false);
    }
  };

  const toggleFilter = (filterArray: string[], setFilter: Function, value: string) => {
    if (filterArray.includes(value)) {
      setFilter(filterArray.filter(item => item !== value));
    } else {
      setFilter([...filterArray, value]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Find Your Coach</h1>
          <p className="mt-2 text-gray-600">
            Browse our network of intercultural coaches
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>

              {/* Languages Filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Languages</h3>
                <div className="space-y-2">
                  {LANGUAGES.map(lang => (
                    <label key={lang} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedLanguages.includes(lang)}
                        onChange={() => toggleFilter(selectedLanguages, setSelectedLanguages, lang)}
                        className="mr-2"
                      />
                      <span className="text-sm">{lang}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Countries Filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Countries</h3>
                <div className="space-y-2">
                  {COUNTRIES.map(country => (
                    <label key={country} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedCountries.includes(country)}
                        onChange={() => toggleFilter(selectedCountries, setSelectedCountries, country)}
                        className="mr-2"
                      />
                      <span className="text-sm">{country}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Expertise Filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Expertise</h3>
                <div className="space-y-2">
                  {EXPERTISE.map(exp => (
                    <label key={exp} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={selectedExpertise.includes(exp)}
                        onChange={() => toggleFilter(selectedExpertise, setSelectedExpertise, exp)}
                        className="mr-2"
                      />
                      <span className="text-sm">{exp}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Price Range Filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Hourly Rate</h3>
                <div className="space-y-2">
                  <div>
                    <label className="text-xs text-gray-500">Min: ${minRate}</label>
                    <input
                      type="range"
                      min="25"
                      max="500"
                      value={minRate}
                      onChange={(e) => setMinRate(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500">Max: ${maxRate}</label>
                    <input
                      type="range"
                      min="25"
                      max="500"
                      value={maxRate}
                      onChange={(e) => setMaxRate(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={() => {
                  setSelectedLanguages([]);
                  setSelectedCountries([]);
                  setSelectedExpertise([]);
                  setMinRate(25);
                  setMaxRate(500);
                }}
                className="w-full px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Coaches List */}
          <div className="lg:col-span-3">
            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              </div>
            ) : coaches.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow">
                <p className="text-gray-600">No coaches found matching your filters.</p>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Showing {coaches.length} coach{coaches.length !== 1 ? 'es' : ''}
                </p>
                {coaches.map(coach => (
                  <CoachCard key={coach.id} coach={coach} />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CoachesPage() {
  return (
    <ProtectedRoute>
      <CoachesListContent />
    </ProtectedRoute>
  );
}
