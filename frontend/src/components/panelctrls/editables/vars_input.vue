<template>
  <n-flex vertical>
    <n-flex class="flexctitem" justify="space-between">
      <editable_header type="success"> 输入变量 </editable_header>
      <n-button text type="success" @click="addVariable" :disabled="!isEditorMode">
        <template #icon>
          <n-icon>
            <Add />
          </n-icon>
        </template>
        新增变量
      </n-button>
    </n-flex>
    <cp_var_input
      v-for="(pvar, vindex) in vardatas"
      :key="vindex"
      v-model:itemKey="pvar.key"
      v-model:itemType="pvar.type"
      v-model:itemValue="pvar.value"
      :selfVarSelections="selfVarSelections"
      :itemIdx="vindex"
      @remove="rmVariable(vindex)"
    />
  </n-flex>
</template>

<script lang="ts" setup>
import { ref, computed, defineAsyncComponent, inject, type ComputedRef } from 'vue'
import { useMessage, NFlex, NButton, NIcon, type SelectOption } from 'naive-ui'
import { Add } from '@vicons/ionicons5'
import type { VariableItem } from '@/schemas/var_schemas'
import { isEditorMode } from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
const editable_header = defineAsyncComponent(() => import('./common/header.vue'))
const cp_var_input = defineAsyncComponent(() => import('./common/var_input.vue'))



const props = defineProps<{
  selfVarSelections: SelectOption[]
  pid: string
}>()
const { curSelectedNode } = useCurSelectedNode()
const vardatas = computed({
  get(): VariableItem[] {
    return curSelectedNode.value.data.payloads.byId[props.pid].data
  },
  set(value: VariableItem[]) {
    curSelectedNode.value.data.payloads.byId[props.pid].data = value
  },
})
const addVariable = (): void => {
  const newVar: VariableItem = { key: '', type: 'String', value: '' }
  vardatas.value.push(newVar)
}

const rmVariable = (index: number): void => {
  vardatas.value.splice(index, 1)
}
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
