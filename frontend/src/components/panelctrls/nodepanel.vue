<script setup lang="ts">
import {
  type Ref,
  computed,
  ref,
  watch,
  nextTick,
  inject,
  defineAsyncComponent,
  onUnmounted,
  onMounted,
  h,
  type VNode,
} from 'vue'
import {
  NFlex,
  NH2,
  NCard,
  NScrollbar,
  NInput,
  NIcon,
  NText,
  NDivider,
  NModal,
  NAlert,
  type SelectOption,
} from 'naive-ui'
import { Panel, useVueFlow } from '@vue-flow/core'
import { CreateOutline } from '@vicons/ionicons5'
import { useNodeUtils } from '@/hooks/useNodeUtils'
import { useVFlowSaver } from '@/services/useVFlowSaver'
import { selectedNodeId, isEditorMode, isEditing } from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import { type InputNode } from '@/schemas/schemas'

const { recursiveFindVariables, mapVarItemToSelect } = useNodeUtils()
const { autoSaveWorkflow } = useVFlowSaver()

const editable_tagoutputs = defineAsyncComponent(() => import('./editables/tagoutputs.vue'))
const editable_packoutputs = defineAsyncComponent(() => import('./editables/packoutputs.vue'))
const editable_retryoutputs = defineAsyncComponent(() => import('./editables/retryoutputs.vue'))
const editable_iterretryoutputs = defineAsyncComponent(
  () => import('./editables/iterretryoutputs.vue'),
)
const editable_retryconfig = defineAsyncComponent(() => import('./editables/retry_config.vue'))
const editable_condoutputs = defineAsyncComponent(() => import('./editables/condoutputs.vue'))
const editable_codeoutputs = defineAsyncComponent(() => import('./editables/codeoutputs.vue'))
const editable_iter_input = defineAsyncComponent(() => import('./editables/iter_input.vue'))
const editable_textinput = defineAsyncComponent(() => import('./editables/textinput.vue'))
const editable_texttag = defineAsyncComponent(() => import('./editables/texttag.vue'))
const editable_header = defineAsyncComponent(() => import('./editables/common/header.vue'))
const editable_codeeditor = defineAsyncComponent(() => import('./editables/codeeditor.vue'))
const editable_vars_input = defineAsyncComponent(() => import('./editables/vars_input.vue'))
const editable_llmprompts = defineAsyncComponent(() => import('./editables/llmprompts.vue'))
const editable_aggregatebranchs = defineAsyncComponent(
  () => import('./editables/aggregatebranchs.vue'),
)
const editable_llmmodel = defineAsyncComponent(() => import('./editables/llmmodel.vue'))
const editable_httprequests = defineAsyncComponent(() => import('./editables/httprequests.vue'))
const editable_httptimeout = defineAsyncComponent(() => import('./editables/httptimeout.vue'))

const { findNode, getHandleConnections } = useVueFlow()

const nodeId = computed(() => selectedNodeId.value as string)
// 获取节点
const { curSelectedNode } = useCurSelectedNode()

watch(
  () => curSelectedNode.value.data,
  () => {
    autoSaveWorkflow()
  },
  { deep: true },
)

// 节点标题相关
const isEditingTitle = ref(false)
const titleInputRef = ref<HTMLInputElement | null>(null)
const titleInputText = ref('')
watch(
  () => selectedNodeId.value,
  (newVal) => {
    titleInputText.value = curSelectedNode.value.data.label || ''
  },
  { immediate: true },
)

const startEditTilte = () => {
  if (!isEditorMode.value) return
  isEditingTitle.value = true
  isEditing!.value = true
  nextTick(() => {
    titleInputRef.value?.focus()
  })
}

const saveTitle = () => {
  isEditing!.value = false
  isEditingTitle.value = false
  const newLabel = titleInputText.value.trim()
  if (curSelectedNode.value) {
    curSelectedNode.value.data.label = newLabel || curSelectedNode.value.data.placeholderlabel
  }
}

