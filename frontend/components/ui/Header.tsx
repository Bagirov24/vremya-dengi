'use client';

import { useAuth } from '@/components/providers/AuthProvider';
import NotificationBell from '@/components/NotificationBell';
import { getInitials } from '@/lib/utils';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-gray-800 bg-gray-900/95 backdrop-blur px-6">
      <div className="flex flex-1 items-center justify-end gap-4">
        <NotificationBell />
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-medium text-white">
            {user ? getInitials(user.name) : '?'}
          </div>
          <button
            onClick={logout}
            className="text-sm text-gray-400 hover:text-white transition-colors"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
