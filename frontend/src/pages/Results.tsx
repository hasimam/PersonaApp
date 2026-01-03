import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resultsApi } from '../services/api';
import { ResultResponse } from '../types';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const Results: React.FC = () => {
  const { resultId } = useParams<{ resultId: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<ResultResponse | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchResults = async () => {
      if (!resultId) return;

      try {
        const data = await resultsApi.getResult(parseInt(resultId));
        setResult(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load results. Please try again.');
        setLoading(false);
      }
    };

    fetchResults();
  }, [resultId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing your personality...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card max-w-md text-center">
          <p className="text-red-600 mb-4">{error || 'Results not found'}</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const chartData = result.user_trait_scores.map((trait) => ({
    trait: trait.trait_name,
    score: trait.score,
  }));

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Your Personality Results</h1>
          <p className="text-gray-600">Here are the celebrities most similar to your personality</p>
        </div>

        {/* Top Matches */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
            Your Top 3 Matches
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {result.top_matches.map((match, index) => (
              <div key={match.idol_id} className="card text-center hover:shadow-xl transition-shadow">
                <div className="relative mb-4">
                  <div className="absolute -top-4 -right-4 bg-primary-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg">
                    #{index + 1}
                  </div>
                  <img
                    src={match.image_url || '/placeholder.png'}
                    alt={match.name}
                    className="w-full h-64 object-cover rounded-lg mb-4"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder.png';
                    }}
                  />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{match.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{match.description}</p>
                <div className="bg-primary-50 rounded-lg p-4">
                  <p className="text-3xl font-bold text-primary-600">
                    {match.similarity_percentage}%
                  </p>
                  <p className="text-sm text-gray-600">Personality Match</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Personality Profile Chart */}
        <div className="card mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6 text-center">
            Your Personality Profile
          </h2>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={chartData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="trait" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar
                name="Your Score"
                dataKey="score"
                stroke="#0284c7"
                fill="#0284c7"
                fillOpacity={0.6}
              />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Trait Scores */}
        <div className="card mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Your Trait Scores</h2>
          <div className="space-y-4">
            {result.user_trait_scores.map((trait) => (
              <div key={trait.trait_id}>
                <div className="flex justify-between mb-2">
                  <span className="font-medium text-gray-700">{trait.trait_name}</span>
                  <span className="text-primary-600 font-semibold">{trait.score.toFixed(1)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-primary-600 h-3 rounded-full transition-all"
                    style={{ width: `${trait.score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-center gap-4">
          <button onClick={() => navigate('/')} className="btn-primary">
            Retake Test
          </button>
          <button
            onClick={() => {
              // Share functionality would go here
              alert('Share feature coming soon!');
            }}
            className="btn-secondary"
          >
            Share Results
          </button>
        </div>

        {/* Disclaimer */}
        <p className="text-sm text-gray-500 text-center mt-8 max-w-2xl mx-auto">
          These results are for entertainment and self-reflection purposes. Idol personalities are
          estimated from publicly available information and may not reflect their complete or private
          personalities.
        </p>
      </div>
    </div>
  );
};

export default Results;
