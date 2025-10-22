import { createRouter, createWebHistory } from 'vue-router'
import PlayerHome from '../views/player/PlayerHome.vue'
import AdminHome from '../views/admin/AdminHome.vue'
import Home from '../views/Home.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/player/:gameId', component: PlayerHome },
  { path: '/admin/:gameId', component: AdminHome }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
