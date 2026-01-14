import React, { useEffect, useState } from 'react';
import { traitsApi } from '../../services/adminApi';
import { AdminTrait, AdminTraitCreate } from '../../types/admin';

const AdminTraits: React.FC = () => {
  const [traits, setTraits] = useState<AdminTrait[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingTrait, setEditingTrait] = useState<AdminTrait | null>(null);

  useEffect(() => {
    loadTraits();
  }, []);

  const loadTraits = async () => {
    try {
      const data = await traitsApi.list();
      setTraits(data);
    } catch (err) {
      setError('Failed to load traits');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this trait? This will fail if questions are using it.')) return;

    try {
      await traitsApi.delete(id);
      setTraits(traits.filter((t) => t.id !== id));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete trait');
    }
  };

  const handleEdit = (trait: AdminTrait) => {
    setEditingTrait(trait);
    setShowModal(true);
  };

  const handleCreate = () => {
    setEditingTrait(null);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingTrait(null);
  };

  const handleSave = async (data: AdminTraitCreate) => {
    try {
      if (editingTrait) {
        const updated = await traitsApi.update(editingTrait.id, data);
        setTraits(traits.map((t) => (t.id === updated.id ? updated : t)));
      } else {
        const created = await traitsApi.create(data);
        setTraits([...traits, created]);
      }
      handleModalClose();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save trait');
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
        <h1 className="text-2xl font-bold text-gray-900">Traits</h1>
        <button
          onClick={handleCreate}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          + Add Trait
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {traits.map((trait) => (
          <div key={trait.id} className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {trait.name_en}
                </h3>
                {trait.name_ar && (
                  <p className="text-gray-600" dir="rtl">
                    {trait.name_ar}
                  </p>
                )}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(trait)}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(trait.id)}
                  className="text-sm text-red-600 hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-500 mb-1">
                  Description (EN)
                </h4>
                <p className="text-sm text-gray-700">{trait.description_en}</p>
              </div>
              {trait.description_ar && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-1">
                    Description (AR)
                  </h4>
                  <p className="text-sm text-gray-700" dir="rtl">
                    {trait.description_ar}
                  </p>
                </div>
              )}
            </div>

            {(trait.high_behavior_en || trait.low_behavior_en) && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-100">
                {trait.high_behavior_en && (
                  <div>
                    <h4 className="text-sm font-medium text-green-600 mb-1">
                      High Behavior
                    </h4>
                    <p className="text-sm text-gray-600">{trait.high_behavior_en}</p>
                  </div>
                )}
                {trait.low_behavior_en && (
                  <div>
                    <h4 className="text-sm font-medium text-orange-600 mb-1">
                      Low Behavior
                    </h4>
                    <p className="text-sm text-gray-600">{trait.low_behavior_en}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {traits.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center text-gray-500">
          No traits found. Create one to get started.
        </div>
      )}

      {showModal && (
        <TraitModal
          trait={editingTrait}
          onSave={handleSave}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};

interface TraitModalProps {
  trait: AdminTrait | null;
  onSave: (data: AdminTraitCreate) => void;
  onClose: () => void;
}

const TraitModal: React.FC<TraitModalProps> = ({ trait, onSave, onClose }) => {
  const [formData, setFormData] = useState<AdminTraitCreate>({
    name_en: trait?.name_en || '',
    name_ar: trait?.name_ar || '',
    description_en: trait?.description_en || '',
    description_ar: trait?.description_ar || '',
    high_behavior_en: trait?.high_behavior_en || '',
    high_behavior_ar: trait?.high_behavior_ar || '',
    low_behavior_en: trait?.low_behavior_en || '',
    low_behavior_ar: trait?.low_behavior_ar || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      ...formData,
      name_ar: formData.name_ar || null,
      description_ar: formData.description_ar || null,
      high_behavior_en: formData.high_behavior_en || null,
      high_behavior_ar: formData.high_behavior_ar || null,
      low_behavior_en: formData.low_behavior_en || null,
      low_behavior_ar: formData.low_behavior_ar || null,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {trait ? 'Edit Trait' : 'Add Trait'}
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
                  Description (English) *
                </label>
                <textarea
                  value={formData.description_en}
                  onChange={(e) =>
                    setFormData({ ...formData, description_en: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={3}
                  required
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

            {/* High Behavior */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  High Behavior (English)
                </label>
                <textarea
                  value={formData.high_behavior_en || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, high_behavior_en: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={2}
                  placeholder="Behavior when score is high..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  High Behavior (Arabic)
                </label>
                <textarea
                  value={formData.high_behavior_ar || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, high_behavior_ar: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={2}
                  dir="rtl"
                />
              </div>
            </div>

            {/* Low Behavior */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Low Behavior (English)
                </label>
                <textarea
                  value={formData.low_behavior_en || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, low_behavior_en: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={2}
                  placeholder="Behavior when score is low..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Low Behavior (Arabic)
                </label>
                <textarea
                  value={formData.low_behavior_ar || ''}
                  onChange={(e) =>
                    setFormData({ ...formData, low_behavior_ar: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  rows={2}
                  dir="rtl"
                />
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
                {trait ? 'Save Changes' : 'Create Trait'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AdminTraits;
