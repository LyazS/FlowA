<template>
  <n-flex vertical>
    <n-flex>
      <editable_header>
        {{ curSelectedNode.data.payloads.byId[pid].label }}
      </editable_header>
      <cp_var_select v-model:value="selectValue" :options="selfVarSelections" />
    </n-flex>
  </n-flex>
</template>

<style scoped></style>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'
import { NFlex, type SelectOption } from 'naive-ui'
import editable_header from './common/header.vue'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

const props = defineProps<{
  pid: string
  selfVarSelections: SelectOption[]
}>()

const cp_var_select = defineAsyncComponent(
  () => import('@/components/panelctrls/editables/common/var_select.vue'),
)

const { curSelectedNode } = useCurSelectedNode()

const selectValue = computed({
  get(): string {
    return curSelectedNode.value.data.payloads.byId[props.pid].data
  },
  set(value: string) {
    curSelectedNode.value.data.payloads.byId[props.pid].data = value
  },
})
</script>
