<template>
  <n-flex vertical>
    <n-flex class="flexctitem" justify="space-between">
      <editable_header type="info"> 输出变量 </editable_header>
      <n-button text type="info" @click="addVariable" :disabled="!isEditorMode">
        <template #icon>
          <n-icon>
            <Add />
          </n-icon>
        </template>
        新增变量
      </n-button>
    </n-flex>
    <n-flex
      v-for="rid in curSelectedNode.data.results.order"
      class="flexctitem"
      justify="space-between"
      :style="{ width: '100%' }"
      :wrap="false"
    >
      <n-flex vertical :style="{ width: '95%' }">
        <n-flex :wrap="false">
          <n-input
            :style="{ width: '50%' }"
            size="small"
            placeholder="变量名"
            :value="curSelectedNode.data.results.byId[rid].key"
            @blur="isEditing = false"
            @focus="isEditing = true"
            @update:value="(v: string) => updateVariable(rid, v)"
            :disabled="!isEditorMode"
          />
          <n-select
            :style="{ width: '50%' }"
            size="small"
            placeholder="变量类型"
            v-model:value="curSelectedNode.data.results.byId[rid].type"
            :options="CodeVarTypes"
            :disabled="!isEditorMode"
          />
        </n-flex>
      </n-flex>
      <n-button
        circle
        tertiary
        size="small"
        type="error"
        @click="rmVariable(rid)"
        :disabled="!isEditorMode"
      >
        <template #icon>
          <n-icon>
            <Close />
          </n-icon>
        </template>
      </n-button>
    </n-flex>
  </n-flex>
</template>

<script setup lang="ts">
import { ref, computed, inject } from 'vue'
import { NFlex, NIcon, NButton, NInput, NSelect } from 'naive-ui'
import { Add, Close } from '@vicons/ionicons5'
import editable_header from './common/header.vue'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import { isEditorMode, isEditing } from '@/hooks/useVFlowAttribute'
import { getUuid } from '@/utils/tools'
import { VariableTypesSelectionsWCode, FileVariableTypesSelections } from '@/schemas/select_schemas'
import type { VFNodeContentData } from '@/components/nodes/VFNodeInterface'

const { curSelectedNode } = useCurSelectedNode()

const CodeVarTypes = [...VariableTypesSelectionsWCode, ...FileVariableTypesSelections]

const addVariable = (): void => {
  const rid = getUuid()
  const cid = `c-${rid}`
  const newVariable: VFNodeContentData = {
    label: '',
    type: 'String',
    key: '',
    data: null,
  }
  curSelectedNode.value.data.addResultWithConnection(newVariable, 'output', rid, cid)
}

const updateVariable = (rid: string, key: string): void => {
  curSelectedNode.value.data.results.byId[rid].key = key
  curSelectedNode.value.data.results.byId[rid].label = key
}

const rmVariable = (rid: string): void => {
  curSelectedNode.value.data.rmResultWithConnection(rid)
}
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
