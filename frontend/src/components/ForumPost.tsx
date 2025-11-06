import { useState } from 'react';
import { api } from '@/lib/api';

interface ForumPostProps {
  post: {
    id: string;
    title: string;
    content: string;
    author_name: string;
    post_type: string;
    upvotes: number;
    comment_count: number;
    created_at: string;
    is_upvoted?: boolean;
  };
  onUpdate?: () => void;
}

export default function ForumPost({ post, onUpdate }: ForumPostProps) {
  const [showComments, setShowComments] = useState(false);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [upvoted, setUpvoted] = useState(post.is_upvoted || false);
  const [upvoteCount, setUpvoteCount] = useState(post.upvotes);

  const fetchComments = async () => {
    if (comments.length > 0) {
      setShowComments(!showComments);
      return;
    }

    setLoading(true);
    try {
      const response = await api.get(`/community/posts/${post.id}/comments`);
      setComments(response.data.comments || []);
      setShowComments(true);
    } catch (err) {
      console.error('Failed to fetch comments');
    } finally {
      setLoading(false);
    }
  };

  const handleUpvote = async () => {
    try {
      await api.post(`/community/posts/${post.id}/upvote`);
      setUpvoted(!upvoted);
      setUpvoteCount(upvoted ? upvoteCount - 1 : upvoteCount + 1);
    } catch (err) {
      console.error('Failed to upvote');
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const response = await api.post(`/community/posts/${post.id}/comment`, {
        content: newComment
      });
      setComments([...comments, response.data]);
      setNewComment('');
      if (onUpdate) onUpdate();
    } catch (err) {
      console.error('Failed to add comment');
    }
  };

  const getPostTypeColor = (type: string) => {
    switch (type) {
      case 'question':
        return 'bg-purple-100 text-purple-800';
      case 'announcement':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-start space-x-4">
        {/* Upvote Section */}
        <div className="flex flex-col items-center space-y-1">
          <button
            onClick={handleUpvote}
            className={`p-1 rounded hover:bg-gray-100 ${upvoted ? 'text-blue-600' : 'text-gray-400'}`}
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
            </svg>
          </button>
          <span className="text-sm font-medium text-gray-700">{upvoteCount}</span>
        </div>

        {/* Post Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <span className={`px-2 py-1 text-xs font-medium rounded ${getPostTypeColor(post.post_type)}`}>
              {post.post_type}
            </span>
            <span className="text-sm text-gray-500">
              by {post.author_name} • {new Date(post.created_at).toLocaleDateString()}
            </span>
          </div>

          <h3 className="text-lg font-semibold text-gray-900 mb-2">{post.title}</h3>
          <p className="text-gray-700 whitespace-pre-line">{post.content}</p>

          {/* Actions */}
          <div className="mt-4 flex items-center space-x-4">
            <button
              onClick={fetchComments}
              className="flex items-center text-sm text-gray-500 hover:text-gray-700"
            >
              <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              {post.comment_count} {post.comment_count === 1 ? 'Comment' : 'Comments'}
            </button>
          </div>

          {/* Comments Section */}
          {showComments && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : (
                <>
                  {comments.map((comment) => (
                    <div key={comment.id} className="mb-4 pl-4 border-l-2 border-gray-200">
                      <div className="text-sm text-gray-500 mb-1">
                        {comment.author_name} • {new Date(comment.created_at).toLocaleDateString()}
                      </div>
                      <p className="text-gray-700">{comment.content}</p>
                    </div>
                  ))}

                  {/* Add Comment Form */}
                  <form onSubmit={handleAddComment} className="mt-4">
                    <textarea
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      placeholder="Add a comment..."
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                    <button
                      type="submit"
                      className="mt-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                    >
                      Post Comment
                    </button>
                  </form>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
