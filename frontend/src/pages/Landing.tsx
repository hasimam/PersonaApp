import React from 'react';
import { useNavigate } from 'react-router-dom';

const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-2xl text-center">
        <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
          Find Your Idol Twin
        </h1>

        <p className="text-xl text-gray-700 mb-8">
          Discover which celebrities and public figures share your unique personality traits.
          Take our science-inspired personality test and find your top 3 matches.
        </p>

        <div className="card mb-8">
          <h2 className="text-2xl font-semibold mb-4">What to Expect</h2>
          <div className="space-y-4 text-left">
            <div className="flex items-start">
              <span className="text-primary-600 mr-3 text-2xl">✓</span>
              <div>
                <h3 className="font-semibold">50 Quick Questions</h3>
                <p className="text-gray-600">Takes about 8-10 minutes to complete</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 mr-3 text-2xl">✓</span>
              <div>
                <h3 className="font-semibold">Your Personality Profile</h3>
                <p className="text-gray-600">Get scores across 10 key personality traits</p>
              </div>
            </div>
            <div className="flex items-start">
              <span className="text-primary-600 mr-3 text-2xl">✓</span>
              <div>
                <h3 className="font-semibold">Top 3 Idol Matches</h3>
                <p className="text-gray-600">See which celebrities are most similar to you</p>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={() => navigate('/test')}
          className="btn-primary text-lg px-10 py-4"
        >
          Start Personality Test
        </button>

        <p className="text-sm text-gray-600 mt-6 max-w-lg mx-auto">
          <strong>Disclaimer:</strong> This test is designed for entertainment and self-reflection.
          Idol personalities are estimated from public information and may not reflect their private selves.
          This is not a clinical psychological assessment.
        </p>
      </div>
    </div>
  );
};

export default Landing;
