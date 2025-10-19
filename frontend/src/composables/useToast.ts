import { ref } from 'vue'

export interface Toast {
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    title: string
    message: string
    duration?: number
}

const toasts = ref<Toast[]>([])

export function useToast() {
    function addToast(toast: Omit<Toast, 'id'>) {
        const id = Math.random().toString(36).substr(2, 9)
        const newToast: Toast = {
            id,
            duration: 5000,
            ...toast
        }

        toasts.value.push(newToast)

        return id
    }

    function removeToast(id: string) {
        const index = toasts.value.findIndex(toast => toast.id === id)
        if (index > -1) {
            toasts.value.splice(index, 1)
        }
    }

    function success(title: string, message: string, duration?: number) {
        return addToast({ type: 'success', title, message, duration })
    }

    function error(title: string, message: string, duration?: number) {
        return addToast({ type: 'error', title, message, duration })
    }

    function warning(title: string, message: string, duration?: number) {
        return addToast({ type: 'warning', title, message, duration })
    }

    function info(title: string, message: string, duration?: number) {
        return addToast({ type: 'info', title, message, duration })
    }

    return {
        toasts,
        addToast,
        removeToast,
        success,
        error,
        warning,
        info
    }
}