// 输出变量字典{列表}
const outputVarSelections = computed(() => {
  const selections: Record<string, SelectOption[]> = {}
  if (!curSelectedNode.value) return selections
  for (const hid of Object.keys(curSelectedNode.value.data.connections.outputs)) {
    selections[hid] = recursiveFindVariables(nodeId.value, [], [], [], false, [], false, [hid]).map(
      (item) => mapVarItemToSelect(item),
    )
  }
  return selections
})

// 自身可用变量
const selfVarSelections = computed(() => {
  return recursiveFindVariables(nodeId.value, ['self'], [], [], false, [], false, []).map((item) =>
    mapVarItemToSelect(item),
  )
})

const selfVarSelections_aouput = computed(() => {
  return recursiveFindVariables(nodeId.value, ['attach_output'], [], [], false, [], false, []).map(
    (item) => mapVarItemToSelect(item),
  )
})

// 输入链接的节点
const inputNodes = computed<Record<string, InputNode[]>>(() => {
  const preNodes: Record<string, InputNode[]> = {}
  if (!curSelectedNode.value) return preNodes
  for (const hid of Object.keys(curSelectedNode.value.data.connections.inputs)) {
    const edges = getHandleConnections({ id: hid, type: 'target', nodeId: nodeId.value })
    preNodes[hid] = edges.map((edge) => ({
      srcid: edge.source,
      srcohid: edge.sourceHandle,
    })) as InputNode[]
  }
  return preNodes
})

// 渲染节点payload的内置变量
const payloadInnerComponents = computed<Record<string, VNode>>(() => {
  const components: Record<string, VNode> = {}
  if (!curSelectedNode.value) return components
  curSelectedNode.value.data.payloads.order.forEach((pid) => {
    const payload = curSelectedNode.value!.data.payloads.byId[pid]
    if (payload.uitype === 'texttag') {
      components[pid] = h(editable_texttag, { pid })
    }
  })
  return components
})

// 渲染节点payload数据
const payloadComponents = computed<Record<string, VNode>>(() => {
  const components: Record<string, VNode> = {}
  if (!curSelectedNode.value) return components
  curSelectedNode.value.data.payloads.order.forEach((pid) => {
    const payload = curSelectedNode.value!.data.payloads.byId[pid]
    let component: VNode | null = null
    switch (payload.uitype) {
      case 'textinput':
        component = h(editable_textinput, { pid })
        break
      case 'codeeditor':
        component = h(editable_codeeditor, { pid })
        break
      case 'vars_input':
        component = h(editable_vars_input, {
          pid,
          selfVarSelections: selfVarSelections.value,
        })
        break
      case 'llmprompts':
        component = h(editable_llmprompts, { pid })
        break
      case 'iter_input':
        component = h(editable_iter_input, {
          pid,
          selfVarSelections: selfVarSelections.value,
        })
        break
      case 'aggregatebranch':
        component = h(editable_aggregatebranchs, {
          pid,
          selfVarSelections: selfVarSelections.value,
          inputNodes: inputNodes.value,
        })
        break
      case 'llmmodel':
        component = h(editable_llmmodel, {
          pid,
          selfVarSelections: selfVarSelections.value,
        })
        break
      case 'httprequests':
        component = h(editable_httprequests, {
          pid,
          selfVarSelections: selfVarSelections.value,
        })
        break
      case 'httptimeout':
        component = h(editable_httptimeout, { nodeId: nodeId.value, pid })
        break
      case 'retry_config':
        component = h(editable_retryconfig, {
          pid,
          selfVarSelections: selfVarSelections.value,
        })
        break
      case 'iterretryoutputs':
        component = h(editable_iterretryoutputs, {
          selfVarSelections: selfVarSelections.value,
          selfVarSelections_aoutput: selfVarSelections_aouput.value,
        })
    }
    if (component) components[pid] = component
  })
  return components
})

