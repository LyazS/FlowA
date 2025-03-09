<script setup lang="ts">
import { BaseEdge, getBezierPath, Position } from '@vue-flow/core'
import { computed } from 'vue'

interface Props {
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  sourcePosition: Position
  targetPosition: Position
  markerEnd?: string
  style?: Record<string, any>
}

const props = defineProps<Props>()

const path = computed(() => getBezierPath(props))
</script>

<template>
  <BaseEdge
    :id="id"
    :style="{
      ...style,
      stroke: 'rgb(138, 203, 236)',
      strokeWidth: 2,
    }"
    :path="path[0]"
    :marker-end="markerEnd"
  />
</template>

<style scoped></style>
