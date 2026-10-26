import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import AdminView from '@/views/AdminView.vue'
import MeetupCreateView from '@/views/MeetupCreateView.vue'
import MeetupDetailView from '@/views/MeetupDetailView.vue'
import TaskListView from '@/views/TaskListView.vue'
import TaskSubmitView from '@/views/TaskSubmitView.vue'
import TaskManageView from '@/views/TaskManageView.vue'
import TaskSubmissionsView from '@/views/TaskSubmissionsView.vue'
import SettingsView from '@/views/SettingsView.vue'
import HelpView from '@/views/HelpView.vue'
import ReviewFeedView from '@/views/ReviewFeedView.vue'
import WriteReviewView from '@/views/WriteReviewView.vue'
import MeetupPaymentLinkView from '@/views/MeetupPaymentLinkView.vue'
import PaymentQRView from '@/views/PaymentQRView.vue'

// 예전 주소로 들어오면 /legacy 아래 같은 화면으로 보낸다. /admin은 LITE 운영자 화면이 쓰므로 넣지 않는다.
const LEGACY_PATHS = [
  '/dashboard',
  '/login',
  '/register',
  '/create-meetup',
  '/meetup/:rest(.*)',
  '/settings',
  '/help',
  '/reviews',
  '/write-review/:rest(.*)?',
  '/pay/:token',
]

const toLegacy = (to) => ({ path: `/legacy${to.path}`, query: to.query, hash: to.hash })

const routes = [
  // LITE가 메인이다. 예전에 공유한 /lite/... 링크는 /lite를 떼고 보낸다(복구·운영자 링크의 #fragment 유지).
  {
    path: '/lite/:rest(.*)*',
    redirect: (to) => ({ path: to.path.replace(/^\/lite/, '') || '/', query: to.query, hash: to.hash }),
  },
  {
    path: '/',
    component: () => import('@/lite/views/LiteLayout.vue'),
    children: [
      { path: '', name: 'LiteHome', component: () => import('@/lite/views/LiteHome.vue') },
      { path: 'm/:id', name: 'LiteRoom', component: () => import('@/lite/views/LiteRoom.vue') },
      { path: 'm/:id/info', name: 'LiteMeetupDetail', component: () => import('@/lite/views/LiteMeetupDetail.vue') },
      { path: 'seminar', name: 'LiteSeminar', component: () => import('@/lite/views/LiteSeminar.vue') },
      { path: 'seminar/:id', name: 'LiteSeminarHost', component: () => import('@/lite/views/LiteSeminar.vue') },
      { path: 'requests', name: 'LiteRequests', component: () => import('@/lite/views/LiteRequests.vue') },
      { path: 'new-request', name: 'LiteRequestNew', component: () => import('@/lite/views/LiteRequestNew.vue') },
      { path: 'new-meetup', name: 'LiteMeetupNew', component: () => import('@/lite/views/LiteMeetupNew.vue') },
      { path: 'admin', name: 'LiteAdmin', component: () => import('@/lite/views/LiteAdmin.vue') },
      { path: 'admin/m/:id', name: 'LiteAdminMeetup', component: () => import('@/lite/views/LiteAdminMeetup.vue') },
      { path: 'r', name: 'LiteRecover', component: () => import('@/lite/views/LiteRecover.vue') },
      { path: 'host', name: 'LiteHostClaim', component: () => import('@/lite/views/LiteHostClaim.vue') },
    ],
  },
  {
    path: '/legacy',
    redirect: '/legacy/dashboard',
  },
  {
    path: '/legacy/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true },
  },
  {
    path: '/legacy/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true },
  },
  {
    path: '/legacy/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/legacy/create-meetup',
    name: 'CreateMeetup',
    component: MeetupCreateView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/meetup/:id',
    name: 'MeetupDetail',
    component: MeetupDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/legacy/meetup/:id/tasks',
    name: 'MeetupTasks',
    component: TaskListView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/meetup/:id/tasks/:taskId/submit',
    name: 'TaskSubmit',
    component: TaskSubmitView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/meetup/:id/tasks/manage',
    name: 'TaskManage',
    component: TaskManageView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/meetup/:id/tasks/:taskId/submissions',
    name: 'TaskSubmissions',
    component: TaskSubmissionsView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/admin',
    name: 'Admin',
    component: AdminView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/legacy/help',
    name: 'Help',
    component: HelpView,
  },
  {
    path: '/legacy/reviews',
    name: 'Reviews',
    component: ReviewFeedView,
  },
  {
    path: '/legacy/write-review',
    name: 'WriteReview',
    component: WriteReviewView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/write-review/:meetupId',
    name: 'WriteReviewForMeetup',
    component: WriteReviewView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/meetup/:id/payment-link',
    name: 'MeetupPaymentLink',
    component: MeetupPaymentLinkView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/legacy/pay/:token',
    name: 'PaymentQR',
    component: PaymentQRView,
  },
  ...LEGACY_PATHS.map((path) => ({ path, redirect: toLegacy })),
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  // LITE는 별도 토큰 인증을 쓰므로 기존 authStore 검사는 /legacy 화면에만 한다
  if (to.path !== '/legacy' && !to.path.startsWith('/legacy/')) {
    next()
    return
  }

  const authStore = useAuthStore()
  
  // 로그인 상태 확인
  authStore.checkAuth()
  
  if (to.meta.requiresGuest && authStore.isLoggedIn) {
    // 로그인된 사용자가 게스트 페이지 접근 시
    if (authStore.isAdmin) {
      next('/legacy/admin')
    } else {
      next('/legacy/dashboard')
    }
  } else if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // 인증이 필요한 페이지에 비로그인 사용자 접근 시
    next('/legacy/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    // 관리자 페이지에 일반 사용자 접근 시
    next('/legacy/dashboard')
  } else if (to.meta.requiresNonGuest && authStore.isGuest) {
    // 게스트가 접근할 수 없는 페이지에 게스트 접근 시
    next('/legacy/dashboard')
  } else {
    next()
  }
})

export default router