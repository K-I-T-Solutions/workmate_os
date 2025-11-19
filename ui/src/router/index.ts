import { createRouter, createWebHistory } from 'vue-router'
import UnderConstruction from '../pages/UnderConstruction.vue'
import Linktree from '../pages/Linktree.vue'

const routes = [
  { path: '/', redirect: '/under-construction' },
  { path: '/under-construction', component: UnderConstruction },
  {path: '/linktree', component: Linktree},
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
