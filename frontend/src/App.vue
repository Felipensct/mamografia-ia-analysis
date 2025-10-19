<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <RouterView />
    
    <!-- Toast Notifications -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :type="toast.type"
        :title="toast.title"
        :message="toast.message"
        :duration="toast.duration"
        @close="removeToast(toast.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import Toast from '@/components/Toast.vue'
import { useToast } from '@/composables/useToast'
import { RouterView } from 'vue-router'

const { toasts, removeToast } = useToast()
</script>