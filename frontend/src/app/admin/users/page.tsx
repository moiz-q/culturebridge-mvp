'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import AdminTable from '@/components/AdminTable';
import { api } from '@/lib/api';

function AdminUsersContent() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchUsers();
  }, [filter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter !== 'all') params.append('role', filter);
      if (searchTerm) params.append('search', searchTerm);

      const response = await api.get(`/admin/users?${params.toString()}`);
      setUsers(response.data.users || []);
    } catch (err: any) {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers();
  };

  const handleEdit = (user: any) => {
    // Open edit modal or navigate to edit page
    console.log('Edit user:', user);
  };

  const handleDelete = async (user: any) => {
    if (!confirm(`Are you sure you want to delete user ${user.email}?`)) return;

    try {
      await api.delete(`/admin/users/${user.id}`);
      fetchUsers();
    } catch (err: any) {
      alert('Failed to delete user');
    }
  };

  const columns = [
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Role', render: (value: string) => (
      <span className={`px-2 py-1 text-xs font-medium rounded ${
        value === 'admin' ? 'bg-red-100 text-red-800' :
        value === 'coach' ? 'bg-blue-100 text-blue-800' :
        'bg-green-100 text-green-800'
      }`}>
        {value}
      </span>
    )},
    { key: 'is_active', label: 'Status', render: (value: boolean) => (
      <span className={`px-2 py-1 text-xs font-medium rounded ${
        value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
      }`}>
        {value ? 'Active' : 'Inactive'}
      </span>
    )},
    { key: 'created_at', label: 'Joined', render: (value: string) => 
      new Date(value).toLocaleDateString()
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="mt-2 text-gray-600">
            View and manage platform users
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <form onSubmit={handleSearch} className="flex space-x-2">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by email..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              type="submit"
              className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Search
            </button>
          </form>

          <div className="flex space-x-2">
            {['all', 'client', 'coach', 'admin'].map((role) => (
              <button
                key={role}
                onClick={() => setFilter(role)}
                className={`px-4 py-2 text-sm font-medium rounded-md ${
                  filter === role
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                {role.charAt(0).toUpperCase() + role.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-6">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <AdminTable
          columns={columns}
          data={users}
          onEdit={handleEdit}
          onDelete={handleDelete}
          loading={loading}
        />
      </div>
    </div>
  );
}

export default function AdminUsersPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminUsersContent />
    </ProtectedRoute>
  );
}
