import Link from 'next/link';

interface CoachCardProps {
  coach: {
    id: string;
    first_name: string;
    last_name: string;
    photo_url?: string;
    bio: string;
    expertise: string[];
    languages: string[];
    countries: string[];
    hourly_rate: number;
    rating: number;
    total_sessions: number;
  };
  matchScore?: number;
}

export default function CoachCard({ coach, matchScore }: CoachCardProps) {
  return (
    <Link href={`/coaches/${coach.id}`}>
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer">
        <div className="flex items-start space-x-4">
          {/* Photo */}
          <div className="flex-shrink-0">
            {coach.photo_url ? (
              <img
                src={coach.photo_url}
                alt={`${coach.first_name} ${coach.last_name}`}
                className="w-20 h-20 rounded-full object-cover"
              />
            ) : (
              <div className="w-20 h-20 rounded-full bg-gray-200 flex items-center justify-center">
                <span className="text-2xl text-gray-500">
                  {coach.first_name[0]}{coach.last_name[0]}
                </span>
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {coach.first_name} {coach.last_name}
                </h3>
                <div className="flex items-center mt-1">
                  <div className="flex items-center">
                    <svg className="w-4 h-4 text-yellow-400 fill-current" viewBox="0 0 20 20">
                      <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                    </svg>
                    <span className="ml-1 text-sm text-gray-600">
                      {coach.rating.toFixed(1)} ({coach.total_sessions} sessions)
                    </span>
                  </div>
                </div>
              </div>
              
              {matchScore !== undefined && (
                <div className="flex-shrink-0 ml-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{matchScore}%</div>
                    <div className="text-xs text-gray-500">Match</div>
                  </div>
                </div>
              )}
            </div>

            <p className="mt-2 text-sm text-gray-600 line-clamp-2">
              {coach.bio}
            </p>

            <div className="mt-3 flex flex-wrap gap-2">
              {coach.expertise.slice(0, 3).map((exp, idx) => (
                <span
                  key={idx}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {exp}
                </span>
              ))}
              {coach.expertise.length > 3 && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  +{coach.expertise.length - 3} more
                </span>
              )}
            </div>

            <div className="mt-3 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                <span className="font-medium">Languages:</span> {coach.languages.slice(0, 2).join(', ')}
                {coach.languages.length > 2 && ` +${coach.languages.length - 2}`}
              </div>
              <div className="text-lg font-bold text-gray-900">
                ${coach.hourly_rate}/hr
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
