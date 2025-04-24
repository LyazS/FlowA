<script setup lang="ts">
import { computed } from 'vue'

interface ControlPoints {
  controlPoint1X: number
  controlPoint1Y: number
  controlPoint2X: number
  controlPoint2Y: number
}

const props = defineProps<{
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
}>()

const cp = computed(() =>
  getControlPoints(props.sourceX, props.sourceY, props.targetX, props.targetY),
)

const getControlPoints = (
  sourceX: number,
  sourceY: number,
  targetX: number,
  targetY: number,
): ControlPoints => {
  const deltaX = Math.abs(targetX - sourceX)
  const offsetX = deltaX * 0.5

  return {
    controlPoint1X: sourceX + offsetX,
    controlPoint1Y: sourceY,
    controlPoint2X: targetX - offsetX,
    controlPoint2Y: targetY,
  }
}
</script>

<template>
  <g>
    <path
      class="animated"
      fill="none"
      stroke="rgb(138, 203, 236)"
      :stroke-width="2"
      :d="`M${sourceX},${sourceY} C ${cp.controlPoint1X},${
        cp.controlPoint1Y
      } ${cp.controlPoint2X},${cp.controlPoint2Y} ${targetX},${targetY}`"
    />
    <circle
      :cx="targetX"
      :cy="targetY"
      fill="#000"
      :r="4"
      stroke="rgb(138, 203, 236)"
      :stroke-width="1.5"
    />
  </g>
</template>

<style scoped></style>
