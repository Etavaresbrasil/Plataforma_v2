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

// Components
const Navbar = () => {
  const { user, logout } = useAuth();

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

const Dashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('challenges');
  const [challenges, setChallenges] = useState([]);
  const [solutions, setSolutions] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [adminStats, setAdminStats] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'challenges') {
      fetchChallenges();
    } else if (activeTab === 'solutions') {
      fetchSolutions();
    } else if (activeTab === 'leaderboard') {
      fetchLeaderboard();
    } else if (activeTab === 'admin' && user?.role === 'admin') {
      fetchAdminStats();
    }
  }, [activeTab, user]);

  const fetchChallenges = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/challenges`, {
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
              <div className="flex items-center space-x-2">
                <img 
                  src="https://images.unsplash.com/photo-1664526937033-fe2c11f1be25?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1NzZ8MHwxfHNlYXJjaHwxfHxjb2xsYWJvcmF0aW9uJTIwdGVjaG5vbG9neXxlbnwwfHx8Ymx1ZXwxNzUzNTgwNDM4fDA&ixlib=rb-4.1.0&q=85"
                  alt="Collaboration Technology"
                  className="w-8 h-8 rounded"
                />
                <span className="text-sm text-gray-600">{challenges.length} desafios disponíveis</span>
              </div>
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
                    
                    <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                      <span>⏰ {new Date(challenge.deadline).toLocaleDateString('pt-BR')}</span>
                      <span className="font-medium text-yellow-600">🏆 {challenge.points_reward} pts</span>
                    </div>
                    
                    <div className="flex space-x-2">
                      {challenge.user_submitted ? (
                        <span className="flex-1 bg-green-100 text-green-800 py-2 px-4 rounded-md text-center text-sm font-medium">
                          ✅ Enviado
                        </span>
                      ) : challenge.can_submit ? (
                        <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium transition duration-200">
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
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Solução #{solution.id.slice(0, 8)}</h3>
                        <p className="text-gray-600 text-sm">{solution.content}</p>
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
                      Enviado em: {new Date(solution.submitted_at).toLocaleDateString('pt-BR')}
                    </div>
                    
                    {solution.feedback && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-blue-900 mb-2">Feedback do Avaliador:</h4>
                        <p className="text-blue-800 text-sm">{solution.feedback}</p>
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
                {leaderboard.slice(0, 10).map((entry) => (
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
                        <div className="text-sm text-gray-500">{entry.badges.length} badges</div>
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
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
                    <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">✅</span>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="text-2xl font-bold text-gray-900">{adminStats.evaluated_solutions}</div>
                    <div className="text-sm text-gray-500">Soluções Avaliadas</div>
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
            
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-yellow-400">⚠️</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-yellow-700">
                    <strong>Recursos administrativos em desenvolvimento:</strong> Criação de desafios, avaliação de soluções e gerenciamento de usuários serão implementados na próxima versão.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
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