<template>
  <!-- 横向的展示label以及对应的key，key放在ntag里 -->
  <n-flex class="flexctitem">
    <n-text :bordered="false">{{ nodeTextTag.label }}</n-text>
    <n-tag :bordered="false" type="info">{{ nodeTextTag.key }}</n-tag>
    <n-text :bordered="false">{{ nodeTextTag.type }}</n-text>
  </n-flex>
</template>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import { NText, NTag, NFlex } from 'naive-ui'
import { useVueFlow } from '@vue-flow/core'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

interface NodeTextTag {
  label: string
  key: string
  type: string
}

const props = defineProps<{
  pid: string
}>()

const { curSelectedNode } = useCurSelectedNode()
const nodeTextTag = computed<NodeTextTag>(() => {
  const tagdata = curSelectedNode.value?.data.payloads.byId[props.pid]
  return {
    label: tagdata?.label || '',
    key: tagdata?.key || '',
    type: tagdata?.type || '',
  }
})
</script>
