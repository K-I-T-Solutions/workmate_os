import { createRouter, createWebHistory } from 'vue-router'
import UnderConstruction from '../pages/UnderConstruction.vue'
import Linktree from '../pages/Linktree.vue'
import MainPage from '../pages/MainPage.vue'

const routes = [
  { path: '/', redirect: '/under-construction' },
  { path: '/under-construction', component: UnderConstruction },
  {path: '/linktree', component: Linktree},
  {path:'/main' , component: MainPage}
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
