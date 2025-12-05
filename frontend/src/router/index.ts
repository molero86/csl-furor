import { createRouter, createWebHistory } from 'vue-router'
import PlayerHome from '../views/player/PlayerHome.vue'
import AdminHome from '../views/admin/AdminHome.vue'
import AdminFirstPhase from '../views/admin/AdminFirstPhase.vue'
import AdminSecondPhase from '../views/admin/AdminSecondPhase.vue'
import AdminThirdPhase from '../views/admin/AdminThirdPhase.vue'
import AdminFourthPhase from '../views/admin/AdminFourthPhase.vue'
import FinalScores from '../views/admin/FinalScores.vue'
import Configuration from '../views/admin/Configuration.vue'
import Home from '../views/Home.vue'
import FirstPhase from '../views/player/FirstPhase.vue'
import SecondPhase from '../views/player/SecondPhase.vue'
import ThirdPhase from '../views/player/ThirdPhase.vue'
import FourthPhase from '../views/player/FourthPhase.vue'


const routes = [
  { path: '/', component: Home },
  { path: '/player/:gameId', component: PlayerHome },
  { path: '/player/:gameId/1', component: FirstPhase },
  { path: '/player/:gameId/2', component: SecondPhase },
  { path: '/player/:gameId/3', component: ThirdPhase },
  { path: '/player/:gameId/4', component: FourthPhase },
  { path: '/admin/:gameId', component: AdminHome },
  { path: '/admin/:gameId/2', component: AdminSecondPhase },
  { path: '/admin/:gameId/3', component: AdminThirdPhase },
  { path: '/admin/:gameId/4', component: AdminFourthPhase },
  { path: '/admin/:gameId/1', component: AdminFirstPhase },
  { path: '/admin/:gameId/final-scores', component: FinalScores },
  { path: '/configuration', component: Configuration }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
