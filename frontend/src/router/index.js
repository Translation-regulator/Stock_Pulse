import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import TwiiPage from '../pages/TwiiPage.vue'

const routes = [
  { path: '/', component: HomePage },
  { path: '/twii', component: TwiiPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

