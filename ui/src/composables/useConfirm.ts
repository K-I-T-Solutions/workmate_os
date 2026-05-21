import { ref } from 'vue'

interface ConfirmState {
  message: string
  title: string
  resolve: (value: boolean) => void
}

const pending = ref<ConfirmState | null>(null)

export function useConfirm() {
  function confirm(message: string, title = 'Bestätigung'): Promise<boolean> {
    return new Promise((resolve) => {
      pending.value = { message, title, resolve }
    })
  }

  function accept() {
    pending.value?.resolve(true)
    pending.value = null
  }

  function cancel() {
    pending.value?.resolve(false)
    pending.value = null
  }

  return { pending, confirm, accept, cancel }
}
