<template>
  <n-flex vertical>
    <n-flex class="flexctitem" justify="space-between">
      <editable_header type="warning"> Prompts设计 </editable_header>
      <n-button text type="warning" @click="addVariable" :disabled="!isEditorMode">
        <template #icon>
          <n-icon>
            <Add />
          </n-icon>
        </template>
        新增Prompt
      </n-button>
    </n-flex>
    <n-flex
      vertical
      v-for="(pvar, vindex) in curSelectedNode.data.payloads.byId[pid].data"
      :style="{ border: '1px solid #555', padding: '5px' }"
    >
      <n-flex
        :style="{ width: '100%', marginBottom: '2px' }"
        class="flexctitem"
        justify="space-between"
        :wrap="false"
      >
        <n-flex :style="{ width: '90%' }" class="flexctitem" justify="space-between" :wrap="false">
          <n-select
            :style="{ width: '130px' }"
            size="small"
            placeholder="类型"
            :options="roleSelections"
            :disabled="!isEditorMode"
            v-model:value="pvar.role"
          />
          <n-button
            text
            size="small"
            type="warning"
            @click="openEditor(vindex)"
            :disabled="!isEditorMode"
          >
            <template #icon>
              <n-icon>
                <CreateOutline />
              </n-icon>
            </template>
            放大编辑
          </n-button>
        </n-flex>
        <n-button
          circle
          tertiary
          size="small"
          type="error"
          @click="rmVariable(vindex)"
          :disabled="!isEditorMode"
        >
          <template #icon>
            <n-icon>
              <Close />
            </n-icon>
          </template>
        </n-button>
      </n-flex>
      <!-- TODO: minRows会报错Uncaught ResizeObserver loop completed with undelivered notifications. -->
      <n-input
        type="textarea"
        placeholder="请输入Prompt"
        clearable
        :disabled="!isEditorMode"
        :autosize="{
          minRows: 3,
          maxRows: 15,
        }"
        v-model:value="pvar.content"
        @blur="isEditing = false"
        @focus="isEditing = true"
      />
    </n-flex>
  </n-flex>
</template>

<script setup lang="ts">
import { ref, computed, inject, onMounted, type Ref } from 'vue'
import { NFlex, NIcon, NButton, NInput, NSelect, type SelectOption } from 'naive-ui'
import { Add, Close } from '@vicons/ionicons5'
import editable_header from './common/header.vue'
import { CreateOutline } from '@vicons/ionicons5'
import {
  isEditing,
  isEditorMode,
  isShowCodeEditor,
  CodeEditorPath,
  CodeEditorLangType,
} from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

interface PromptItem {
  role: string
  content: string
}

const props = defineProps<{
  pid: string
}>()

const { curSelectedNode } = useCurSelectedNode()

const roleSelections: SelectOption[] = [
  { label: '系统提示词', value: 'system' },
  { label: '用户提示词', value: 'user' },
  { label: 'AI回复', value: 'assistant' },
]

const addVariable = (): void => {
  const newVar: PromptItem = { role: 'user', content: '' }
  curSelectedNode.value.data.payloads.byId[props.pid].data.push(newVar)
}

const rmVariable = (index: number): void => {
  curSelectedNode.value.data.payloads.byId[props.pid].data.splice(index, 1)
}

const openEditor = (index: number): void => {
  CodeEditorPath.value = ['data', 'payloads', 'byId', props.pid, 'data', index, 'content']
  CodeEditorLangType.value = 'text'
  isShowCodeEditor.value = true
}
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
}
</style>
