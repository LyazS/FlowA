<template>
  <n-flex vertical>
    <editable_header type="success"> 重试设置 </editable_header>
    <n-flex class="flexctitem" :wrap="false">
      <n-tag :bordered="false" type="info">重试次数</n-tag>
      <n-slider v-model:value="num_retries" :min="0" :max="10" :step="1" />
      <n-input-number v-model:value="num_retries" size="tiny" :min="0" :max="10" :step="1" />
    </n-flex>
    <n-flex class="flexctitem" :wrap="false">
      <n-tag :bordered="false" type="info">重试机制</n-tag>
      <n-select
        v-model:value="retry_type"
        :options="retry_type_selection"
        size="tiny"
        :style="{ width: '8em' }"
        :consistent-menu-width="false"
      />
    </n-flex>
    <template v-if="retry_type !== 'Immediate'">
      <n-flex class="flexctitem" :wrap="false">
        <n-tag :bordered="false" type="info">重试时长（ms）</n-tag>
        <n-input-number
          v-model:value="retry_interval"
          size="tiny"
          :min="0"
          :step="1"
        />
      </n-flex>
      <template v-if="retry_type === 'Exponential'">
        <n-flex class="flexctitem" :wrap="false">
          <n-tag :bordered="false" type="info">幂等基数</n-tag>
          <n-input-number
            v-model:value="exponential_base"
            size="tiny"
            :min="0"
            :step="0.1"
            :precision="2"
          />
        </n-flex>
        <n-flex class="flexctitem" :wrap="false">
          <n-tag :bordered="false" type="info">幂等增长率</n-tag>
          <n-input-number
            v-model:value="exponential_growth"
            size="tiny"
            :min="0"
            :step="0.1"
            :precision="2"
          />
        </n-flex>
      </template>
    </template>
  </n-flex>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, inject, defineAsyncComponent, type Ref } from 'vue'
import {
  NSwitch,
  NFlex,
  NCollapse,
  NCollapseItem,
  NSelect,
  NSlider,
  NTag,
  NInputNumber,
  useMessage,
  type SelectOption,
} from 'naive-ui'
import editable_header from './common/header.vue'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

const props = defineProps<{
  pid: string
  selfVarSelections: SelectOption[]
}>()

const { curSelectedNode } = useCurSelectedNode()

const createComputedConfig = <T,>(prop: string) => {
  return computed<T>({
    get() {
      return curSelectedNode.value.data.payloads.byId[props.pid].data[prop]
    },
    set(value: T) {
      curSelectedNode.value.data.payloads.byId[props.pid].data[prop] = value
    },
  })
}
const retry_type_selection = [
  { label: '直接重试', value: 'Immediate' },
  { label: '固定重试', value: 'Fixed' },
  { label: '幂等重试', value: 'Exponential' },
]
const num_retries = createComputedConfig<number>('num_retries')
const retry_type = createComputedConfig<string>('type')
const retry_interval = createComputedConfig<number>('interval')
const exponential_base = createComputedConfig<number>('exponential_base')
const exponential_growth = createComputedConfig<number>('exponential_growth')
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
  flex-wrap: nowrap;
}
</style>
