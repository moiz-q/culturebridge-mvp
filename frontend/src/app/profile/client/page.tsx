'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/lib/api';

interface QuizData {
  target_countries: string[];
  cultural_goals: string[];
  preferred_languages: string[];
  industry: string;
  family_status: string;
  previous_expat_experience: boolean;
  timeline_urgency: number;
  budget_min: number;
  budget_max: number;
  coaching_style: string;
  specific_challenges: string[];
}

interface ClientProfile {
  first_name: string;
  last_name: string;
  phone: string;
  timezone: string;
  photo_url?: string;
  quiz_data: QuizData;
  preferences: any;
}

const COUNTRIES = [
  'United States', 'United Kingdom', 'Germany', 'France', 'Spain', 'Italy',
  'Netherlands', 'Switzerland', 'Japan', 'China', 'Singapore', 'Australia',
  'Canada', 'Brazil', 'Mexico', 'India', 'South Korea', 'UAE', 'Other'
];

const LANGUAGES = [
  'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
  'Mandarin', 'Japanese', 'Korean', 'Arabic', 'Dutch', 'Russian', 'Other'
];

const CULTURAL_GOALS = [
  'Career transition', 'Family relocation', 'Business expansion',
  'Cultural adaptation', 'Language learning', 'Networking',
  'Work-life balance', 'Leadership development', 'Other'
];

const CHALLENGES = [
  'Communication barriers', 'Cultural differences', 'Isolation',
  'Career uncertainty', 'Family adjustment', 'Legal/visa issues',
  'Housing', 'Healthcare', 'Education', 'Other'
];

const COACHING_STYLES = [
  { value: 'directive', label: 'Directive - Clear guidance and structure' },
  { value: 'collaborative', label: 'Collaborative - Partnership approach' },
  { value: 'supportive', label: 'Supportive - Emotional support focus' }
];

