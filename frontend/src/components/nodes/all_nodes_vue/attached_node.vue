<template>
  <div class="node-container">
    <div class="corner-text" :style="{ justifyContent: justCont }">
      {{ node_text }}
    </div>
    <Handle :id="handle_id" :type="handle_type" :position="posLR" :style="handle_style" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { Position, Handle, useVueFlow, type Node, type HandleType } from '@vue-flow/core'
import {
  type AttachedVFNodeData,
  VFNodeAttachingPos,
  VFNodeAttachingType,
} from '@/components/nodes/VFNodeInterface'

interface Props {
  id: string
  data: AttachedVFNodeData
}

const props = defineProps<Props>()
const { findNode } = useVueFlow()
const thisnode = findNode(props.id) as Node

// 解构获取位置信息
const [yPart, yPos, xPart, xPos] = props.data.attaching.pos

// 计算属性
const posLR = computed(() => (xPart === VFNodeAttachingPos.left ? Position.Right : Position.Left))
const node_text = computed(() => props.data.attaching.label)
const handle_style = computed(() =>
  xPart === VFNodeAttachingPos.left ? { right: '2px' } : { left: '2px' },
)
const justCont = computed(() => (xPart === VFNodeAttachingPos.left ? 'flex-start' : 'flex-end'))

// 处理 handle 类型
type HandleId = 'input' | 'output' | 'callbackUser' | 'callbackFunc'

const handle_type = computed<HandleType>(() => {
  switch (props.data.attaching.type) {
    case VFNodeAttachingType.output:
      return 'target'
    case VFNodeAttachingType.input:
      return 'source'
    case VFNodeAttachingType.callbackFunc:
      return 'source'
    case VFNodeAttachingType.callbackUser:
      return 'target'
    default:
      return 'source'
  }
})

const handle_id = computed<HandleId>(() => {
  switch (props.data.attaching.type) {
    case VFNodeAttachingType.output:
      return 'input'
    case VFNodeAttachingType.input:
      return 'output'
    case VFNodeAttachingType.callbackFunc:
      return 'callbackUser'
    case VFNodeAttachingType.callbackUser:
      return 'callbackFunc'
    default:
      return 'output'
  }
})

onMounted(() => {
  if (thisnode) {
    thisnode.class = 'vue-flow__node-attached_node'
  }
})
</script>

<style>
.vue-flow__node-attached_node {
  pointer-events: none;
  border: 1px solid rgb(52, 52, 56);
  padding: 3px;
  border-radius: 6px;
}

.vue-flow__node-attached_node:hover {
  box-shadow: 0 0 0px;
  border: 1px solid rgb(52, 52, 56);
  box-shadow: 0 0 0px rgb(52, 52, 56);
}
</style>
<style scoped>
.node-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.corner-text {
  font-size: 4px;
  color: white;
  font-family: var(--font-mono);
  letter-spacing: 0.1px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  display: flex;
  height: auto;
  text-align: center;
}
</style>
