<script setup lang="ts">
import {
  type Ref,
  type ComputedRef,
  computed,
  ref,
  provide,
  reactive,
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
import { useNodeUtils, type VarItem, type HandleVarItem4Selects } from '@/hooks/useNodeUtils'
import { useVFlowInitial } from '@/hooks/useVFlowInitial'
import { useVFlowSaver } from '@/services/useVFlowSaver'
import { selectedNodeId, isEditorMode } from '@/hooks/useVFlowAttribute'
import { useCurSelectedNode } from '@/hooks/useCurSelectedNode'
import { getData } from '@/utils/requestMethod'
import { type InputNode, type NodeWithVFData } from '@/schemas/schemas'
import { type BaseComponent } from '@/schemas/plugin_schemas'
import {
  PropVarType,
  THIS_NODE_DATA,
  CONTEXT_FUNCTION,
  VFOR_DATA,
  CONNECT_DATA_TO_SELECT,
  TYPE_VFOR,
  TYPE_VALUE,
  TYPE_VBIND,
  TYPE_VMODEL,
  TYPE_CONDITION_COMPARE,
  TYPE_CONDITION_LOGICAL,
  TYPE_CONDITION_DIRECT,
  TYPE_CONDITION_VBIND,
  TYPE_CONDITION_VALUE,
  PAYLOADS_ID,
} from '@/schemas/plugin_schemas'
import {
  type VFNodeData,
  VFNodeConnectionType,
  type VFNodeHandleData,
  type VFNodeHandle,
  VFNodeConnectionDataType,
} from '@/components/nodes/VFNodeInterface'
const { recursiveFindVariables, mapVarItemToSelect } = useNodeUtils()
const { autoSaveWorkflow } = useVFlowSaver()

const DynamicComponent = defineAsyncComponent(() => import('./editables/DynamicComponent.vue'))

const { findNode, getHandleConnections } = useVueFlow()

const nodeId = computed(() => selectedNodeId.value as string)
// 获取节点
const { curSelectedNode } = useCurSelectedNode()
const { AllUIComponents, AllNodeConfig } = useVFlowInitial()
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
    titleInputText.value = curSelectedNode.value.data.Label || ''
  },
  { immediate: true },
)

const startEditTilte = () => {
  if (!isEditorMode.value) return
  isEditingTitle.value = true
  nextTick(() => {
    titleInputRef.value?.focus()
  })
}

const saveTitle = () => {
  isEditingTitle.value = false
  const newLabel = titleInputText.value.trim()
  if (curSelectedNode.value) {
    curSelectedNode.value.data.Label = newLabel || curSelectedNode.value.data.PlaceholderLabel
  }
}

// 连接变量选择相关
const _VarSelection: Record<string, ComputedRef<VarItem[]>> = {}
const getOrCreateVarSelection = (path: string[]) => {
  const key = `${nodeId.value}-${path.join('/')}`
  if (!(key in _VarSelection)) {
    let ctype: VFNodeConnectionType
    if (path[0] === 'Self') ctype = VFNodeConnectionType.Self
    else if (path[0] === 'Attach') ctype = VFNodeConnectionType.Attach
    else if (path[0] === 'Input') ctype = VFNodeConnectionType.Inputs
    else if (path[0] === 'Output') ctype = VFNodeConnectionType.Outputs
    else return []

    if (path[1]) {
      _VarSelection[key] = computed(() => recursiveFindVariables(nodeId.value, ctype, [path[1]]))
    } else {
      _VarSelection[key] = computed(() => recursiveFindVariables(nodeId.value, ctype, null))
    }
  }

  return _VarSelection[key].value
}
provide('getOrCreateVarSelection', getOrCreateVarSelection)

