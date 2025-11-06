import CoachCard from './CoachCard';

interface Match {
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
  match_score: number;
  confidence: string;
}

interface MatchResultsProps {
  matches: Match[];
  loading?: boolean;
}

export default function MatchResults({ matches, loading }: MatchResultsProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Finding your perfect matches...</p>
        </div>
      </div>
    );
  }

  if (matches.length === 0) {
    return (
      <div className="text-center py-12">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">No matches found</h3>
        <p className="mt-1 text-sm text-gray-500">
          Try adjusting your preferences or complete your profile quiz.
        </p>
      </div>
    );
  }

  const getConfidenceColor = (confidence: string) => {
    switch (confidence.toLowerCase()) {
      case 'high':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-blue-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              Your Top {matches.length} Matches
            </h3>
            <p className="mt-1 text-sm text-blue-700">
              These coaches are ranked based on your profile and preferences. Match scores indicate compatibility.
            </p>
          </div>
        </div>
      </div>

      {matches.map((match, index) => (
        <div key={match.coach.id} className="relative">
          {index === 0 && match.match_score >= 80 && (
            <div className="absolute -top-2 -right-2 z-10">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-400 text-yellow-900">
                ⭐ Best Match
              </span>
            </div>
          )}
          <CoachCard coach={match.coach} matchScore={Math.round(match.match_score)} />
          <div className="mt-2 flex items-center justify-between px-2">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(match.confidence)}`}>
              {match.confidence} Confidence
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
