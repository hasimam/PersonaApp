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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
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
