<template>
  <n-modal
    :show="!isReady"
    display-directive="if"
    :auto-focus="false"
    transform-origin="center"
    :z-index="99999"
  >
    <n-spin :size="50">
      <template #description><n-text> 正在加载... </n-text> </template>
    </n-spin>
  </n-modal>
  <VueFlow
    class="basic-flow"
    :connection-mode="ConnectionMode.Strict"
    :connection-radius="30"
    zoom-activation-key-code="Space"
    :nodeTypes="AllVFNodeTypes"
    fit-view-on-init
    :max-zoom="4"
    :min-zoom="0.1"
    :select-nodes-on-drag="false"
    elevate-edges-on-select
    multi-selection-key-code="Control"
    delete-key-code="Delete"
  >
    <Background />
    <miniMapCtrl />
    <nuipanel />

    <template #edge-normal="customEdgeProps">
      <connected_edge
        :id="customEdgeProps.id"
        :source-x="customEdgeProps.sourceX"
        :source-y="customEdgeProps.sourceY"
        :target-x="customEdgeProps.targetX"
        :target-y="customEdgeProps.targetY"
        :source-position="customEdgeProps.sourcePosition"
        :target-position="customEdgeProps.targetPosition"
        :marker-end="customEdgeProps.markerEnd"
        :style="customEdgeProps.style"
      />
    </template>
    <template #connection-line="{ sourceX, sourceY, targetX, targetY }">
      <connecting_edge
        :source-x="sourceX"
        :source-y="sourceY"
        :target-x="targetX"
        :target-y="targetY"
      />
    </template>
  </VueFlow>
  <ContextMenu v-model:show="showMenu" :options="menuOptions" />
</template>

<style scoped>
.basic-flow {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  background: rgb(0, 0, 0);
}
</style>

<script setup lang="ts">
import {
  ref,
  markRaw,
  onMounted,
  onBeforeMount,
  onBeforeUnmount,
  reactive,
  watch,
  provide,
} from 'vue'
import { NSpin, NText, NModal } from 'naive-ui'
import { ConnectionMode, VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { ContextMenu } from '@imengyu/vue3-context-menu'
import connected_edge from '@/components/edges/connected_edge.vue'
import connecting_edge from '@/components/edges/connecting_edge.vue'
import miniMapCtrl from '@/components/panelctrls/miniMapCtrl.vue'
import nuipanel from '@/components/panelctrls/nuipanel.vue'

import { useVFlowInitial } from '@/hooks/useVFlowInitial'
import { useVFlowManager } from '@/hooks/useVFlowManager'
import { useContextMenu } from '@/hooks/useContextMenu'
import { useVFlowEvents } from '@/hooks/useVFlowEvent'
import { useKeyboardControls } from '@/hooks/useKeyboardControls'
import { useVFlowRequest } from '@/services/useVFlowRequest'

const { AllVFNodeTypes, importAllNodes } = useVFlowInitial()
const { initNodeManagement } = useVFlowManager()
const { initContextMenu, menuOptions, showMenu } = useContextMenu()
const {} = useVFlowEvents()
const {} = useKeyboardControls()
const { onMountedFunc } = useVFlowRequest()
const isReady = ref(false)
onMounted(async () => {
  await importAllNodes()
  initNodeManagement()
  initContextMenu()
  await onMountedFunc()
  isReady.value = true
})
</script>