const _VarSelectionWHandle: Record<string, ComputedRef<Record<string, HandleVarItem4Selects>>> = {}
const getOrCreateVarSelectionWHandle = (path: string[]) => {
  const key = `${nodeId.value}-${path.join('/')}`
  if (!(key in _VarSelectionWHandle)) {
    let ctype: VFNodeConnectionType
    let Connections: Record<string, VFNodeHandle>
    if (path[0] == VFNodeConnectionType.Self) {
      ctype = VFNodeConnectionType.Self
      Connections = curSelectedNode.value.data.Connections.Self
    } else if (path[0] == VFNodeConnectionType.Attach) {
      ctype = VFNodeConnectionType.Attach
      Connections = curSelectedNode.value.data.Connections.Attach
    } else if (path[0] == VFNodeConnectionType.Inputs) {
      ctype = VFNodeConnectionType.Inputs
      Connections = curSelectedNode.value.data.Connections.Inputs
    } else if (path[0] == VFNodeConnectionType.Outputs) {
      ctype = VFNodeConnectionType.Outputs
      Connections = curSelectedNode.value.data.Connections.Outputs
    } else return []

    if (path[1] && Connections.hasOwnProperty(path[1])) {
      _VarSelectionWHandle[key] = computed(() => {
        const selections: Record<string, HandleVarItem4Selects> = {
          [path[1]]: {
            Label: Connections[path[1]].Label,
            Data: recursiveFindVariables(nodeId.value, ctype, [path[1]]),
          },
        }
        return selections
      })
    } else {
      _VarSelectionWHandle[key] = computed(() => {
        const selections: Record<string, HandleVarItem4Selects> = {}
        for (const hid of Object.keys(Connections)) {
          selections[hid] = {
            Label: Connections[hid].Label,
            Data: recursiveFindVariables(nodeId.value, ctype, [hid]),
          }
        }
        return selections
      })
    }
  }

  return _VarSelectionWHandle[key].value
}
provide('getOrCreateVarSelectionWHandle', getOrCreateVarSelectionWHandle)

// 节点config相关
const getNodeConfig = (nid: string) => {
  const node = findNode(nid) as NodeWithVFData
  if (!node) return null
  return AllNodeConfig.value[node.data.NType]
}
provide('getNodeConfig', getNodeConfig)

// 监控并清理缓存
watch(
  () => selectedNodeId.value,
  (newVal, oldVal) => {
    if (newVal !== oldVal) {
      Object.keys(_VarSelection).forEach((key) => {
        delete _VarSelection[key]
      })
      Object.keys(_VarSelectionWHandle).forEach((key) => {
        delete _VarSelectionWHandle[key]
      })
    }
  },
)

// 渲染节点payload数据
const payloadComponents = computed<Record<string, VNode>>(() => {
  const components: Record<string, VNode> = {}
  if (!curSelectedNode.value) return components

  for (const pid of curSelectedNode.value.data.Payloads.Order) {
    const context = {
      [THIS_NODE_DATA]: curSelectedNode.value.data,
      [CONTEXT_FUNCTION]: {
        [PAYLOADS_ID]: () => [pid],
      },
    }
    const uitype = curSelectedNode.value.data.Payloads.ById[pid].UiType
    if (uitype && AllUIComponents.value.hasOwnProperty(uitype)) {
      components[pid] = h(DynamicComponent, {
        key: `${nodeId.value}-${pid}-payloads`,
        componentData: AllUIComponents.value[uitype],
        dataContext: context,
      })
    }
  }

  return components
})

// 渲染输出的连接
const outputsComponents = computed<VNode | null>(() => {
  if (!curSelectedNode.value) return null
  const context = {
    [THIS_NODE_DATA]: curSelectedNode.value.data,
    [CONTEXT_FUNCTION]: {},
  }
  const uitype = curSelectedNode.value.data.Config.OutputsUiType
  if (uitype && AllUIComponents.value.hasOwnProperty(uitype)) {
    return h(DynamicComponent, {
      key: `${nodeId.value}-outputs`,
      componentData: AllUIComponents.value[uitype],
      dataContext: context,
    })
  }
  return null
})

const nodedatatext = computed(() => {
  return curSelectedNode.value ? JSON.stringify(curSelectedNode.value.data, null, 2) : ''
})
const showErrors = computed(() => {
  return curSelectedNode.value ? curSelectedNode.value.data.State.Errors : []
})
onMounted(() => {})
onUnmounted(() => {})
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
          <n-text type="success" strong>{{ curSelectedNode?.data.Label }}</n-text>
          <n-icon size="17" depth="2">
            <CreateOutline />
          </n-icon>
        </n-h2>
        <n-input
          v-else
          v-model:value="titleInputText"
          :placeholder="curSelectedNode?.data.PlaceholderLabel"
          ref="titleInputRef"
          :bordered="false"
          @blur="saveTitle"
          class="title-input"
        />
      </template>
      <n-flex vertical :key="`${nodeId}-main`">
        <n-alert v-if="showErrors.length > 0" title="参数错误" type="error">
          <n-flex vertical>
            <template v-for="(error, index) in showErrors" :key="index">
              <n-text>{{ error }}</n-text>
            </template>
          </n-flex>
        </n-alert>
        <n-flex
          vertical
          v-if="Object.keys(payloadComponents).length > 0"
          :key="`${nodeId}-payloads`"
        >
          <template v-for="(comp, pid) in payloadComponents" :key="`${nodeId}-${pid}-payloads`">
            <component v-if="comp" :is="comp" />
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
