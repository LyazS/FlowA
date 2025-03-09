<template>
    <n-flex vertical>
      <n-flex class="flexctitem" justify="space-between">
        <editable_header type="info">输出</editable_header>
        <n-button type="primary" text @click="handleAdd" :disabled="!isEditorMode">
          <template #icon>
            <n-icon>
              <Add />
            </n-icon>
          </template>
          添加输出
        </n-button>
      </n-flex>
      <n-flex
        v-for="rid in curSelectedNode.data.results.order"
        :key="rid"
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
              @update:value="(v) => updateResultKey(rid, v)"
              :disabled="!isEditorMode"
            />
            <cp_var_select
              :style="{ width: '50%' }"
              v-model:value="curSelectedNode.data.results.byId[rid].config!.ref"
              :options="selfVarSelections"
              size="small"
            />
          </n-flex>
        </n-flex>
        <n-button
          circle
          tertiary
          size="small"
          type="error"
          @click="handleRemove(rid)"
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
  import { type VFNodeContentData } from '@/components/nodes/VFNodeInterface'
  import {
    selectedNodeId,
    isEditorMode,
    isEditing,
    isShowCodeEditor,
    CodeEditorPath,
    CodeEditorLangType,
  } from '@/hooks/useVFlowAttribute'
  import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
  
  const cp_var_select = defineAsyncComponent(
    () => import('@/components/panelctrls/editables/common/var_select.vue'),
  )
  const props = defineProps<{
    selfVarSelections: SelectOption[]
  }>()
  
  const { curSelectedNode } = useCurSelectedNode()
  
  // 处理添加
  function handleAdd() {
    const newResult: VFNodeContentData = {
      label: '',
      type: 'String',
      key: '',
      data: "",
      config: { ref: '' },
    }
    curSelectedNode.value.data.addResultWithConnection(newResult, 'output')
  }
  function handleRemove(rid: string) {
    curSelectedNode.value.data.rmResultWithConnection(rid)
  }
  // 更新结果的 key
  function updateResultKey(rid: string, value: string) {
    if (curSelectedNode.value.data.results.byId[rid]) {
      curSelectedNode.value.data.results.byId[rid].key = value
      curSelectedNode.value.data.results.byId[rid].label = value
    }
  }
  </script>
  