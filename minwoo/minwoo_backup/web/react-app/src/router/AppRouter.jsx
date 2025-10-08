import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from '../components/Layout'
import RequireAuth from '../components/auth/RequireAuth'
import MainView from '../views/MainView'
import LoginView from '../views/LoginView'
import SignupView from '../views/SignupView'
import MyPageView from '../views/MyPageView'
import ChatbotView from '../views/ChatbotView'
import PlaceView from '../views/PlaceView'

const AppRouter = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<MainView />} />
          <Route path="/login" element={<LoginView />} />
          <Route path="/signup" element={<SignupView />} />
          <Route path="/mypage" element={<RequireAuth><MyPageView /></RequireAuth>} />
          <Route path="/planner" element={<RequireAuth><ChatbotView /></RequireAuth>} />
          <Route path="/place/:id" element={<PlaceView />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default AppRouter
