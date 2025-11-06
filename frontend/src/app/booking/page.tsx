'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import BookingCalendar from '@/components/BookingCalendar';
import { api } from '@/lib/api';

function BookingPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const [coach, setCoach] = useState<any>(null);
  const [selectedSlot, setSelectedSlot] = useState<string>('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState('');

  const coachId = searchParams.get('coach_id');

  useEffect(() => {
    if (coachId) {
      fetchCoach();
    } else {
      setError('No coach selected');
      setLoading(false);
    }
  }, [coachId]);

  const fetchCoach = async () => {
    try {
      const response = await api.get(`/coaches/${coachId}`);
      setCoach(response.data);
    } catch (err: any) {
      setError('Failed to load coach details');
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async () => {
    if (!selectedSlot) {
      setError('Please select a time slot');
      return;
    }

    setBooking(true);
    setError('');

    try {
      // Create booking
      const bookingResponse = await api.post('/booking', {
        coach_id: coachId,
        session_datetime: selectedSlot,
        duration_minutes: 60,
        notes
      });

      const bookingId = bookingResponse.data.id;

      // Initiate payment
      const paymentResponse = await api.post('/payment/checkout', {
        booking_id: bookingId
      });

      // Redirect to Stripe checkout
      window.location.href = paymentResponse.data.checkout_url;
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to create booking');
      setBooking(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !coach) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => router.push('/coaches')}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Browse Coaches
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
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">Book a Session</h1>
          </div>

          <div className="p-6 space-y-6">
            {/* Coach Info */}
            {coach && (
              <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                {coach.photo_url ? (
                  <img
                    src={coach.photo_url}
                    alt={`${coach.first_name} ${coach.last_name}`}
                    className="w-16 h-16 rounded-full object-cover"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-xl text-gray-500">
                      {coach.first_name[0]}{coach.last_name[0]}
                    </span>
                  </div>
                )}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {coach.first_name} {coach.last_name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    ${coach.hourly_rate}/hour • 60 minutes
                  </p>
                </div>
              </div>
            )}

            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {/* Calendar */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Date & Time</h2>
              <BookingCalendar
                coachId={coachId!}
                onSelectSlot={setSelectedSlot}
                selectedSlot={selectedSlot}
              />
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Session Notes (Optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Any specific topics or goals you'd like to discuss..."
              />
            </div>

            {/* Summary */}
            {selectedSlot && coach && (
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="text-sm font-medium text-blue-900 mb-2">Booking Summary</h3>
                <div className="space-y-1 text-sm text-blue-800">
                  <p>
                    <span className="font-medium">Date:</span>{' '}
                    {new Date(selectedSlot).toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                  <p>
                    <span className="font-medium">Time:</span>{' '}
                    {new Date(selectedSlot).toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit',
                      hour12: true
                    })}
                  </p>
                  <p>
                    <span className="font-medium">Duration:</span> 60 minutes
                  </p>
                  <p className="text-lg font-bold mt-2">
                    Total: ${coach.hourly_rate}
                  </p>
                </div>
              </div>
            )}

            {/* Book Button */}
            <button
              onClick={handleBooking}
              disabled={!selectedSlot || booking}
              className="w-full px-6 py-3 text-lg font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {booking ? 'Processing...' : 'Proceed to Payment'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function BookingPage() {
  return (
    <ProtectedRoute allowedRoles={['client']}>
      <BookingPageContent />
    </ProtectedRoute>
  );
}
