<script setup lang="ts">
import { BaseEdge, getBezierPath, Position } from '@vue-flow/core'
import { computed, ref, watch } from 'vue'

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
  data?: any
}

const props = defineProps<Props>()
const isHovered = computed(() => props.data?.isHovered)
const path = computed(() => getBezierPath(props))
</script>

<template>
  <BaseEdge
    :id="id"
    :style="{
      ...style,
      stroke: isHovered ? '#FFDF00' : 'rgb(138, 203, 236)',
      strokeWidth: 2,
      filter: isHovered
        ? `
        drop-shadow(0 0 4px rgba(255, 215, 0, 0.7))
        drop-shadow(0 0 8px rgba(255, 215, 0, 0.5))
        drop-shadow(0 0 12px rgba(255, 215, 0, 0.3))
      `
        : 'none',
    }"
    :path="path[0]"
    :marker-end="markerEnd"
  />
</template>

<style scoped></style>
