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
import { type InputNode, type NodeWithVFData } from '@/schemas/schemas'
import {
  PropVarType,
  THIS_NODE_DATA,
  CONTEXT_FUNCTION,
  VFOR_DATA,
  CONNECT_DATA_TO_SELECT,
  CONNECT_ALL_DATA,
  CONNECT_CUR_NODE,
  CONNECT_PARENT_NODE,
  CONNECT_CHILD_NODE,
  CONNECT_PRE_NODE,
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
import { object } from 'zod'
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

const getConnectionsByPath = (args: string[]) => {
  /*
  对于连接的使用需求：
  1. 节点
    1.1. 本节点
    1.2. 父节点
    1.3. 子节点
    1.4. 前导节点
  2. handle
    2.1. 节点的输入输出handle
  3. 变量（总是递归的）
    3.1. handle的递归变量
  4. 最终格式
    NODE{xxx}HANDLE{xxx}VAR{xxx}
  */
  /* args应该符合这个格式
  参考python的argparse方式
  ====================================================
  --node 必填
    CONNECT_CUR_NODE
      该节点
    CONNECT_PARENT_NODE
      该节点的父节点
    CONNECT_CHILD_NODE
      --child 如果是CONNECT_CHILD_NODE则必填
        CONNECT_ALL_DATA：表示该节点的所有child节点
        string 该节点child节点名字
    CONNECT_PRE_NODE
      --inhid 如果是CONNECT_PRE_NODE必填
        CONNECT_ALL_DATA：表示该节点所有输入handels的id
        string：表示该节点输入handels的id
  ====================================================
  --handle 必填
    VFNodeConnectionType：表示上述节点的handels类型
    CONNECT_ALL_DATA：表示上述节点的所有handels类型
  --hid 非必填，
    CONNECT_ALL_DATA：表示上述节点的所有handels
    string 上述节点的handle的id
  ====================================================
  --var 非必填，如有则--hid必须要有
    存在则表示所有变量
    不存在则表示不需要变量
  ====================================================
  --outfmt 必填
    CONNECT_ALL_DATA：表示输出对应Dict
    string：NODE{xxx}HANDLE{xxx}VAR{xxx}
  ====================================================
  */
  let elementId = 0
  // 节点 ====================================================
  const nodeids: string[] = []
  if (args[elementId] === CONNECT_CUR_NODE) {
    nodeids.push(nodeId.value)
  } else if (args[elementId] === CONNECT_PARENT_NODE) {
    if (curSelectedNode.value.parentNode) nodeids.push(curSelectedNode.value.parentNode)
  } else if (args[elementId] === CONNECT_CHILD_NODE) {
    if (curSelectedNode.value.data.isNestedNode()) {
      const childName = args[elementId + 1]
      if (childName === CONNECT_ALL_DATA) {
        for (const anode of Object.values(curSelectedNode.value.data.Nesting.ANodes)) {
          if (anode.Nid) nodeids.push(anode.Nid)
        }
      } else {
        const anode = curSelectedNode.value.data.Nesting.ANodes[childName]
        if (anode && anode.Nid) {
          nodeids.push(anode.Nid)
        }
      }
    }
    elementId += 1
  } else if (args[elementId] === CONNECT_PRE_NODE) {
    const inHandle = args[elementId + 1]
    const inHandles: string[] = []
    if (inHandle === CONNECT_ALL_DATA) {
      inHandles.push(...curSelectedNode.value.data.Connections.Inputs.Order)
    } else {
      inHandles.push(inHandle)
    }
    for (const handle of inHandles) {
      const edges = getHandleConnections({
        id: handle,
        type: 'target',
        nodeId: nodeId.value,
      })
      for (const edge of Object.values(edges)) {
        nodeids.push(edge.source)
      }
    }
    elementId += 1
  }
  // handle ====================================================
  elementId += 1
  const handlesWnidWvars: [string, VFNodeConnectionType, string, VarItem[]][] = []
  const handleType = args[elementId]
  const handleId = args[elementId + 1]
  for (const nid of nodeids) {
    const node = findNode(nid) as NodeWithVFData
    if (!node) continue

    // 获取handle类型
    if (handleType === CONNECT_ALL_DATA) {
      // 所有handle类型
      for (const ctype of Object.values(VFNodeConnectionType)) {
        if (handleId === CONNECT_ALL_DATA) {
          // 所有handle
          for (const hid of node.data.Connections[ctype].Order) {
            handlesWnidWvars.push([nid, ctype as VFNodeConnectionType, hid, []])
          }
        } else {
          // 特定handle
          if (node.data.Connections[ctype].ById[handleId]) {
            handlesWnidWvars.push([nid, ctype as VFNodeConnectionType, handleId, []])
          }
        }
      }
    } else if (Object.values(VFNodeConnectionType).includes(handleType as VFNodeConnectionType)) {
      // 特定handle类型
      const ctype = handleType as VFNodeConnectionType
      if (handleId === CONNECT_ALL_DATA) {
        // 所有handle
        for (const hid of node.data.Connections[ctype].Order) {
          handlesWnidWvars.push([nid, ctype, hid, []])
        }
      } else {
        // 特定handle
        if (node.data.Connections[ctype].ById[handleId]) {
          handlesWnidWvars.push([nid, ctype, handleId, []])
        }
      }
    }
  }
  elementId += 1

  // var变量 ====================================================
  elementId += 1
  for (let i = 0; i < handlesWnidWvars.length; i++) {
    const [nid, ctype, hid, varArray] = handlesWnidWvars[i]
    const vars = recursiveFindVariables(nid, ctype, [hid])
    if (args[elementId] === CONNECT_ALL_DATA) {
      // 所有变量
      varArray.push(...vars)
    } else {
      // 特定变量
      // 将变量添加到对应handle的第四个元素数组中
      varArray.push(...vars)
    }
  }

  // 输出格式 ====================================================
  elementId += 1
  if (args[elementId] === CONNECT_ALL_DATA) {
    // 返回字典
    return {
      nodeids,
      handlesWnid: handlesWnidWvars,
    }
  } else {
    // 返回特定格式
    const format = args[elementId]
    // 这里可以根据格式进行处理
    // 从 handlesWnidWvars 中提取所有变量
    const allVars: VarItem[] = []
    for (const [_, __, ___, varArray] of handlesWnidWvars) {
      allVars.push(...varArray)
    }
    return allVars.map((item) => {
      return format
        .replace('NODE{xxx}', `NODE{${item.NodeId}}`)
        .replace('HANDLE{xxx}', `HANDLE{${item.DataPath.ContentId}}`)
        .replace('VAR{xxx}', `VAR{${item.DataLabel}}`)
    })
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
      Connections = curSelectedNode.value.data.Connections.Self.ById
    } else if (path[0] == VFNodeConnectionType.Attach) {
      ctype = VFNodeConnectionType.Attach
      Connections = curSelectedNode.value.data.Connections.Attach.ById
    } else if (path[0] == VFNodeConnectionType.Inputs) {
      ctype = VFNodeConnectionType.Inputs
      Connections = curSelectedNode.value.data.Connections.Inputs.ById
    } else if (path[0] == VFNodeConnectionType.Outputs) {
      ctype = VFNodeConnectionType.Outputs
      Connections = curSelectedNode.value.data.Connections.Outputs.ById
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
