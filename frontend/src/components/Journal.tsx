import React, { useState, useEffect } from 'react';

interface JournalEntry {
  id: string;
  date: string;
  title: string;
  content: string;
  symbol?: string;
  tags: string[];
}

const Journal: React.FC = () => {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [symbol, setSymbol] = useState('');
  const [tags, setTags] = useState('');


  const fetchEntries = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/journal');
      if (!res.ok) {
        throw new Error('Failed to fetch journal entries');
      }
      const data = await res.json();
      setEntries(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  const handleAddEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
        const newEntry = {
            title,
            content,
            symbol: symbol || undefined,
            tags: tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        };

        const res = await fetch('/api/v1/journal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newEntry),
        });

        if (!res.ok) {
            throw new Error('Failed to add journal entry');
        }

        // Reset form and refetch data
        setTitle('');
        setContent('');
        setSymbol('');
        setTags('');
        fetchEntries();

    } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };


  if (loading) {
    return <div>Loading journal...</div>;
  }

  if (error) {
    return <div className="text-red-500">Error: {error}</div>;
  }

  return (
    <div className="p-6 bg-white rounded-lg shadow-md mt-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Investment Journal</h2>
      
      {/* Form to add a new entry */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-700 mb-4">New Journal Entry</h3>
        <form onSubmit={handleAddEntry} className="space-y-4">
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
          <textarea
            placeholder="Content..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="w-full p-2 border rounded"
            rows={4}
            required
          ></textarea>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Symbol (optional)"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="p-2 border rounded"
            />
            <input
              type="text"
              placeholder="Tags (comma-separated)"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="p-2 border rounded"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Add Entry
          </button>
        </form>
      </div>

      {/* List of journal entries */}
      <div>
        <h3 className="text-xl font-semibold text-gray-700 mb-4">Past Entries</h3>
        <div className="space-y-6">
          {entries.length > 0 ? (
            entries.map((entry) => (
              <div key={entry.id} className="p-4 border-l-4 border-blue-500 bg-blue-50">
                <p className="font-bold text-lg">{entry.title}</p>
                <p className="text-sm text-gray-600 mb-2">
                    {new Date(entry.date).toLocaleString()}
                    {entry.symbol && <span className="ml-2 font-mono bg-gray-200 px-2 py-1 rounded text-xs">{entry.symbol}</span>}
                </p>
                <p className="text-gray-800 whitespace-pre-wrap">{entry.content}</p>
                {entry.tags.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-2">
                        {entry.tags.map(tag => (
                            <span key={tag} className="text-xs bg-gray-200 text-gray-800 px-2 py-1 rounded-full">{tag}</span>
                        ))}
                    </div>
                )}
              </div>
            ))
          ) : (
            <p>No journal entries yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Journal; 