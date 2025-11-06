'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import AdminTable from '@/components/AdminTable';
import { api } from '@/lib/api';

function AdminBookingsContent() {
  const [bookings, setBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await api.get('/admin/bookings');
      setBookings(response.data.bookings || []);
    } catch (err: any) {
      setError('Failed to load bookings');
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: 'client_email', label: 'Client' },
    { key: 'coach_email', label: 'Coach' },
    { key: 'session_datetime', label: 'Date & Time', render: (value: string) => (
      <div>
        <div>{new Date(value).toLocaleDateString()}</div>
        <div className="text-xs text-gray-500">
          {new Date(value).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
        </div>
      </div>
    )},
    { key: 'duration_minutes', label: 'Duration', render: (value: number) => `${value} min` },
    { key: 'status', label: 'Status', render: (value: string) => (
      <span className={`px-2 py-1 text-xs font-medium rounded ${
        value === 'confirmed' ? 'bg-green-100 text-green-800' :
        value === 'pending' ? 'bg-yellow-100 text-yellow-800' :
        value === 'completed' ? 'bg-blue-100 text-blue-800' :
        'bg-red-100 text-red-800'
      }`}>
        {value}
      </span>
    )}
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Bookings Management</h1>
          <p className="mt-2 text-gray-600">
            View all platform bookings
          </p>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-6">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <AdminTable
          columns={columns}
          data={bookings}
          loading={loading}
        />
      </div>
    </div>
  );
}

export default function AdminBookingsPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminBookingsContent />
    </ProtectedRoute>
  );
}
