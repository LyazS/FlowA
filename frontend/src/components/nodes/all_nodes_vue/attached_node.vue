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
  type VFNodeAttaching,
  type VFNodeAttachingPos,
  VFNodeAttachingPosType,
  VFNodeAttachingType,
} from '@/components/nodes/VFNodeInterface'
import { type VFNode } from '../VFNodeClass'

interface Props {
  id: string
}

const props = defineProps<Props>()
const { findNode } = useVueFlow()
const thisnode = findNode(props.id) as Node
const thisnodedata = thisnode.data as VFNode

// 解构获取位置信息
const thisattaching = computed<VFNodeAttaching>(() => thisnodedata.Attaching!)

// 计算属性
const posLR = computed(() =>
  thisattaching.value.Pos.XType === VFNodeAttachingPosType.Left ? Position.Right : Position.Left,
)
const node_text = computed(() => thisattaching.value.Label)
const handle_style = computed(() =>
  thisattaching.value.Pos.XType === VFNodeAttachingPosType.Left
    ? { right: '2px' }
    : { left: '2px' },
)
const justCont = computed(() =>
  thisattaching.value.Pos.XType === VFNodeAttachingPosType.Left ? 'flex-start' : 'flex-end',
)

const handle_type = computed<HandleType>(() => {
  switch (thisattaching.value.Type) {
    case VFNodeAttachingType.Output:
      return 'target'
    case VFNodeAttachingType.Input:
      return 'source'
    case VFNodeAttachingType.CallbackFunc:
      return 'source'
    case VFNodeAttachingType.CallbackUser:
      return 'target'
    default:
      return 'source'
  }
})

const handle_id = computed<string>(() => {
  switch (thisattaching.value.Type) {
    case VFNodeAttachingType.Output:
      return Object.keys(thisnodedata.Connections.Inputs)[0]
    case VFNodeAttachingType.Input:
      return Object.keys(thisnodedata.Connections.Outputs)[0]
    case VFNodeAttachingType.CallbackFunc:
      return Object.keys(thisnodedata.Connections.CallbackUsers)[0]
    case VFNodeAttachingType.CallbackUser:
      return Object.keys(thisnodedata.Connections.CallbackFuncs)[0]
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
