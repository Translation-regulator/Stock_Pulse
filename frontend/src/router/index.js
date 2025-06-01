import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import TwiiPage from '../pages/TwiiPage.vue'
import StockPage from '../pages/StockPage.vue'
import PortfolioPage from '../pages/PortfolioPage.vue'
import ChatroomPage from '../pages/ChatroomPage.vue'  
import ChatLobbyPage from '../pages/ChatLobbyPage.vue'

const routes = [
  { path: '/', component: HomePage },
  { path: '/twii', component: TwiiPage },
  { path: '/stock/:stockId?', name: 'StockPage', component: StockPage, props: true },
  { path: '/portfolio', component: PortfolioPage },
  // { path: '/chat', name: 'ChatLobby', component: ChatLobbyPage},
  { path: '/chat', name: 'ChatRoom', component: ChatroomPage},
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
