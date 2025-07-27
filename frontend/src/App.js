import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API}/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/login`, { email, password });
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (name, email, password, role = 'student') => {
    try {
      const response = await axios.post(`${API}/register`, { name, email, password, role });
      const { access_token, user: userData } = response.data;
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('token', access_token);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Utility Functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('pt-BR');
};

// Components
const Navbar = () => {
  const { user, logout } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      const response = await axios.get(`${API}/notifications`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  const markNotificationRead = async (notificationId) => {
    try {
      await axios.put(`${API}/notifications/${notificationId}/read`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      fetchNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-purple-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <span className="text-white text-xl font-bold">PUCRS Innovation</span>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <>
                {/* Notifications */}
                <div className="relative">
                  <button
                    onClick={() => setShowNotifications(!showNotifications)}
                    className="relative p-2 text-white hover:bg-white hover:bg-opacity-20 rounded-full transition duration-200"
                  >
                    <span className="text-xl">🔔</span>
                    {unreadCount > 0 && (
                      <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                        {unreadCount}
                      </span>
                    )}
                  </button>
                  
                  {showNotifications && (
                    <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
                      <div className="p-4 border-b">
                        <h3 className="text-lg font-semibold text-gray-900">Notificações</h3>
                      </div>
                      {notifications.length === 0 ? (
                        <div className="p-4 text-center text-gray-500">
                          Nenhuma notificação
                        </div>
                      ) : (
                        notifications.slice(0, 10).map((notification) => (
                          <div
                            key={notification.id}
                            className={`p-4 border-b hover:bg-gray-50 cursor-pointer ${
                              !notification.read ? 'bg-blue-50' : ''
                            }`}
                            onClick={() => markNotificationRead(notification.id)}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1">
                                <h4 className="text-sm font-medium text-gray-900">
                                  {notification.title}
                                </h4>
                                <p className="text-sm text-gray-600 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-400 mt-2">
                                  {formatDateTime(notification.created_at)}
                                </p>
                              </div>
                              {!notification.read && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  )}
                </div>

                <div className="text-white flex items-center space-x-2">
                  <span className="bg-yellow-500 text-black px-2 py-1 rounded-full text-sm font-semibold">
                    {user.points} pontos
                  </span>
                  <span>{user.name}</span>
                  <span className="text-xs bg-blue-500 px-2 py-1 rounded">{user.role}</span>
                </div>
                <button
                  onClick={logout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md transition duration-200"
                >
                  Sair
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

const LoginForm = () => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    let result;
    if (isRegistering) {
      result = await register(formData.name, formData.email, formData.password, formData.role);
    } else {
      result = await login(formData.email, formData.password);
    }

    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-purple-600">
            <span className="text-white font-bold text-xl">P</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {isRegistering ? 'Criar Conta' : 'Entrar na Plataforma'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Sistema de Gamificação para Inovação - PUCRS
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            {isRegistering && (
              <div>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Nome completo"
                />
              </div>
            )}
            <div>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Email"
              />
            </div>
            <div>
              <input
                type="password"
                required
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Senha"
              />
            </div>
            {isRegistering && (
              <div>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="appearance-none rounded-lg relative block w-full px-3 py-3 border border-gray-300 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                >
                  <option value="student">Estudante</option>
                  <option value="professor">Professor</option>
                  <option value="admin">Administrador</option>
                </select>
              </div>
            )}
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition duration-200"
            >
              {loading ? 'Carregando...' : (isRegistering ? 'Criar Conta' : 'Entrar')}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => {
                setIsRegistering(!isRegistering);
                setError('');
              }}
              className="text-blue-600 hover:text-blue-500 text-sm font-medium"
            >
              {isRegistering ? 'Já tem conta? Faça login' : 'Não tem conta? Registre-se'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Create Challenge Modal
const CreateChallengeModal = ({ isOpen, close, onChallengeCreated }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'technology',
    difficulty: 'beginner',
    deadline: '',
    criteria: '',
    points_reward: 100,
    tags: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const challengeData = {
        ...formData,
        deadline: new Date(formData.deadline).toISOString(),
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };

      await axios.post(`${API}/challenges`, challengeData, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      onChallengeCreated();
      close();
      setFormData({
        title: '',
        description: '',
        category: 'technology',
        difficulty: 'beginner',
        deadline: '',
        criteria: '',
        points_reward: 100,
        tags: ''
      });
    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao criar desafio');
    }
    setLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Criar Novo Desafio</h2>
            <button
              onClick={close}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Título do Desafio
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: Inovação em Sustentabilidade PUCRS"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descrição
              </label>
              <textarea
                required
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Descreva o desafio em detalhes..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Categoria
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="technology">Tecnologia</option>
                  <option value="sustainability">Sustentabilidade</option>
                  <option value="education">Educação</option>
                  <option value="health">Saúde</option>
                  <option value="innovation">Inovação</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dificuldade
                </label>
                <select
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="beginner">Iniciante</option>
                  <option value="intermediate">Intermediário</option>
                  <option value="advanced">Avançado</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prazo Final
                </label>
                <input
                  type="datetime-local"
                  required
                  value={formData.deadline}
                  onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pontos de Recompensa
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  value={formData.points_reward}
                  onChange={(e) => setFormData({ ...formData, points_reward: parseInt(e.target.value) })}
                  className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Critérios de Avaliação
              </label>
              <textarea
                required
                value={formData.criteria}
                onChange={(e) => setFormData({ ...formData, criteria: e.target.value })}
                rows={3}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: Originalidade, viabilidade técnica, impacto..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tags (separadas por vírgula)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: sustentabilidade, energia, campus"
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={close}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-3 px-4 rounded-lg font-medium transition duration-200"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 px-4 rounded-lg font-medium transition duration-200 disabled:opacity-50"
              >
                {loading ? 'Criando...' : 'Criar Desafio'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Submit Solution Modal
const SubmitSolutionModal = ({ isOpen, close, challenge, onSolutionSubmitted }) => {
  const [formData, setFormData] = useState({
    content: '',
    files: [],
    file_names: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const fileReaders = files.map(file => {
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = () => {
          resolve({
            name: file.name,
            data: reader.result.split(',')[1] // Remove data:type;base64, prefix
          });
        };
        reader.readAsDataURL(file);
      });
    });

    Promise.all(fileReaders).then(results => {
      setFormData({
        ...formData,
        files: [...formData.files, ...results.map(r => r.data)],
        file_names: [...formData.file_names, ...results.map(r => r.name)]
      });
    });
  };

  const removeFile = (index) => {
    const newFiles = formData.files.filter((_, i) => i !== index);
    const newFileNames = formData.file_names.filter((_, i) => i !== index);
    setFormData({ ...formData, files: newFiles, file_names: newFileNames });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/solutions`, {
        challenge_id: challenge.id,
        content: formData.content,
        files: formData.files,
        file_names: formData.file_names
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      onSolutionSubmitted();
      close();
      setFormData({ content: '', files: [], file_names: [] });
    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao enviar solução');
    }
    setLoading(false);
  };

  if (!isOpen || !challenge) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Enviar Solução</h2>
            <button
              onClick={close}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-800">{challenge.title}</h3>
            <p className="text-blue-600 text-sm mt-1">{challenge.description}</p>
            <div className="flex items-center space-x-4 mt-2 text-sm text-blue-600">
              <span>🏆 {challenge.points_reward} pontos</span>
              <span>⏰ {formatDate(challenge.deadline)}</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sua Solução
              </label>
              <textarea
                required
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                rows={6}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Descreva sua solução em detalhes..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Arquivos de Apoio (opcional)
              </label>
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
              />
              <p className="text-xs text-gray-500 mt-1">
                Formatos aceitos: PDF, DOC, DOCX, TXT, JPG, PNG, GIF
              </p>
            </div>

            {formData.file_names.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Arquivos Selecionados
                </label>
                <div className="space-y-2">
                  {formData.file_names.map((fileName, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                      <span className="text-sm text-gray-700">{fileName}</span>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        Remover
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={close}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-3 px-4 rounded-lg font-medium transition duration-200"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white py-3 px-4 rounded-lg font-medium transition duration-200 disabled:opacity-50"
              >
                {loading ? 'Enviando...' : 'Enviar Solução'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

// Evaluate Solution Modal
const EvaluateSolutionModal = ({ isOpen, close, solution, onSolutionEvaluated }) => {
  const [formData, setFormData] = useState({
    score: '',
    feedback: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.put(`${API}/solutions/evaluate`, {
        solution_id: solution.id,
        score: parseInt(formData.score),
        feedback: formData.feedback
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });

      onSolutionEvaluated();
      close();
      setFormData({ score: '', feedback: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao avaliar solução');
    }
    setLoading(false);
  };

  if (!isOpen || !solution) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-screen overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Avaliar Solução</h2>
            <button
              onClick={close}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>

          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold text-gray-800">{solution.challenge_title}</h3>
            <p className="text-gray-600 text-sm mt-1">Por: {solution.user_name}</p>
            <div className="mt-4">
              <h4 className="font-medium text-gray-700 mb-2">Solução:</h4>
              <p className="text-gray-600 whitespace-pre-wrap">{solution.content}</p>
            </div>
            {solution.file_names && solution.file_names.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium text-gray-700 mb-2">Arquivos:</h4>
                <div className="space-y-1">
                  {solution.file_names.map((fileName, index) => (
                    <div key={index} className="text-sm text-blue-600">
                      📎 {fileName}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pontuação (0-100)
              </label>
              <input
                type="number"
                required
                min="0"
                max="200"
                value={formData.score}
                onChange={(e) => setFormData({ ...formData, score: e.target.value })}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Ex: 85"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Feedback para o Participante
              </label>
              <textarea
                required
                value={formData.feedback}
                onChange={(e) => setFormData({ ...formData, feedback: e.target.value })}
                rows={5}
                className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Forneça um feedback construtivo sobre a solução..."
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                {error}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={close}
                className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 py-3 px-4 rounded-lg font-medium transition duration-200"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 px-4 rounded-lg font-medium transition duration-200 disabled:opacity-50"
              >
                {loading ? 'Avaliando...' : 'Salvar Avaliação'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('challenges');
  const [challenges, setChallenges] = useState([]);
  const [solutions, setSolutions] = useState([]);
  const [adminSolutions, setAdminSolutions] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [adminStats, setAdminStats] = useState({});
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    category: '',
    difficulty: '',
    status: ''
  });

  // Modal states
  const [showCreateChallenge, setShowCreateChallenge] = useState(false);
  const [showSubmitSolution, setShowSubmitSolution] = useState(false);
  const [showEvaluateSolution, setShowEvaluateSolution] = useState(false);
  const [selectedChallenge, setSelectedChallenge] = useState(null);
  const [selectedSolution, setSelectedSolution] = useState(null);

  useEffect(() => {
    if (activeTab === 'challenges') {
      fetchChallenges();
    } else if (activeTab === 'solutions') {
      fetchSolutions();
    } else if (activeTab === 'leaderboard') {
      fetchLeaderboard();
    } else if (activeTab === 'admin' && user?.role === 'admin') {
      fetchAdminStats();
      fetchAdminSolutions();
      fetchUsers();
    }
  }, [activeTab, user]);

  const fetchChallenges = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.difficulty) params.append('difficulty', filters.difficulty);
      if (filters.status) params.append('status', filters.status);
      if (searchTerm) params.append('search', searchTerm);

      const response = await axios.get(`${API}/challenges?${params}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setChallenges(response.data);
    } catch (error) {
      console.error('Error fetching challenges:', error);
    }
    setLoading(false);
  };

  const fetchSolutions = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/solutions/my`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setSolutions(response.data);
    } catch (error) {
      console.error('Error fetching solutions:', error);
    }
    setLoading(false);
  };

  const fetchAdminSolutions = async () => {
    try {
      const response = await axios.get(`${API}/solutions`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setAdminSolutions(response.data);
    } catch (error) {
      console.error('Error fetching admin solutions:', error);
    }
  };

  const fetchLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/leaderboard`);
      setLeaderboard(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
    setLoading(false);
  };

  const fetchAdminStats = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/stats`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setAdminStats(response.data);
    } catch (error) {
      console.error('Error fetching admin stats:', error);
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/users`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const toggleUserActive = async (userId) => {
    try {
      await axios.put(`${API}/admin/users/${userId}/toggle-active`, {}, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
      });
      fetchUsers();
    } catch (error) {
      console.error('Error toggling user status:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (activeTab === 'challenges') {
      fetchChallenges();
    }
  };

  const handleFilterChange = (filterType, value) => {
    setFilters({ ...filters, [filterType]: value });
  };

  const getCategoryColor = (category) => {
    const colors = {
      technology: 'bg-blue-100 text-blue-800',
      sustainability: 'bg-green-100 text-green-800',
      education: 'bg-purple-100 text-purple-800',
      health: 'bg-red-100 text-red-800',
      innovation: 'bg-yellow-100 text-yellow-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  const getDifficultyColor = (difficulty) => {
    const colors = {
      beginner: 'bg-green-500',
      intermediate: 'bg-yellow-500',
      advanced: 'bg-red-500'
    };
    return colors[difficulty] || 'bg-gray-500';
  };

  const getBadgeIcon = (badge) => {
    const icons = {
      first_submission: '🏁',
      expert_solver: '🎯',
      innovation_leader: '💡',
      sustainability_champion: '🌱',
      technology_pioneer: '🚀',
      health_advocate: '❤️',
      education_innovator: '📚',
      quick_solver: '⚡',
      top_performer: '👑'
    };
    return icons[badge] || '🏆';
  };

  useEffect(() => {
    if (activeTab === 'challenges') {
      fetchChallenges();
    }
  }, [filters, searchTerm]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h1 className="text-4xl font-bold mb-4">
                Bem-vindo, {user?.name}! 🚀
              </h1>
              <p className="text-xl opacity-90">
                Participe dos desafios de inovação e ajude a construir o futuro da PUCRS
              </p>
            </div>
            <div className="hidden md:block">
              <img 
                src="https://images.unsplash.com/photo-1621009047117-30b97f97965b?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwyfHx1bml2ZXJzaXR5JTIwaW5ub3ZhdGlvbnxlbnwwfHx8Ymx1ZXwxNzUzNTgwNDMzfDA&ixlib=rb-4.1.0&q=85"
                alt="University Innovation"
                className="w-64 h-40 object-cover rounded-lg shadow-lg"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('challenges')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'challenges'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Desafios Disponíveis
            </button>
            <button
              onClick={() => setActiveTab('solutions')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'solutions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Minhas Soluções
            </button>
            <button
              onClick={() => setActiveTab('leaderboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'leaderboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Ranking
            </button>
            {user?.role === 'admin' && (
              <button
                onClick={() => setActiveTab('admin')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'admin'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Administração
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* Challenges Tab */}
        {activeTab === 'challenges' && !loading && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Desafios Ativos</h2>
              {user?.role === 'admin' && (
                <button
                  onClick={() => setShowCreateChallenge(true)}
                  className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-4 py-2 rounded-lg font-medium transition duration-200"
                >
                  + Criar Desafio
                </button>
              )}
            </div>

            {/* Search and Filters */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Buscar desafios..."
                  />
                </div>
                <div className="flex gap-2">
                  <select
                    value={filters.category}
                    onChange={(e) => handleFilterChange('category', e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Todas as categorias</option>
                    <option value="technology">Tecnologia</option>
                    <option value="sustainability">Sustentabilidade</option>
                    <option value="education">Educação</option>
                    <option value="health">Saúde</option>
                    <option value="innovation">Inovação</option>
                  </select>
                  <select
                    value={filters.difficulty}
                    onChange={(e) => handleFilterChange('difficulty', e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Todas as dificuldades</option>
                    <option value="beginner">Iniciante</option>
                    <option value="intermediate">Intermediário</option>
                    <option value="advanced">Avançado</option>
                  </select>
                  <button
                    type="submit"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-200"
                  >
                    Buscar
                  </button>
                </div>
              </form>
            </div>
            
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {challenges.map((challenge) => (
                <div key={challenge.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200">
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{challenge.title}</h3>
                        <p className="text-gray-600 text-sm line-clamp-3">{challenge.description}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 mb-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(challenge.category)}`}>
                        {challenge.category}
                      </span>
                      <div className="flex items-center space-x-1">
                        <div className={`w-2 h-2 rounded-full ${getDifficultyColor(challenge.difficulty)}`}></div>
                        <span className="text-xs text-gray-500 capitalize">{challenge.difficulty}</span>
                      </div>
                    </div>

                    {challenge.tags && challenge.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-4">
                        {challenge.tags.map((tag, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <span>⏰ {formatDate(challenge.deadline)}</span>
                      <span className="font-medium text-yellow-600">🏆 {challenge.points_reward} pts</span>
                    </div>
                    
                    <div className="flex space-x-2">
                      {challenge.user_submitted ? (
                        <span className="flex-1 bg-green-100 text-green-800 py-2 px-4 rounded-md text-center text-sm font-medium">
                          ✅ Enviado
                        </span>
                      ) : challenge.can_submit ? (
                        <button 
                          onClick={() => {
                            setSelectedChallenge(challenge);
                            setShowSubmitSolution(true);
                          }}
                          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium transition duration-200"
                        >
                          Participar
                        </button>
                      ) : (
                        <span className="flex-1 bg-gray-100 text-gray-500 py-2 px-4 rounded-md text-center text-sm font-medium">
                          Prazo Expirado
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Solutions Tab */}
        {activeTab === 'solutions' && !loading && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Minhas Soluções</h2>
            
            {solutions.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">📝</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma solução enviada ainda</h3>
                <p className="text-gray-500">Participe dos desafios para ver suas soluções aqui!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {solutions.map((solution) => (
                  <div key={solution.id} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{solution.challenge_title}</h3>
                        <p className="text-gray-600 text-sm whitespace-pre-wrap">{solution.content}</p>
                        {solution.file_names && solution.file_names.length > 0 && (
                          <div className="mt-3">
                            <p className="text-sm font-medium text-gray-700 mb-1">Arquivos enviados:</p>
                            <div className="flex flex-wrap gap-2">
                              {solution.file_names.map((fileName, index) => (
                                <span key={index} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                  📎 {fileName}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="ml-4">
                        {solution.score !== null ? (
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">{solution.score}</div>
                            <div className="text-xs text-gray-500">pontos</div>
                          </div>
                        ) : (
                          <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                            Aguardando Avaliação
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="text-sm text-gray-500">
                      Enviado em: {formatDateTime(solution.submitted_at)}
                    </div>
                    
                    {solution.feedback && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Feedback do Avaliador:</h4>
                        <p className="text-blue-800 text-sm">{solution.feedback}</p>
                        {solution.evaluated_at && (
                          <p className="text-xs text-blue-600 mt-2">
                            Avaliado em: {formatDateTime(solution.evaluated_at)}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Leaderboard Tab */}
        {activeTab === 'leaderboard' && !loading && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">🏆 Ranking de Inovadores</h2>
            
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="px-6 py-4 bg-gradient-to-r from-yellow-400 to-orange-500">
                <h3 className="text-lg font-semibold text-white">Top Participantes</h3>
              </div>
              
              <div className="divide-y divide-gray-200">
                {leaderboard.slice(0, 20).map((entry) => (
                  <div key={entry.user_id} className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                        entry.rank === 1 ? 'bg-yellow-500' :
                        entry.rank === 2 ? 'bg-gray-400' :
                        entry.rank === 3 ? 'bg-yellow-600' :
                        'bg-blue-500'
                      }`}>
                        {entry.rank}
                      </div>
                      <div>
                        <div className="font-medium text-gray-900">{entry.name}</div>
                        <div className="text-sm text-gray-500 flex items-center space-x-2">
                          <span>{entry.badges.length} badges:</span>
                          <div className="flex space-x-1">
                            {entry.badges.slice(0, 5).map((badge, index) => (
                              <span key={index} className="text-lg">
                                {getBadgeIcon(badge)}
                              </span>
                            ))}
                            {entry.badges.length > 5 && (
                              <span className="text-xs text-gray-400">+{entry.badges.length - 5}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-900">{entry.points} pontos</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Admin Tab */}
        {activeTab === 'admin' && user?.role === 'admin' && !loading && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Painel Administrativo</h2>
            
            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">👥</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-2xl font-bold text-gray-900">{adminStats.total_users}</div>
                    <div className="text-sm text-gray-500">Usuários Ativos</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">🎯</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-2xl font-bold text-gray-900">{adminStats.active_challenges}</div>
                    <div className="text-sm text-gray-500">Desafios Ativos</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">📝</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-2xl font-bold text-gray-900">{adminStats.total_solutions}</div>
                    <div className="text-sm text-gray-500">Soluções Enviadas</div>
                  </div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-red-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">⏳</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-2xl font-bold text-gray-900">{adminStats.pending_evaluations}</div>
                    <div className="text-sm text-gray-500">Pendentes de Avaliação</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Solutions to Evaluate */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold text-gray-900">Soluções para Avaliar</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {adminSolutions.filter(sol => sol.score === null || sol.score === undefined).slice(0, 10).map((solution) => (
                  <div key={solution.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{solution.challenge_title}</h4>
                        <p className="text-sm text-gray-600">Por: {solution.user_name}</p>
                        <p className="text-sm text-gray-500 mt-1 line-clamp-2">{solution.content}</p>
                        <p className="text-xs text-gray-400 mt-2">
                          Enviado em: {formatDateTime(solution.submitted_at)}
                        </p>
                      </div>
                      <button
                        onClick={() => {
                          setSelectedSolution(solution);
                          setShowEvaluateSolution(true);
                        }}
                        className="ml-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition duration-200"
                      >
                        Avaliar
                      </button>
                    </div>
                  </div>
                ))}
                {adminSolutions.filter(sol => sol.score === null || sol.score === undefined).length === 0 && (
                  <div className="px-6 py-4 text-center text-gray-500">
                    Todas as soluções foram avaliadas! 🎉
                  </div>
                )}
              </div>
            </div>

            {/* User Management */}
            <div className="bg-white rounded-lg shadow-md">
              <div className="px-6 py-4 border-b">
                <h3 className="text-lg font-semibold text-gray-900">Gerenciamento de Usuários</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {users.slice(0, 10).map((userData) => (
                  <div key={userData.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{userData.name}</h4>
                        <p className="text-sm text-gray-600">{userData.email}</p>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
                          <span className="capitalize">{userData.role}</span>
                          <span>{userData.points} pontos</span>
                          <span>{userData.badges.length} badges</span>
                          <span>Criado: {formatDate(userData.created_at)}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => toggleUserActive(userData.id)}
                        className={`ml-4 px-4 py-2 rounded-lg text-sm font-medium transition duration-200 ${
                          userData.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {userData.is_active ? 'Desativar' : 'Ativar'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      <CreateChallengeModal
        isOpen={showCreateChallenge}
        close={() => setShowCreateChallenge(false)}
        onChallengeCreated={fetchChallenges}
      />

      <SubmitSolutionModal
        isOpen={showSubmitSolution}
        close={() => setShowSubmitSolution(false)}
        challenge={selectedChallenge}
        onSolutionSubmitted={() => {
          fetchChallenges();
          fetchSolutions();
        }}
      />

      <EvaluateSolutionModal
        isOpen={showEvaluateSolution}
        close={() => setShowEvaluateSolution(false)}
        solution={selectedSolution}
        onSolutionEvaluated={() => {
          fetchAdminSolutions();
          fetchAdminStats();
        }}
      />
    </div>
  );
};

const App = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return user ? <Dashboard /> : <LoginForm />;
};

const AppWithAuth = () => {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
};

export default AppWithAuth;