<template>
  <level prefix="bar" :type="type" class="header">
    <slot></slot>
  </level>
</template>

<style scoped>
.header {
  margin-top: 0;
  margin-bottom: 0;
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import { NH1, NH2, NH3, NH4, NH5, NH6 } from 'naive-ui'
import type { HeaderType } from '@/schemas/schemas'

const props = withDefaults(
  defineProps<{
    type?: HeaderType
    level?: 1 | 2 | 3 | 4 | 5 | 6
  }>(),
  {
    type: 'default',
    level: 3,
  },
)

const levelMap: Record<
  number,
  typeof NH1 | typeof NH2 | typeof NH3 | typeof NH4 | typeof NH5 | typeof NH6
> = {
  1: NH1,
  2: NH2,
  3: NH3,
  4: NH4,
  5: NH5,
  6: NH6,
}

const level = computed(() => levelMap[props.level])
</script>