// 渲染输出的连接
const outputsComponents = computed<VNode | null>(() => {
  if (!curSelectedNode.value) return null
  const uitype = curSelectedNode.value.data.config.outputsUIType
  switch (uitype) {
    case 'tagoutputs':
      return h(editable_tagoutputs, {
        outputVarSelections: outputVarSelections.value,
      })
    case 'packoutputs':
      return h(editable_packoutputs, {
        nodeId: nodeId.value,
        selfVarSelections: selfVarSelections_aouput.value,
      })
    case 'retryoutputs':
      return h(editable_retryoutputs, {
        selfVarSelections: selfVarSelections_aouput.value,
      })
    case 'condoutputs':
      return h(editable_condoutputs, {
        selfVarSelections: selfVarSelections.value,
      })
    case 'codeoutputs':
      return h(editable_codeoutputs, {})
    default:
      return null
  }
})

const nodedatatext = computed(() => {
  return curSelectedNode.value ? JSON.stringify(curSelectedNode.value.data, null, 2) : ''
})
const validation_errors = computed(() => {
  return curSelectedNode.value ? curSelectedNode.value.data.state.validation_errors : []
})
onMounted(() => {})
onUnmounted(() => {
  if (isEditing) isEditing.value = false
})
</script>

<template>
  <n-scrollbar style="max-height: calc(100vh - 80px); border-radius: 10px">
    <n-card header-style="height: 70px;" closable @close="selectedNodeId = null">
      <template #header>
        <n-h2
          prefix="bar"
          align-text
          v-if="!isEditingTitle"
          class="card-title"
          @click="startEditTilte"
        >
          <n-text type="success" strong>{{ curSelectedNode?.data.label }}</n-text>
          <n-icon size="17" depth="2">
            <CreateOutline />
          </n-icon>
        </n-h2>
        <n-input
          v-else
          v-model:value="titleInputText"
          :placeholder="curSelectedNode?.data.placeholderlabel"
          ref="titleInputRef"
          :bordered="false"
          @blur="saveTitle"
          class="title-input"
        />
      </template>
      <n-flex vertical :key="`${nodeId}-main`">
        <n-alert v-if="validation_errors.length > 0" title="参数错误" type="error">
          <n-flex vertical>
            <template v-for="(error, index) in validation_errors" :key="index">
              <n-text>{{ error }}</n-text>
            </template>
          </n-flex>
        </n-alert>
        <n-flex
          vertical
          v-if="Object.keys(payloadInnerComponents).length > 0"
          :style="{ 'padding-bottom': '10px' }"
          :key="`${nodeId}-inner`"
        >
          <editable_header type="default">内置变量</editable_header>
          <n-flex vertical>
            <template v-for="(comp, pid) in payloadInnerComponents" :key="`${nodeId}-${pid}-inner`">
              <component v-if="comp" :is="comp" />
            </template>
          </n-flex>
        </n-flex>
        <n-flex
          vertical
          v-if="Object.keys(payloadComponents).length > 0"
          :key="`${nodeId}-payloads`"
        >
          <template v-for="(comp, pid) in payloadComponents" :key="`${nodeId}-${pid}-payloads`">
            <component v-if="comp" :is="comp" :style="{ 'padding-bottom': '10px' }" />
          </template>
        </n-flex>
        <component v-if="outputsComponents" :is="outputsComponents" :key="`${nodeId}-outputs`" />
        <n-divider />
        <pre>{{ nodeId }}</pre>
        <!-- <pre>{{ inputNodes }}</pre> -->
        <pre>{{ nodedatatext }}</pre>
      </n-flex>
    </n-card>
  </n-scrollbar>
</template>

<style scoped>
.card-title {
  cursor: pointer;
  padding: 0;
  font-weight: 500;
}

.title-input {
  font-weight: 500;
}
</style>
