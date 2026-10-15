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

const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/create-meetup',
    name: 'CreateMeetup',
    component: MeetupCreateView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/meetup/:id',
    name: 'MeetupDetail',
    component: MeetupDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/meetup/:id/tasks',
    name: 'MeetupTasks',
    component: TaskListView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/meetup/:id/tasks/:taskId/submit',
    name: 'TaskSubmit',
    component: TaskSubmitView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/meetup/:id/tasks/manage',
    name: 'TaskManage',
    component: TaskManageView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/meetup/:id/tasks/:taskId/submissions',
    name: 'TaskSubmissions',
    component: TaskSubmissionsView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/help',
    name: 'Help',
    component: HelpView,
  },
  {
    path: '/reviews',
    name: 'Reviews',
    component: ReviewFeedView,
  },
  {
    path: '/write-review',
    name: 'WriteReview',
    component: WriteReviewView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/write-review/:meetupId',
    name: 'WriteReviewForMeetup',
    component: WriteReviewView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/meetup/:id/payment-link',
    name: 'MeetupPaymentLink',
    component: MeetupPaymentLinkView,
    meta: { requiresAuth: true, requiresNonGuest: true },
  },
  {
    path: '/pay/:token',
    name: 'PaymentQR',
    component: PaymentQRView,
  },
  {
    path: '/lite',
    component: () => import('@/lite/views/LiteLayout.vue'),
    children: [
      { path: '', name: 'LiteHome', component: () => import('@/lite/views/LiteHome.vue') },
      { path: 'm/:id', name: 'LiteRoom', component: () => import('@/lite/views/LiteRoom.vue') },
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
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  // LITE는 별도 토큰 인증을 쓰므로 기존 authStore 검사를 건너뛴다
  if (to.path === '/lite' || to.path.startsWith('/lite/')) {
    next()
    return
  }

  const authStore = useAuthStore()
  
  // 로그인 상태 확인
  authStore.checkAuth()
  
  if (to.meta.requiresGuest && authStore.isLoggedIn) {
    // 로그인된 사용자가 게스트 페이지 접근 시
    if (authStore.isAdmin) {
      next('/admin')
    } else {
      next('/dashboard')
    }
  } else if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // 인증이 필요한 페이지에 비로그인 사용자 접근 시
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    // 관리자 페이지에 일반 사용자 접근 시
    next('/dashboard')
  } else if (to.meta.requiresNonGuest && authStore.isGuest) {
    // 게스트가 접근할 수 없는 페이지에 게스트 접근 시
    next('/dashboard')
  } else {
    next()
  }
})

export default router