function ClientProfileContent() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');

  const [profile, setProfile] = useState<ClientProfile>({
    first_name: '',
    last_name: '',
    phone: '',
    timezone: 'UTC',
    quiz_data: {
      target_countries: [],
      cultural_goals: [],
      preferred_languages: [],
      industry: '',
      family_status: '',
      previous_expat_experience: false,
      timeline_urgency: 3,
      budget_min: 50,
      budget_max: 200,
      coaching_style: 'collaborative',
      specific_challenges: []
    },
    preferences: {}
  });

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get('/profile');
      if (response.data) {
        setProfile(response.data);
        if (response.data.photo_url) {
          setPhotoPreview(response.data.photo_url);
        }
        setIsEditing(false);
      } else {
        setIsEditing(true);
      }
    } catch (err: any) {
      if (err.response?.status === 404) {
        setIsEditing(true);
      } else {
        setError('Failed to load profile');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setError('Photo must be less than 5MB');
        return;
      }
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
        setError('Photo must be JPEG, PNG, or WebP');
        return;
      }
      setPhotoFile(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  const handleArrayToggle = (field: keyof QuizData, value: string) => {
    const currentArray = profile.quiz_data[field] as string[];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    
    setProfile({
      ...profile,
      quiz_data: { ...profile.quiz_data, [field]: newArray }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setSaving(true);

    try {
      // Upload photo if changed
      let photoUrl = profile.photo_url;
      if (photoFile) {
        const formData = new FormData();
        formData.append('file', photoFile);
        const uploadResponse = await api.post('/profile/photo', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        photoUrl = uploadResponse.data.photo_url;
      }

      // Update profile
      await api.put('/profile', {
        ...profile,
        photo_url: photoUrl
      });

      setSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Client Profile</h1>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                Edit Profile
              </button>
            )}
          </div>

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}
            
            {success && (
              <div className="rounded-md bg-green-50 p-4">
                <p className="text-sm text-green-800">Profile saved successfully!</p>
              </div>
            )}

            {/* Personal Information */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    First Name *
                  </label>
                  <input
                    type="text"
                    required
                    disabled={!isEditing}
                    value={profile.first_name}
                    onChange={(e) => setProfile({ ...profile, first_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Name *
                  </label>
                  <input
                    type="text"
                    required
                    disabled={!isEditing}
                    value={profile.last_name}
                    onChange={(e) => setProfile({ ...profile, last_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    disabled={!isEditing}
                    value={profile.phone}
                    onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Timezone *
                  </label>
                  <input
                    type="text"
                    required
                    disabled={!isEditing}
                    value={profile.timezone}
                    onChange={(e) => setProfile({ ...profile, timezone: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                    placeholder="e.g., America/New_York"
                  />
                </div>
              </div>

              {/* Photo Upload */}
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Profile Photo
                </label>
                {photoPreview && (
                  <img
                    src={photoPreview}
                    alt="Profile"
                    className="w-32 h-32 rounded-full object-cover mb-2"
                  />
                )}
                {isEditing && (
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handlePhotoChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Max 5MB. JPEG, PNG, or WebP format.
                </p>
              </div>
            </div>

            {/* Quiz Section */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Matching Quiz</h2>
              
              {/* Target Countries */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Countries * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {COUNTRIES.map(country => (
                    <label key={country} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.quiz_data.target_countries.includes(country)}
                        onChange={() => handleArrayToggle('target_countries', country)}
                        className="mr-2"
                      />
                      <span className="text-sm">{country}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Cultural Goals */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cultural Adaptation Goals * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {CULTURAL_GOALS.map(goal => (
                    <label key={goal} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.quiz_data.cultural_goals.includes(goal)}
                        onChange={() => handleArrayToggle('cultural_goals', goal)}
                        className="mr-2"
                      />
                      <span className="text-sm">{goal}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Preferred Languages */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Languages * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {LANGUAGES.map(lang => (
                    <label key={lang} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.quiz_data.preferred_languages.includes(lang)}
                        onChange={() => handleArrayToggle('preferred_languages', lang)}
                        className="mr-2"
                      />
                      <span className="text-sm">{lang}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Industry */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Industry/Profession *
                </label>
                <input
                  type="text"
                  required
                  disabled={!isEditing}
                  value={profile.quiz_data.industry}
                  onChange={(e) => setProfile({
                    ...profile,
                    quiz_data: { ...profile.quiz_data, industry: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                />
              </div>

              {/* Family Status */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Family Status *
                </label>
                <select
                  required
                  disabled={!isEditing}
                  value={profile.quiz_data.family_status}
                  onChange={(e) => setProfile({
                    ...profile,
                    quiz_data: { ...profile.quiz_data, family_status: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                >
                  <option value="">Select...</option>
                  <option value="single">Single</option>
                  <option value="married">Married</option>
                  <option value="married_with_children">Married with Children</option>
                  <option value="single_parent">Single Parent</option>
                </select>
              </div>

              {/* Previous Experience */}
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    disabled={!isEditing}
                    checked={profile.quiz_data.previous_expat_experience}
                    onChange={(e) => setProfile({
                      ...profile,
                      quiz_data: { ...profile.quiz_data, previous_expat_experience: e.target.checked }
                    })}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    I have previous expat experience
                  </span>
                </label>
              </div>

              {/* Timeline Urgency */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Timeline Urgency * (1 = Not urgent, 5 = Very urgent)
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  disabled={!isEditing}
                  value={profile.quiz_data.timeline_urgency}
                  onChange={(e) => setProfile({
                    ...profile,
                    quiz_data: { ...profile.quiz_data, timeline_urgency: parseInt(e.target.value) }
                  })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Not urgent</span>
                  <span className="font-semibold">{profile.quiz_data.timeline_urgency}</span>
                  <span>Very urgent</span>
                </div>
              </div>

              {/* Budget Range */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Budget Range (USD per hour) *
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Minimum</label>
                    <input
                      type="number"
                      min="25"
                      max="500"
                      required
                      disabled={!isEditing}
                      value={profile.quiz_data.budget_min}
                      onChange={(e) => setProfile({
                        ...profile,
                        quiz_data: { ...profile.quiz_data, budget_min: parseInt(e.target.value) }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Maximum</label>
                    <input
                      type="number"
                      min="25"
                      max="500"
                      required
                      disabled={!isEditing}
                      value={profile.quiz_data.budget_max}
                      onChange={(e) => setProfile({
                        ...profile,
                        quiz_data: { ...profile.quiz_data, budget_max: parseInt(e.target.value) }
                      })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                    />
                  </div>
                </div>
              </div>

              {/* Coaching Style */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Coaching Style *
                </label>
                <div className="space-y-2">
                  {COACHING_STYLES.map(style => (
                    <label key={style.value} className="flex items-start">
                      <input
                        type="radio"
                        disabled={!isEditing}
                        checked={profile.quiz_data.coaching_style === style.value}
                        onChange={() => setProfile({
                          ...profile,
                          quiz_data: { ...profile.quiz_data, coaching_style: style.value }
                        })}
                        className="mt-1 mr-2"
                      />
                      <span className="text-sm">{style.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Specific Challenges */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Specific Challenges * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {CHALLENGES.map(challenge => (
                    <label key={challenge} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.quiz_data.specific_challenges.includes(challenge)}
                        onChange={() => handleArrayToggle('specific_challenges', challenge)}
                        className="mr-2"
                      />
                      <span className="text-sm">{challenge}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            {isEditing && (
              <div className="flex justify-end space-x-4 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    fetchProfile();
                  }}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Profile'}
                </button>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

export default function ClientProfilePage() {
  return (
    <ProtectedRoute allowedRoles={['client']}>
      <ClientProfileContent />
    </ProtectedRoute>
  );
}
