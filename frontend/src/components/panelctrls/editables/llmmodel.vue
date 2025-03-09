<template>
  <n-flex vertical>
    <editable_header type="success">
      <n-collapse arrow-placement="right" :trigger-areas="['arrow']">
        <n-collapse-item title="模型设置">
          <n-flex vertical>
            <n-flex class="flexctitem" :wrap="false">
              <n-tag :bordered="false" type="info">模型选择</n-tag>
              <n-select
                v-model:value="modelConfig.cpType.value"
                :options="RefValTypeSelections"
                size="tiny"
                :style="{ width: '8em' }"
                :consistent-menu-width="false"
              />
              <template v-if="modelConfig.cpType.value === 'Ref'">
                <cp_var_select
                  v-model:value="modelConfig.cpValue.value"
                  :options="selfVarSelections"
                  size="tiny"
                />
              </template>
              <template v-else>
                <n-select
                  v-model:value="modelConfig.cpValue.value"
                  size="tiny"
                  :options="modelSelections"
                />
              </template>
            </n-flex>
            <n-flex class="flexctitem" :wrap="false">
              <n-tag :bordered="false" type="info">流式传输</n-tag>
              <n-switch v-model:value="streamConfig" />
            </n-flex>
            <n-flex v-for="config in configs" class="flexctitem" :wrap="false">
              <n-tag :bordered="false" type="info">{{ config.label }}</n-tag>
              <n-select
                v-model:value="config.cpType.value"
                :options="RefValTypeSelectionsWNull"
                size="tiny"
                :style="{ width: '8em' }"
                :consistent-menu-width="false"
              />
              <template v-if="config.cpType.value === 'Ref'">
                <cp_var_select
                  v-model:value="config.cpValue.value"
                  :options="selfVarSelections"
                  size="tiny"
                />
              </template>
              <template v-else-if="config.cpType.value === 'Value'">
                <n-slider
                  v-model:value="config.cpValue.value"
                  :min="config.min"
                  :max="config.max"
                  :step="config.step"
                />
                <n-input-number
                  v-model:value="config.cpValue.value"
                  size="tiny"
                  :min="config.min"
                  :max="config.max"
                  :step="config.step"
                />
              </template>
            </n-flex>
            <n-flex class="flexctitem" :wrap="false">
              <n-tag :bordered="false" type="info">{{ responseFormatConfig.label }}</n-tag>
              <n-select
                v-model:value="responseFormatConfig.cpType.value"
                :options="RefValTypeSelectionsWNull"
                size="tiny"
                :style="{ width: '8em' }"
                :consistent-menu-width="false"
              />
              <template v-if="responseFormatConfig.cpType.value === 'Value'">
                <n-select
                  v-model:value="responseFormatConfig.cpValue.value"
                  :options="response_format_selections"
                  size="tiny"
                />
              </template>
              <template v-else-if="responseFormatConfig.cpType.value === 'Ref'">
                <cp_var_select
                  v-model:value="responseFormatConfig.cpValue.value"
                  :options="selfVarSelections"
                  size="tiny"
                />
              </template>
            </n-flex>
          </n-flex>
        </n-collapse-item>
      </n-collapse>
    </editable_header>
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
import { getData } from '@/utils/requestMethod'
import { RefValTypeSelections, RefValTypeSelectionsWNull } from '@/schemas/select_schemas'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'

interface ConfigItem {
  label: string
  cpType: Ref<string>
  cpValue: Ref<any>
  min?: number
  max?: number
  step?: number
  options?: Ref<SelectOption[]>
}

const props = defineProps<{
  pid: string
  selfVarSelections: SelectOption[]
}>()
const message = useMessage()
const { curSelectedNode } = useCurSelectedNode()
const cp_var_select = defineAsyncComponent(
  () => import('@/components/panelctrls/editables/common/var_select.vue'),
)

const createComputedConfig = <T,>(prop: string) => {
  return computed<T>({
    get() {
      return curSelectedNode.value.data.payloads.byId[props.pid].data[prop].value
    },
    set(value: T) {
      curSelectedNode.value.data.payloads.byId[props.pid].data[prop].value = value
    },
  })
}

const createComputedType = (prop: string) => {
  return computed<string>({
    get() {
      return curSelectedNode.value.data.payloads.byId[props.pid].data[prop].type
    },
    set(value: string) {
      curSelectedNode.value.data.payloads.byId[props.pid].data[prop].type = value
    },
  })
}

const modelSelections = ref<SelectOption[]>([])
const response_format_selections: SelectOption[] = [{ label: 'json', value: 'json' }]

const streamConfig = computed<boolean>({
  get() {
    return curSelectedNode.value.data.payloads.byId[props.pid].data.stream
  },
  set(value: boolean) {
    curSelectedNode.value.data.payloads.byId[props.pid].data.stream = value
  },
})

const modelConfig: ConfigItem = {
  label: '模型选择',
  cpType: createComputedType('model'),
  cpValue: createComputedConfig<string>('model'),
  options: modelSelections,
}

const configs: ConfigItem[] = [
  {
    label: '最长回复',
    cpType: createComputedType('max_tokens'),
    cpValue: createComputedConfig<number>('max_tokens'),
    min: 256,
    max: 8192,
    step: 1,
  },
  {
    label: '温度',
    cpType: createComputedType('temperature'),
    cpValue: createComputedConfig<number>('temperature'),
    min: 0,
    max: 1,
    step: 0.1,
  },
  {
    label: 'Top P',
    cpType: createComputedType('top_p'),
    cpValue: createComputedConfig<number>('top_p'),
    min: 0,
    max: 1,
    step: 0.1,
  },
  {
    label: '频率惩罚',
    cpType: createComputedType('frequency_penalty'),
    cpValue: createComputedConfig<number>('frequency_penalty'),
    min: 0,
    max: 1,
    step: 0.1,
  },
]

const responseFormatConfig: ConfigItem = {
  label: '响应格式',
  cpType: createComputedType('response_format'),
  cpValue: createComputedConfig<string>('response_format'),
}

onMounted(async () => {
  try {
    const res = await getData(`workflow/nodeconfig?ntype=LLM_inference`)
    modelSelections.value = Object.values(res).map((item: any) => {
      return { label: item.name, value: item.name }
    })
  } catch (err) {
    message.error('获取模型列表失败')
    console.error(err)
  }
})
</script>

<style scoped>
.flexctitem {
  align-content: center;
  align-items: center;
  flex-wrap: nowrap;
}
</style>
