<template>
  <n-flex vertical>
    <editable_header type="info">输出</editable_header>
    <n-flex vertical v-for="(items, hid) in nodeOutputs" :key="hid">
      <n-flex v-for="item in items" class="flexctitem" :wrap="false" :key="item.dkey">
        <n-text v-if="hasMultipleHandles">
          {{ hid }}
        </n-text>
        <n-text>
          {{ item.dlabel }}
        </n-text>
        <n-tag :bordered="false" type="info">{{ item.dkey }}</n-tag>
        <n-text>{{ item.dtype }}</n-text>
      </n-flex>
    </n-flex>
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
import { NText, NFlex, NTag, type SelectOption } from 'naive-ui'
import { useVueFlow, type GraphNode } from '@vue-flow/core'
import { type VFNodeData } from '@/components/nodes/VFNodeInterface'
import editable_header from './common/header.vue'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

interface NodeOutput {
  dlabel: string
  dkey: string
  dtype: string
}

const props = defineProps<{
  outputVarSelections: Record<string, SelectOption[]>
}>()
const { findNode } = useVueFlow()
// Get node data
const { curSelectedNode } = useCurSelectedNode()
// Check if there are multiple outputs
const hasMultipleHandles = computed(() => {
  return Object.keys(curSelectedNode.value.data.connections.outputs).length > 1
})

// Transform output data
const nodeOutputs = computed<Record<string, NodeOutput[]>>(() => {
  const vars: Record<string, NodeOutput[]> = {}
  for (const [hid, items] of Object.entries(props.outputVarSelections)) {
    vars[hid] = []
    for (const item of items) {
      const [nid, dpath, did] = (item.value as string).split('/')
      const thenode = findNode(nid)
      if (!thenode || !thenode.data[dpath] || !thenode.data[dpath].byId) continue
      const data = thenode.data[dpath].byId[did]
      vars[hid].push({
        dlabel: data.label,
        dkey: data.key,
        dtype: data.type,
      })
    }
  }
  return vars
})
</script>
