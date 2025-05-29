import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import TwiiPage from '../pages/TwiiPage.vue'
import StockPage from '../pages/StockPage.vue'
import PortfolioPage from '../pages/PortfolioPage.vue'
import ChatRoom from '../pages/ChatroomPage.vue'  

const routes = [
  { path: '/', component: HomePage },
  { path: '/twii', component: TwiiPage },
  { path: '/stock/:stockId?', name: 'StockPage', component: StockPage, props: true },
  { path: '/portfolio', component: PortfolioPage },
  { path: '/chat', redirect: '/chat/default' },
  { path: '/chat/:roomId', name: 'ChatRoom', component: ChatRoom, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
