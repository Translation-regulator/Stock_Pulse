import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import TwiiPage from '../pages/TwiiPage.vue'
import StockPage from '../pages/StockPage.vue'


const routes = [
  { path: '/', component: HomePage },
  { path: '/twii', component: TwiiPage },
  { path: '/stock', component: StockPage},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

