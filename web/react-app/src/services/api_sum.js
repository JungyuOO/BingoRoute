// ⭐ 실제 코드 아니고 참고자료로만 보기
// 앤드포인트를 불러오는 시작점
// 다른 서비스들이 여기서 불러옴

// src/services/api.js
import axios from "axios";

// 백엔드 서버 주소 (Docker나 로컬 환경에 맞게 수정)
export const API_BASE_URL = "http://localhost:8000"; // 기본 주소

// axios 인스턴스 생성 (공통 설정)
export const api = axios.create({
  baseURL: API_BASE_URL, // 기본 주소로 자동 요청
  headers: {
    "Content-Type": "application/json",
  },
});