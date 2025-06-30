import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import TwiiPage from '../pages/TwiiPage.vue'
import StockBrowsePage from '../pages/StockBrowsePage.vue'    
import StockDetailPage from '../pages/StockDetailPage.vue'    
import PortfolioPage from '../pages/PortfolioPage.vue'
import ChatLobbyPage from '../pages/ChatLobbyPage.vue'

const routes = [
  { path: '/', component: HomePage },
  { path: '/twii', component: TwiiPage },

  // 拆成兩條獨立路由
  { path: '/stock', name: 'StockBrowse', component: StockBrowsePage },
  { path: '/stock/:stockId', name: 'StockDetail', component: StockDetailPage, props: true },

  { path: '/portfolio', component: PortfolioPage },
  { path: '/chat', component: ChatLobbyPage }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
