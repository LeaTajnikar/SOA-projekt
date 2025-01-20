import { useState, useEffect } from 'react';
import { PlusCircle, Trash2, BookOpen, RefreshCw } from 'lucide-react';

// Authors Component
const AuthorsManager = () => {
  const [authors, setAuthors] = useState([]);
  const [newAuthor, setNewAuthor] = useState({ name: '', books: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAuthors();
  }, []);

  const fetchAuthors = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8012/authors');
      const data = await response.json();
      setAuthors(data);
    } catch (error) {
      console.error('Error fetching authors:', error);
    }
    setLoading(false);
  };

  const addAuthor = async () => {
    try {
      const response = await fetch('http://localhost:8012/authors', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAuthor)
      });
      if (response.ok) {
        setNewAuthor({ name: '', books: [] });
        fetchAuthors();
      }
    } catch (error) {
      console.error('Error adding author:', error);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Authors Management</h2>
      
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          value={newAuthor.name}
          onChange={(e) => setNewAuthor({ ...newAuthor, name: e.target.value })}
          placeholder="Author name"
          className="border p-2 rounded"
        />
        <button
          onClick={addAuthor}
          className="bg-blue-500 text-white px-4 py-2 rounded flex items-center gap-2"
        >
          <PlusCircle size={20} /> Add Author
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center">
          <RefreshCw size={24} className="animate-spin" />
        </div>
      ) : (
        <div className="grid gap-4">
          {authors.map((author) => (
            <div key={author.name} className="border p-4 rounded shadow">
              <h3 className="text-xl font-semibold">{author.name}</h3>
              <div className="mt-2">
                <h4 className="font-medium">Books:</h4>
                <ul className="list-disc ml-4">
                  {author.books?.map((book) => (
                    <li key={book}>{book}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Genres Component
const GenresManager = () => {
  const [genres, setGenres] = useState([]);
  const [newGenre, setNewGenre] = useState({ name: '', description: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchGenres();
  }, []);

  const fetchGenres = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8013/genres');
      const data = await response.json();
      setGenres(data);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
    setLoading(false);
  };

  const addGenre = async () => {
    try {
      const response = await fetch('http://localhost:8013/genres', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newGenre)
      });
      if (response.ok) {
        setNewGenre({ name: '', description: '' });
        fetchGenres();
      }
    } catch (error) {
      console.error('Error adding genre:', error);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Genres Management</h2>
      
      <div className="mb-4 flex gap-2">
        <input
          type="text"
          value={newGenre.name}
          onChange={(e) => setNewGenre({ ...newGenre, name: e.target.value })}
          placeholder="Genre name"
          className="border p-2 rounded"
        />
        <input
          type="text"
          value={newGenre.description}
          onChange={(e) => setNewGenre({ ...newGenre, description: e.target.value })}
          placeholder="Description"
          className="border p-2 rounded"
        />
        <button
          onClick={addGenre}
          className="bg-green-500 text-white px-4 py-2 rounded flex items-center gap-2"
        >
          <PlusCircle size={20} /> Add Genre
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center">
          <RefreshCw size={24} className="animate-spin" />
        </div>
      ) : (
        <div className="grid gap-4">
          {genres.map((genre) => (
            <div key={genre.name} className="border p-4 rounded shadow">
              <h3 className="text-xl font-semibold">{genre.name}</h3>
              <p className="text-gray-600">{genre.description}</p>
              <div className="mt-2">
                <h4 className="font-medium">Books in this genre:</h4>
                <ul className="list-disc ml-4">
                  {genre.books?.map((book) => (
                    <li key={book}>{book}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Recommendations Component
const RecommendationsViewer = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [genres, setGenres] = useState([]);

  useEffect(() => {
    fetchGenres();
  }, []);

  const fetchGenres = async () => {
    try {
      const response = await fetch('http://localhost:8013/genres');
      const data = await response.json();
      setGenres(data);
    } catch (error) {
      console.error('Error fetching genres:', error);
    }
  };

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      // This is a placeholder URL - replace with your actual recommendations endpoint
      const response = await fetch(`http://localhost:8014/recommendations?genre=${selectedGenre}`);
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
    }
    setLoading(false);
  };

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4">Book Recommendations</h2>
      
      <div className="mb-4 flex gap-2">
        <select
          value={selectedGenre}
          onChange={(e) => setSelectedGenre(e.target.value)}
          className="border p-2 rounded"
        >
          <option value="">Select a genre</option>
          {genres.map((genre) => (
            <option key={genre.name} value={genre.name}>
              {genre.name}
            </option>
          ))}
        </select>
        <button
          onClick={fetchRecommendations}
          className="bg-purple-500 text-white px-4 py-2 rounded flex items-center gap-2"
          disabled={!selectedGenre}
        >
          <BookOpen size={20} /> Get Recommendations
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center">
          <RefreshCw size={24} className="animate-spin" />
        </div>
      ) : (
        <div className="grid gap-4">
          {recommendations.map((book) => (
            <div key={book.id} className="border p-4 rounded shadow">
              <h3 className="text-xl font-semibold">{book.title}</h3>
              <p className="text-gray-600">{book.description}</p>
              <div className="mt-2 text-sm text-gray-500">
                Rating: {book.rating} / 5
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Main App Component
const LibraryApp = () => {
  const [activeTab, setActiveTab] = useState('authors');

  return (
    <div className="container mx-auto p-4">
      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setActiveTab('authors')}
          className={`px-4 py-2 rounded ${
            activeTab === 'authors' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Authors
        </button>
        <button
          onClick={() => setActiveTab('genres')}
          className={`px-4 py-2 rounded ${
            activeTab === 'genres' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Genres
        </button>
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`px-4 py-2 rounded ${
            activeTab === 'recommendations' ? 'bg-blue-500 text-white' : 'bg-gray-200'
          }`}
        >
          Recommendations
        </button>
      </div>

      {activeTab === 'authors' && <AuthorsManager />}
      {activeTab === 'genres' && <GenresManager />}
      {activeTab === 'recommendations' && <RecommendationsViewer />}
    </div>
  );
};

export default LibraryApp;