'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import AdminTable from '@/components/AdminTable';
import { api } from '@/lib/api';

function AdminModerationContent() {
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/community/posts');
      setPosts(response.data.posts || []);
    } catch (err: any) {
      setError('Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (post: any) => {
    if (!confirm(`Are you sure you want to delete this post: "${post.title}"?`)) return;

    try {
      await api.delete(`/admin/posts/${post.id}`);
      fetchPosts();
    } catch (err: any) {
      alert('Failed to delete post');
    }
  };

  const columns = [
    { key: 'title', label: 'Title', render: (value: string) => (
      <div className="max-w-md truncate">{value}</div>
    )},
    { key: 'author_name', label: 'Author' },
    { key: 'post_type', label: 'Type', render: (value: string) => (
      <span className={`px-2 py-1 text-xs font-medium rounded ${
        value === 'question' ? 'bg-purple-100 text-purple-800' :
        value === 'announcement' ? 'bg-blue-100 text-blue-800' :
        'bg-gray-100 text-gray-800'
      }`}>
        {value}
      </span>
    )},
    { key: 'upvotes', label: 'Upvotes' },
    { key: 'comment_count', label: 'Comments' },
    { key: 'created_at', label: 'Created', render: (value: string) => 
      new Date(value).toLocaleDateString()
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Content Moderation</h1>
          <p className="mt-2 text-gray-600">
            Moderate forum posts and community content
          </p>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-6">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <AdminTable
          columns={columns}
          data={posts}
          onDelete={handleDelete}
          loading={loading}
        />
      </div>
    </div>
  );
}

export default function AdminModerationPage() {
  return (
    <ProtectedRoute allowedRoles={['admin']}>
      <AdminModerationContent />
    </ProtectedRoute>
  );
}
