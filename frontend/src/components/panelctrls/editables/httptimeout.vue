<template>
  <editable_header type="error" :level="6">
    <n-collapse arrow-placement="right" :trigger-areas="['arrow']">
      <n-collapse-item :title="thislabel">
        <n-flex vertical>
          <n-flex
            v-for="timeout in timeouts"
            class="flexctitem"
            justify="space-between"
            :style="{ width: '50%' }"
            :wrap="false"
          >
            <n-text>{{ timeout.label }}</n-text>
            <n-input-number
              v-model:value="timeout.cpValue.value"
              :style="{ flex: '1' }"
              size="small"
              :disabled="!isEditorMode"
              @blur="isEditing = false"
              @focus="isEditing = true"
              :precision="0"
            />
          </n-flex>
        </n-flex>
      </n-collapse-item>
    </n-collapse>
  </editable_header>
</template>

<script setup lang="ts">
import { type Ref, ref, computed, h, inject, defineAsyncComponent } from 'vue'
import { NFlex, NText, NCollapse, NCollapseItem, NInputNumber } from 'naive-ui'
import editable_header from './common/header.vue'
import { isEditorMode, isEditing } from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import { type Timeout } from '@/schemas/http_schemas'

const props = defineProps<{
  pid: string
}>()

const { curSelectedNode } = useCurSelectedNode()

const thislabel = computed(() => curSelectedNode.value?.data.payloads.byId[props.pid].label)

const createComputed = (prop: string) => {
  return computed({
    get() {
      return curSelectedNode.value?.data.payloads.byId[props.pid].data[prop]
    },
    set(value: number) {
      if (curSelectedNode.value) {
        curSelectedNode.value.data.payloads.byId[props.pid].data[prop] = value
      }
    },
  })
}

const timeouts: Timeout[] = [
  { label: '连接超时（秒）', cpValue: createComputed('connect') },
  { label: '读取超时（秒）', cpValue: createComputed('read') },
  { label: '写入超时（秒）', cpValue: createComputed('write') },
]
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
  flex-wrap: nowrap;
}
</style>
