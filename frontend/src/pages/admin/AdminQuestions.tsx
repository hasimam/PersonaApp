import React, { useEffect, useState } from 'react';
import { questionsApi, traitsApi } from '../../services/adminApi';
import { AdminQuestion, AdminQuestionCreate, AdminTrait } from '../../types/admin';

const AdminQuestions: React.FC = () => {
  const [questions, setQuestions] = useState<AdminQuestion[]>([]);
  const [traits, setTraits] = useState<AdminTrait[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState<AdminQuestion | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [questionsData, traitsData] = await Promise.all([
        questionsApi.list(),
        traitsApi.list(),
      ]);
      setQuestions(questionsData);
      setTraits(traitsData);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this question?')) return;

    try {
      await questionsApi.delete(id);
      setQuestions(questions.filter((q) => q.id !== id));
    } catch (err) {
      alert('Failed to delete question');
    }
  };

  const handleEdit = (question: AdminQuestion) => {
    setEditingQuestion(question);
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingQuestion(null);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingQuestion(null);
  };

  const handleSave = async (data: AdminQuestionCreate) => {
    try {
      if (editingQuestion) {
        const updated = await questionsApi.update(editingQuestion.id, data);
        setQuestions(questions.map((q) => (q.id === updated.id ? updated : q)));
      } else {
        const created = await questionsApi.create(data);
        setQuestions([...questions, created]);
      }
      handleModalClose();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save question');
    }
  };

  const getTraitName = (traitId: number) => {
    const trait = traits.find((t) => t.id === traitId);
    return trait?.name_en || `Trait #${traitId}`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Questions</h1>
        <button
          onClick={handleCreate}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          + Add Question
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Order</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">English</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Arabic</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Trait</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Rev.</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {questions.map((question) => (
              <tr key={question.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-900">{question.order_index}</td>
                <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                  {question.text_en}
                </td>
                <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate" dir="rtl">
                  {question.text_ar || (
                    <span className="text-gray-400 italic">Not translated</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {getTraitName(question.trait_id)}
                </td>
                <td className="px-4 py-3 text-sm">
                  {question.reverse_scored ? (
                    <span className="text-orange-600">Yes</span>
                  ) : (
                    <span className="text-gray-400">No</span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm">
                  <button
                    onClick={() => handleEdit(question)}
                    className="text-primary-600 hover:text-primary-700 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(question.id)}
                    className="text-red-600 hover:text-red-700"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {questions.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No questions found. Create one to get started.
          </div>
        )}
      </div>

      {showModal && (
        <QuestionModal
          question={editingQuestion}
          traits={traits}
          onSave={handleSave}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};

interface QuestionModalProps {
  question: AdminQuestion | null;
  traits: AdminTrait[];
  onSave: (data: AdminQuestionCreate) => void;
  onClose: () => void;
}

const QuestionModal: React.FC<QuestionModalProps> = ({
  question,
  traits,
  onSave,
  onClose,
}) => {
  const [formData, setFormData] = useState<AdminQuestionCreate>({
    text_en: question?.text_en || '',
    text_ar: question?.text_ar || '',
    trait_id: question?.trait_id || (traits[0]?.id || 0),
    reverse_scored: question?.reverse_scored || false,
    order_index: question?.order_index || 0,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...formData,
      text_ar: formData.text_ar || null,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {question ? 'Edit Question' : 'Add Question'}
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  English Text *
                </label>
                <textarea
                  value={formData.text_en}
                  onChange={(e) =>
                    setFormData({ ...formData, text_en: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Arabic Text
                </label>
                <textarea
                  value={formData.text_ar || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, text_ar: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  dir="rtl"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trait *
                </label>
                <select
                  value={formData.trait_id}
                  onChange={(e) =>
                    setFormData({ ...formData, trait_id: Number(e.target.value) })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                >
                  {traits.map((trait) => (
                    <option key={trait.id} value={trait.id}>
                      {trait.name_en}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Order Index *
                </label>
                <input
                  type="number"
                  value={formData.order_index}
                  onChange={(e) =>
                    setFormData({ ...formData, order_index: Number(e.target.value) })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  min="0"
                  required
                />
              </div>
              <div className="flex items-center pt-6">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.reverse_scored}
                    onChange={(e) =>
                      setFormData({ ...formData, reverse_scored: e.target.checked })
                    }
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Reverse Scored</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                {question ? 'Save Changes' : 'Create Question'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AdminQuestions;
