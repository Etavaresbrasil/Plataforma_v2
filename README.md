# Sistema de Gamificação para Engajamento em Inovação - PUCRS

Uma plataforma web completa desenvolvida em Python para promover colaboração e inovação na PUCRS através de gamificação.

## 🎯 Sobre o Projeto

Sistema desenvolvido como TCC de pós-graduação que demonstra inovação tecnológica aplicada ao ambiente acadêmico. A plataforma permite que estudantes, professores e pesquisadores participem de desafios de inovação, submetam soluções criativas e sejam reconhecidos através de um sistema de gamificação completo.

## ✨ Funcionalidades Principais

### 🔐 Sistema de Autenticação
- Cadastro e login seguro com JWT
- Perfis diferenciados: Admin, Estudante, Professor
- Recuperação de senha e gerenciamento de contas

### 🎯 Gestão de Desafios
- **Admins podem:**
  - Criar desafios com categorias (Tecnologia, Sustentabilidade, Educação, Saúde, Inovação)
  - Definir níveis de dificuldade (Iniciante, Intermediário, Avançado)
  - Estabelecer prazos e critérios de avaliação
  - Gerenciar pontuação e recompensas

### 💡 Submissão de Soluções
- Editor de conteúdo para descrição detalhada
- Upload de arquivos (documentos, imagens, vídeos)
- Histórico completo de submissões
- Versionamento de respostas

### 📊 Sistema de Avaliação
- **Admins podem:**
  - Avaliar soluções com pontuação personalizada
  - Fornecer feedback detalhado
  - Acompanhar progresso dos participantes

### 🏆 Gamificação Completa
- **Sistema de Pontos**: Ganhe pontos por participação e qualidade
- **Badges Automáticas**: 9 tipos diferentes de conquistas
  - 🏁 Primeira Submissão
  - 🎯 Solucionador Expert
  - 💡 Líder em Inovação
  - 🌱 Campeão da Sustentabilidade
  - 🚀 Pioneiro em Tecnologia
  - ❤️ Defensor da Saúde
  - 📚 Inovador em Educação
  - ⚡ Solucionador Rápido
  - 👑 Alto Desempenho

### 📈 Dashboard Interativo
- **Para Usuários:**
  - Desafios disponíveis com filtros avançados
  - Progresso pessoal e histórico
  - Ranking e leaderboard
  - Sistema de notificações em tempo real

- **Para Admins:**
  - Métricas detalhadas do sistema
  - Gerenciamento de usuários
  - Painel de avaliação de soluções
  - Estatísticas de engajamento

### 🔍 Sistema de Busca Avançado
- Busca inteligente por título, descrição e tags
- Filtros por categoria, dificuldade e status
- Resultados organizados e relevantes

### 🔔 Notificações em Tempo Real
- Novos desafios disponíveis
- Avaliações recebidas
- Badges conquistadas
- Atualizações do sistema

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework Python moderno e rápido
- **MongoDB**: Banco de dados NoSQL flexível
- **JWT**: Autenticação segura
- **bcrypt**: Criptografia de senhas
- **Motor**: Driver assíncrono para MongoDB

### Frontend
- **React**: Biblioteca JavaScript para UI
- **Tailwind CSS**: Framework CSS utilitário
- **Axios**: Cliente HTTP para API
- **Context API**: Gerenciamento de estado

### Design
- **Interface Responsiva**: Funciona em desktop, tablet e mobile
- **Design Moderno**: Gradientes, animações e micro-interações
- **UX/UI Profissional**: Ícones, ilustrações e elementos gamificados

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8+
- Node.js 14+
- MongoDB
- Git

### Backend
```bash
cd backend
pip install -r requirements.txt
python server.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

### Configuração
1. Configure as variáveis de ambiente no `.env`
2. Certifique-se que o MongoDB está rodando
3. Acesse http://localhost:3000

## 📦 Deploy no PythonAnywhere

O sistema está otimizado para deploy gratuito no PythonAnywhere. Consulte o arquivo `DEPLOY_PYTHONWHERYWHERE.md` para instruções detalhadas.

### Características para Produção
- ✅ Upload de arquivos em base64 (sem necessidade de storage externo)
- ✅ Banco de dados MongoDB Atlas gratuito
- ✅ CORS configurado corretamente
- ✅ JWT com segurança robusta
- ✅ Interface otimizada para performance

## 🎨 Screenshots

### Dashboard Principal
Interface limpa e intuitiva com desafios organizados por categorias

### Sistema de Badges
Reconhecimento visual das conquistas dos usuários

### Painel Administrativo
Ferramentas completas para gestão do sistema

## 📊 Métricas do Sistema

### Funcionalidades Implementadas
- ✅ 15+ endpoints de API RESTful
- ✅ 8 telas principais de interface
- ✅ 9 tipos de badges automáticas
- ✅ Sistema completo de notificações
- ✅ Upload e gerenciamento de arquivos
- ✅ Busca e filtros avançados

### Testagem
- ✅ 68 testes automatizados passando
- ✅ Cobertura completa de funcionalidades
- ✅ Testes de integração frontend/backend
- ✅ Validação de segurança e permissões

## 🏫 Contexto Acadêmico

### Aplicação na PUCRS
- **Estudantes**: Participam de desafios e desenvolvem soluções
- **Professores**: Podem propor desafios e orientar participantes
- **Pesquisadores**: Colaboram com expertise técnica
- **Administradores**: Gerenciam todo o ecossistema

### Categorias de Desafios
- **Tecnologia**: IoT, AI, desenvolvimento de software
- **Sustentabilidade**: Eficiência energética, gestão de resíduos
- **Educação**: Metodologias inovadoras, tecnologia educacional
- **Saúde**: Telemedicina, wellness, equipamentos médicos
- **Inovação**: Startups, empreendedorismo, novos modelos de negócio

## 🤝 Contribuição

Este é um projeto acadêmico desenvolvido para demonstrar inovação tecnológica no ambiente universitário. Contribuições são bem-vindas para:

- Novas funcionalidades de gamificação
- Melhorias na interface do usuário
- Otimizações de performance
- Recursos de acessibilidade
- Integrações com outras plataformas

## 📄 Licença

Projeto desenvolvido para fins acadêmicos - PUCRS 2025

## 👥 Equipe

Desenvolvido como Sistema de TCC demonstrando aplicação de tecnologias modernas na educação e inovação universitária.

---

🚀 **Pronto para transformar a inovação na PUCRS!**

Sistema completo, testado e otimizado para promover engajamento e colaboração através de gamificação inteligente.
