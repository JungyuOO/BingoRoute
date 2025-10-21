export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  FIND_ID: '/find-id',
  FIND_PASSWORD: '/find-password',
  MYPAGE: '/mypage',
  MYPLANS: '/myplans', // ⭐ 추가
  PLANNER: '/planner',
  PLACE: '/place/:id',
  PLACE_DETAIL: (id) => `/place/${id}`,
}

export const ROUTE_META = {
  [ROUTES.HOME]: {
    title: '빙고루트',
    requiresAuth: false,
  },
  [ROUTES.LOGIN]: {
    title: '로그인',
    requiresAuth: false,
  },
  [ROUTES.SIGNUP]: {
    title: '회원가입',
    requiresAuth: false,
  },
  [ROUTES.FIND_ID]: {
    title: '아이디 찾기',
    requiresAuth: false,
  },
  [ROUTES.FIND_PASSWORD]: {
    title: '비밀번호 찾기',
    requiresAuth: false,
  },
  [ROUTES.MYPAGE]: {
    title: '내 정보',
    requiresAuth: true,
  },
  [ROUTES.PLANNER]: {
    title: 'AI 여행 플래너',
    requiresAuth: true,
  },
  [ROUTES.PLACE]: {
    title: '장소 상세',
    requiresAuth: false,
  },
}
