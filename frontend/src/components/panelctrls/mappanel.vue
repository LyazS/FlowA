<script setup lang="ts">
import { computed } from 'vue'
import { NButton, NPopover, NFlex, NIcon } from 'naive-ui'
import { AddSharp, RemoveSharp, ScanSharp, LockOpenOutline, LockClosed } from '@vicons/ionicons5'
import { useVueFlow } from '@vue-flow/core'

const {
  nodesDraggable,
  nodesConnectable,
  elementsSelectable,
  setInteractive,
  zoomIn,
  zoomOut,
  fitView,
  viewport,
  minZoom,
  maxZoom,
} = useVueFlow()
const isInteractive = computed(
  () => nodesDraggable.value || nodesConnectable.value || elementsSelectable.value,
)
const minZoomReached = computed(() => viewport.value.zoom <= minZoom.value)
const maxZoomReached = computed(() => viewport.value.zoom >= maxZoom.value)
</script>

<template>
  <n-flex justify="flex-end">
    <n-popover trigger="hover">
      <template #trigger>
        <n-button
          class="glow-btn"
          :disabled="maxZoomReached"
          circle
          tertiary
          type="success"
          @click="zoomIn()"
        >
          <template #icon>
            <n-icon>
              <AddSharp />
            </n-icon>
          </template>
        </n-button>
      </template>
      <span>放大</span>
    </n-popover>
    <n-popover trigger="hover">
      <template #trigger>
        <n-button
          class="glow-btn"
          :disabled="minZoomReached"
          circle
          tertiary
          type="success"
          @click="zoomOut()"
        >
          <template #icon>
            <n-icon>
              <RemoveSharp />
            </n-icon>
          </template>
        </n-button>
      </template>
      <span>缩小</span>
    </n-popover>
    <n-popover trigger="hover">
      <template #trigger>
        <n-button class="glow-btn" circle tertiary type="success" @click="fitView()">
          <template #icon>
            <n-icon>
              <ScanSharp />
            </n-icon>
          </template>
        </n-button>
      </template>
      <span>视图适应</span>
    </n-popover>
    <n-popover trigger="hover">
      <template #trigger>
        <n-button
          class="glow-btn"
          circle
          tertiary
          type="success"
          @click="setInteractive(!isInteractive)"
        >
          <template #icon>
            <n-icon>
              <template v-if="isInteractive">
                <LockOpenOutline />
              </template>
              <template v-else>
                <LockClosed />
              </template>
            </n-icon>
          </template>
        </n-button>
      </template>
      <span>锁定</span>
    </n-popover>
  </n-flex>
</template>

<style scoped></style>
