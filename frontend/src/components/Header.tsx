'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function Header() {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <header className="bg-white shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-2xl font-bold text-blue-600">CultureBridge</span>
            </Link>
            
            {user && (
              <div className="hidden md:ml-10 md:flex md:space-x-8">
                <Link href="/dashboard" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                  Dashboard
                </Link>
                
                {user.role === 'client' && (
                  <>
                    <Link href="/coaches" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                      Find Coaches
                    </Link>
                    <Link href="/match" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                      AI Match
                    </Link>
                    <Link href="/booking/history" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                      My Bookings
                    </Link>
                  </>
                )}
                
                {user.role === 'coach' && (
                  <>
                    <Link href="/booking/history" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                      My Sessions
                    </Link>
                    <Link href={`/profile/coach`} className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                      My Profile
                    </Link>
                  </>
                )}
                
                {user.role === 'admin' && (
                  <Link href="/admin" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                    Admin
                  </Link>
                )}
                
                <Link href="/community" className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium">
                  Community
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-sm text-gray-700">{user.email}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium"
                >
                  Sign In
                </Link>
                <Link
                  href="/auth/signup"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
