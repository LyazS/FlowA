// hooks/useKeyboardControls.ts
import { ref, provide, watch, onBeforeMount, onBeforeUnmount } from 'vue'
import { useVueFlow, type ViewportTransform } from '@vue-flow/core'
import { isEditing } from '@/hooks/useVFlowAttribute'
// 定义鼠标位置的类型
interface MousePosition {
  x: number
  y: number
}
interface KBCtrlInstance {}
// 单例模式
let instance: KBCtrlInstance | null = null

export const useKeyboardControls = () => {
  if (instance) return instance

  const { getViewport, setViewport } = useVueFlow()

  watch(isEditing, (new_val: boolean) => {
    console.log('isEditing', new_val)
  })

  const isSpacePressed = ref<boolean>(false)
  const lastMousePosition = ref<MousePosition>({ x: 0, y: 0 })
  const currentMousePosition = ref<MousePosition>({ x: 0, y: 0 })

  // 始终跟踪鼠标位置
  const trackMousePosition = (event: MouseEvent) => {
    currentMousePosition.value = { x: event.clientX, y: event.clientY }
  }

  // 监听空格键按下和释放
  const handleKeyDown = (event: KeyboardEvent) => {
    if (isEditing.value) return
    if (event.code === 'Space') {
      // 阻止默认行为，防止触发 VueFlow 的内置平移模式
      event.preventDefault()
      isSpacePressed.value = true
      document.body.style.cursor = 'grabbing'
      // 使用当前跟踪的鼠标位置作为起始点
      lastMousePosition.value = { ...currentMousePosition.value }
    }
  }

  const handleKeyUp = (event: KeyboardEvent) => {
    if (isEditing.value) return
    if (event.code === 'Space') {
      isSpacePressed.value = false
      document.body.style.cursor = 'default'
    }
  }

  // 只需要监听鼠标移动事件
  const handleMouseMove = (event: MouseEvent) => {
    trackMousePosition(event)
    if (isEditing.value) return
    if (isSpacePressed.value) {
      const deltaX = event.clientX - lastMousePosition.value.x
      const deltaY = event.clientY - lastMousePosition.value.y

      const cur_viewport: ViewportTransform = getViewport()
      setViewport({
        x: cur_viewport.x + deltaX,
        y: cur_viewport.y + deltaY,
        zoom: cur_viewport.zoom,
      })
      lastMousePosition.value = { x: event.clientX, y: event.clientY }
    }
  }

  const addKBEventListeners = () => {
    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('keyup', handleKeyUp)
    document.addEventListener('mousemove', handleMouseMove)
  }

  const removeKBEventListeners = () => {
    document.removeEventListener('keydown', handleKeyDown)
    document.removeEventListener('keyup', handleKeyUp)
    document.removeEventListener('mousemove', handleMouseMove)
  }

  onBeforeMount(async () => {
    addKBEventListeners()
  })

  onBeforeUnmount(() => {
    removeKBEventListeners()
  })

  instance = {
    isEditing,
  }

  return instance
}
