import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '../components/layout'
import { RequireAuth } from '../components/features/auth'
import HomePage from '../pages/HomePage'
import LoginView from '../views/LoginView'
import SignupView from '../views/SignupView'
import FindIdView from '../views/FindIdView'
import FindPasswordView from '../views/FindPasswordView'
import MyPageView from '../views/MyPageView'
import ChatbotView from '../views/ChatbotView'
import { ROUTES } from './routes'

const AppRouter = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          {/* ✅ 홈 */}
          <Route path={ROUTES.HOME} element={<HomePage />} />

          {/* ✅ 로그인 / 회원가입 / 계정찾기 */}
          <Route path={ROUTES.LOGIN} element={<LoginView />} />
          <Route path={ROUTES.SIGNUP} element={<SignupView />} />
          <Route path={ROUTES.FIND_ID} element={<FindIdView />} />
          <Route path={ROUTES.FIND_PASSWORD} element={<FindPasswordView />} />

          {/* ✅ 마이페이지 (여행 계획 리스트 포함) */}
          <Route
            path={ROUTES.MYPAGE}
            element={
              <RequireAuth>
                <MyPageView />
              </RequireAuth>
            }
          />

          {/* ✅ 챗봇 (여행 계획 세우기) */}
          <Route
            path={ROUTES.PLANNER}
            element={
              <RequireAuth>
                <ChatbotView />
              </RequireAuth>
            }
          />

          {/* ✅ 장소 */}
          <Route path={ROUTES.PLACE} element={<HomePage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default AppRouter
