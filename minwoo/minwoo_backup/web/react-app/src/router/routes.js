// 라우트 경로 상수 정의
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  MYPAGE: '/mypage',
  PLANNER: '/planner',
  PLACE: '/place/:id',
  PLACE_DETAIL: (id) => `/place/${id}`
}

// 라우트 메타데이터
export const ROUTE_META = {
  [ROUTES.HOME]: {
    title: '빙고루트',
    requiresAuth: false
  },
  [ROUTES.LOGIN]: {
    title: '로그인',
    requiresAuth: false
  },
  [ROUTES.SIGNUP]: {
    title: '회원가입',
    requiresAuth: false
  },
  [ROUTES.MYPAGE]: {
    title: '내 정보',
    requiresAuth: true
  },
  [ROUTES.PLANNER]: {
    title: 'AI 여행 플래너',
    requiresAuth: true
  },
  [ROUTES.PLACE]: {
    title: '장소 상세',
    requiresAuth: false
  }
}
