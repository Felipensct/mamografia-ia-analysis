import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/analyses',
      name: 'analyses',
      component: () => import('../views/AnalysesView.vue'),
    },
    {
      path: '/analysis/:id',
      name: 'analysis-detail',
      component: () => import('../views/AnalysisDetailView.vue'),
      props: true,
    },
  ],
})

export default router
