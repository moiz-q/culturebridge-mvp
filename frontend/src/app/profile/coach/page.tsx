'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import { api } from '@/lib/api';

interface CoachProfile {
  first_name: string;
  last_name: string;
  photo_url?: string;
  bio: string;
  intro_video_url?: string;
  expertise: string[];
  languages: string[];
  countries: string[];
  hourly_rate: number;
  currency: string;
  availability: any;
}

const LANGUAGES = [
  'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
  'Mandarin', 'Japanese', 'Korean', 'Arabic', 'Dutch', 'Russian',
  'Hindi', 'Turkish', 'Polish', 'Swedish', 'Norwegian', 'Danish', 'Other'
];

const COUNTRIES = [
  'United States', 'United Kingdom', 'Germany', 'France', 'Spain', 'Italy',
  'Netherlands', 'Switzerland', 'Japan', 'China', 'Singapore', 'Australia',
  'Canada', 'Brazil', 'Mexico', 'India', 'South Korea', 'UAE', 'Belgium',
  'Austria', 'Sweden', 'Norway', 'Denmark', 'Finland', 'Other'
];

const EXPERTISE_AREAS = [
  'Career Transition', 'Cultural Adaptation', 'Leadership Development',
  'Family Relocation', 'Language Learning', 'Business Expansion',
  'Work-Life Balance', 'Networking', 'Communication Skills',
  'Conflict Resolution', 'Team Building', 'Executive Coaching', 'Other'
];

function CoachProfileContent() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');

  const [profile, setProfile] = useState<CoachProfile>({
    first_name: '',
    last_name: '',
    bio: '',
    intro_video_url: '',
    expertise: [],
    languages: [],
    countries: [],
    hourly_rate: 100,
    currency: 'USD',
    availability: {}
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

  const handleArrayToggle = (field: keyof CoachProfile, value: string) => {
    const currentArray = profile[field] as string[];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(item => item !== value)
      : [...currentArray, value];
    
    setProfile({ ...profile, [field]: newArray });
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
            <h1 className="text-2xl font-bold text-gray-900">Coach Profile</h1>
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

            {/* Professional Information */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Professional Information</h2>
              
              {/* Bio */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bio *
                </label>
                <textarea
                  required
                  disabled={!isEditing}
                  value={profile.bio}
                  onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                  rows={5}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  placeholder="Tell clients about your background, experience, and coaching philosophy..."
                />
              </div>

              {/* Intro Video URL */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Intro Video URL (Optional)
                </label>
                <input
                  type="url"
                  disabled={!isEditing}
                  value={profile.intro_video_url}
                  onChange={(e) => setProfile({ ...profile, intro_video_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  placeholder="https://youtube.com/..."
                />
              </div>

              {/* Expertise */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Expertise Areas * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {EXPERTISE_AREAS.map(area => (
                    <label key={area} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.expertise.includes(area)}
                        onChange={() => handleArrayToggle('expertise', area)}
                        className="mr-2"
                      />
                      <span className="text-sm">{area}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Languages */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Languages Spoken * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {LANGUAGES.map(lang => (
                    <label key={lang} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.languages.includes(lang)}
                        onChange={() => handleArrayToggle('languages', lang)}
                        className="mr-2"
                      />
                      <span className="text-sm">{lang}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Countries */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Countries of Experience * (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {COUNTRIES.map(country => (
                    <label key={country} className="flex items-center">
                      <input
                        type="checkbox"
                        disabled={!isEditing}
                        checked={profile.countries.includes(country)}
                        onChange={() => handleArrayToggle('countries', country)}
                        className="mr-2"
                      />
                      <span className="text-sm">{country}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Pricing */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hourly Rate * ($25 - $500 USD)
                </label>
                <div className="flex items-center space-x-2">
                  <span className="text-gray-500">$</span>
                  <input
                    type="number"
                    min="25"
                    max="500"
                    required
                    disabled={!isEditing}
                    value={profile.hourly_rate}
                    onChange={(e) => setProfile({ ...profile, hourly_rate: parseInt(e.target.value) })}
                    className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100"
                  />
                  <span className="text-gray-500">per hour</span>
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

export default function CoachProfilePage() {
  return (
    <ProtectedRoute allowedRoles={['coach']}>
      <CoachProfileContent />
    </ProtectedRoute>
  );
}
