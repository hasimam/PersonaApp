import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { statsApi } from '../../services/adminApi';
import { AdminStats } from '../../types/admin';

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await statsApi.getStats();
      setStats(data);
    } catch (err) {
      setError('Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        {error}
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Questions',
      value: stats?.total_questions || 0,
      subValue: `${stats?.questions_with_arabic || 0} with Arabic`,
      link: '/admin/questions',
      color: 'blue',
    },
    {
      label: 'Total Idols',
      value: stats?.total_idols || 0,
      subValue: `${stats?.idols_with_arabic || 0} with Arabic`,
      link: '/admin/idols',
      color: 'purple',
    },
    {
      label: 'Total Traits',
      value: stats?.total_traits || 0,
      subValue: `${stats?.traits_with_arabic || 0} with Arabic`,
      link: '/admin/traits',
      color: 'green',
    },
    {
      label: 'Total Users',
      value: stats?.total_users || 0,
      subValue: `${stats?.total_tests_completed || 0} tests completed`,
      link: null,
      color: 'orange',
    },
    {
      label: 'Journey Feedback',
      value: stats?.journey_feedback_count || 0,
      subValue:
        stats?.journey_feedback_avg_accuracy != null
          ? `Avg accuracy ${stats.journey_feedback_avg_accuracy.toFixed(2)} / 10`
          : 'No ratings yet',
      link: null,
      color: 'blue',
    },
  ];

  const getColorClasses = (color: string) => {
    const colors: Record<string, string> = {
      blue: 'bg-blue-50 border-blue-200 text-blue-700',
      purple: 'bg-purple-50 border-purple-200 text-purple-700',
      green: 'bg-green-50 border-green-200 text-green-700',
      orange: 'bg-orange-50 border-orange-200 text-orange-700',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {statCards.map((card) => (
          <div
            key={card.label}
            className={`p-6 rounded-lg border ${getColorClasses(card.color)}`}
          >
            <div className="text-3xl font-bold mb-1">{card.value}</div>
            <div className="font-medium mb-2">{card.label}</div>
            <div className="text-sm opacity-75">{card.subValue}</div>
            {card.link && (
              <Link
                to={card.link}
                className="mt-3 inline-block text-sm font-medium hover:underline"
              >
                Manage &rarr;
              </Link>
            )}
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Journey Feedback Analytics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
          {(stats?.journey_feedback_by_run_type || []).map((item) => (
            <div key={item.run_type} className="rounded-lg border border-gray-200 p-4">
              <div className="text-sm text-gray-500 uppercase tracking-wide mb-1">{item.run_type}</div>
              <div className="text-2xl font-bold text-gray-900">{item.count}</div>
              <div className="text-sm text-gray-600">
                Avg accuracy: {item.avg_accuracy_score != null ? item.avg_accuracy_score.toFixed(2) : '-'}
              </div>
              <div className="text-sm text-gray-600">
                Avg personality match:{' '}
                {item.avg_personality_match_score != null
                  ? item.avg_personality_match_score.toFixed(2)
                  : '-'}
              </div>
            </div>
          ))}
        </div>

        <h3 className="text-md font-semibold text-gray-900 mb-3">By Scenario Set</h3>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 text-left text-gray-600">
                <th className="py-2 pr-3">Set ID</th>
                <th className="py-2 pr-3">Run Type</th>
                <th className="py-2 pr-3">Responses</th>
                <th className="py-2 pr-3">Avg Accuracy</th>
                <th className="py-2 pr-3">Avg Personality Match</th>
              </tr>
            </thead>
            <tbody>
              {(stats?.journey_feedback_by_set || []).map((item) => (
                <tr
                  key={`${item.scenario_set_code}-${item.run_type}`}
                  className="border-b border-gray-100 text-gray-800"
                >
                  <td className="py-2 pr-3 font-mono">{item.scenario_set_code}</td>
                  <td className="py-2 pr-3">{item.run_type}</td>
                  <td className="py-2 pr-3">{item.count}</td>
                  <td className="py-2 pr-3">
                    {item.avg_accuracy_score != null ? item.avg_accuracy_score.toFixed(2) : '-'}
                  </td>
                  <td className="py-2 pr-3">
                    {item.avg_personality_match_score != null
                      ? item.avg_personality_match_score.toFixed(2)
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Translation Progress */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Arabic Translation Progress
        </h2>
        <div className="space-y-4">
          <TranslationProgress
            label="Questions"
            current={stats?.questions_with_arabic || 0}
            total={stats?.total_questions || 0}
          />
          <TranslationProgress
            label="Idols"
            current={stats?.idols_with_arabic || 0}
            total={stats?.total_idols || 0}
          />
          <TranslationProgress
            label="Traits"
            current={stats?.traits_with_arabic || 0}
            total={stats?.total_traits || 0}
          />
        </div>
      </div>
    </div>
  );
};

interface TranslationProgressProps {
  label: string;
  current: number;
  total: number;
}

const TranslationProgress: React.FC<TranslationProgressProps> = ({
  label,
  current,
  total,
}) => {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-700">{label}</span>
        <span className="text-gray-500">
          {current} / {total} ({percentage}%)
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary-600 h-2 rounded-full transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

export default AdminDashboard;
