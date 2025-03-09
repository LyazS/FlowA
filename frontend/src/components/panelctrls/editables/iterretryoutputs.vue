<template>
  <n-flex vertical>
    <editable_header type="info">输入输出</editable_header>
    <n-flex class="flexctitem" :wrap="false">
      <n-tag :bordered="false" type="info">输入节点</n-tag>
      <cp_var_select
        :style="{ width: '50%' }"
        v-model:value="input_node"
        :options="selfVarSelections"
        size="small"
      />
    </n-flex>
    <n-flex class="flexctitem" :wrap="false">
      <n-tag :bordered="false" type="info">输出节点</n-tag>
      <cp_var_select
        :style="{ width: '50%' }"
        v-model:value="output_node"
        :options="selfVarSelections_aoutput"
        size="small"
      />
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
import { computed, ref, inject, h, defineAsyncComponent } from 'vue'
import {
  NText,
  NIcon,
  NFlex,
  NTag,
  NInputGroup,
  NInput,
  NSelect,
  NButton,
  type SelectOption,
} from 'naive-ui'
import { useVueFlow } from '@vue-flow/core'
import { Add, Close } from '@vicons/ionicons5'
import editable_header from './common/header.vue'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
const cp_var_select = defineAsyncComponent(
  () => import('@/components/panelctrls/editables/common/var_select.vue'),
)
defineProps<{
  selfVarSelections: SelectOption[]
  selfVarSelections_aoutput: SelectOption[]
}>()
const createComputedConfig = <T,>(prop: string) => {
  return computed<T>({
    get() {
      return curSelectedNode.value.data.payloads.byId['D_RETRY_INOUT'].data[prop]
    },
    set(value: T) {
      curSelectedNode.value.data.payloads.byId['D_RETRY_INOUT'].data[prop] = value
    },
  })
}

const { curSelectedNode } = useCurSelectedNode()
const input_node = createComputedConfig<string>('input')
const output_node = createComputedConfig<string>('output')
</script>
