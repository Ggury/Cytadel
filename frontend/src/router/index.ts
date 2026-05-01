import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { 
    path: '/login', 
    name: 'Login',
    component: () => import('../pages/Login.vue') 
  },
  { 
    path: '/profile', 
    name: 'Profile',
    component: () => import('../pages/Profile.vue') 
  },
  {
    path: '/register',
    name: 'Registration',
    component: () => import('../pages/Register.vue')
  },
  { 
    path: '/', 
    redirect: '/login' 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router