import React, { useEffect, useState } from 'react';
import { idolsApi, traitsApi } from '../../services/adminApi';
import { AdminIdol, AdminIdolCreate, AdminTrait } from '../../types/admin';

const AdminIdols: React.FC = () => {
  const [idols, setIdols] = useState<AdminIdol[]>([]);
  const [traits, setTraits] = useState<AdminTrait[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingIdol, setEditingIdol] = useState<AdminIdol | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [idolsData, traitsData] = await Promise.all([
        idolsApi.list(),
        traitsApi.list(),
      ]);
      setIdols(idolsData);
      setTraits(traitsData);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this idol?')) return;

    try {
      await idolsApi.delete(id);
      setIdols(idols.filter((i) => i.id !== id));
    } catch (err) {
      alert('Failed to delete idol');
    }
  };

  const handleEdit = (idol: AdminIdol) => {
    setEditingIdol(idol);
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingIdol(null);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingIdol(null);
  };

  const handleSave = async (data: AdminIdolCreate) => {
    try {
      if (editingIdol) {
        const updated = await idolsApi.update(editingIdol.id, data);
        setIdols(idols.map((i) => (i.id === updated.id ? updated : i)));
      } else {
        const created = await idolsApi.create(data);
        setIdols([...idols, created]);
      }
      handleModalClose();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save idol');
    }
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
        <h1 className="text-2xl font-bold text-gray-900">Idols</h1>
        <button
          onClick={handleCreate}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          + Add Idol
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {idols.map((idol) => (
          <div key={idol.id} className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex items-start space-x-3">
              {idol.image_url ? (
                <img
                  src={idol.image_url}
                  alt={idol.name_en}
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-2xl">
                  {idol.name_en.charAt(0)}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 truncate">
                  {idol.name_en}
                </h3>
                {idol.name_ar && (
                  <p className="text-sm text-gray-600 truncate" dir="rtl">
                    {idol.name_ar}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  {Object.keys(idol.trait_scores).length} trait scores
                </p>
              </div>
            </div>

            {idol.description_en && (
              <p className="text-sm text-gray-600 mt-3 line-clamp-2">
                {idol.description_en}
              </p>
            )}

            <div className="flex justify-end space-x-2 mt-4 pt-3 border-t border-gray-100">
              <button
                onClick={() => handleEdit(idol)}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(idol.id)}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {idols.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center text-gray-500">
          No idols found. Create one to get started.
        </div>
      )}

      {showModal && (
        <IdolModal
          idol={editingIdol}
          traits={traits}
          onSave={handleSave}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};

interface IdolModalProps {
  idol: AdminIdol | null;
  traits: AdminTrait[];
  onSave: (data: AdminIdolCreate) => void;
  onClose: () => void;
}

const IdolModal: React.FC<IdolModalProps> = ({ idol, traits, onSave, onClose }) => {
  const [formData, setFormData] = useState<AdminIdolCreate>({
    name_en: idol?.name_en || '',
    name_ar: idol?.name_ar || '',
    description_en: idol?.description_en || '',
    description_ar: idol?.description_ar || '',
    image_url: idol?.image_url || '',
    trait_scores: idol?.trait_scores || {},
  });

  const handleTraitScoreChange = (traitId: number, value: string) => {
    const numValue = parseInt(value, 10);
    if (isNaN(numValue)) {
      const newScores = { ...formData.trait_scores };
      delete newScores[traitId.toString()];
      setFormData({ ...formData, trait_scores: newScores });
    } else {
      setFormData({
        ...formData,
        trait_scores: {
          ...formData.trait_scores,
          [traitId.toString()]: Math.min(100, Math.max(0, numValue)),
        },
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...formData,
      name_ar: formData.name_ar || null,
      description_en: formData.description_en || null,
      description_ar: formData.description_ar || null,
      image_url: formData.image_url || null,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {idol ? 'Edit Idol' : 'Add Idol'}
          </h2>

          <form onSubmit={handleSubmit}>
            {/* Names */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name (English) *
                </label>
                <input
                  type="text"
                  value={formData.name_en}
                  onChange={(e) =>
                    setFormData({ ...formData, name_en: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name (Arabic)
                </label>
                <input
                  type="text"
                  value={formData.name_ar || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, name_ar: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  dir="rtl"
                />
              </div>
            </div>

            {/* Descriptions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (English)
                </label>
                <textarea
                  value={formData.description_en || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, description_en: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Arabic)
                </label>
                <textarea
                  value={formData.description_ar || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, description_ar: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  dir="rtl"
                />
              </div>
            </div>

            {/* Image URL */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Image URL
              </label>
              <input
                type="url"
                value={formData.image_url || ''}
                onChange={(e) =>
                  setFormData({ ...formData, image_url: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="https://example.com/image.jpg"
              />
            </div>

            {/* Trait Scores */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trait Scores (0-100)
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {traits.map((trait) => (
                  <div key={trait.id} className="flex items-center space-x-2">
                    <label className="text-sm text-gray-600 w-24 truncate">
                      {trait.name_en}
                    </label>
                    <input
                      type="number"
                      value={formData.trait_scores[trait.id.toString()] ?? ''}
                      onChange={(e) =>
                        handleTraitScoreChange(trait.id, e.target.value)
                      }
                      className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-primary-500 text-sm"
                      min="0"
                      max="100"
                      placeholder="-"
                    />
                  </div>
                ))}
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
                {idol ? 'Save Changes' : 'Create Idol'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AdminIdols;
