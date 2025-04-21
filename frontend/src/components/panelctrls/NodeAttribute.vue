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
import { useNodeUtils, type RefVarItem } from '@/hooks/useNodeUtils'
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
  CONNECT_NODE_LEVEL,
  CONNECT_HANDLE_LEVEL,
  CONNECT_VAR_LEVEL,
  TYPE_VFOR,
  TYPE_VSPAN,
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
  type FromInnerPath,
} from '@/components/nodes/VFNodeInterface'
import { object } from 'zod'

const { recursiveFindVariables, uniqueVarItems } = useNodeUtils()
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

const _CacheConnectionsByArgs: Record<string, any> = {}
const getConnectionsByArgs = (args: string[]) => {
  /*
  真正想要的是什么
  1. 句柄
  2. 变量
  其实不需要具体节点
  */
  /*
  节点层级（Node Level）
  句柄层级（Handle Level）
  变量层级（Variable Level）
  */
  /* args应该符合这个格式
  参考python的argparse方式
  ====================================================
  节点层级（Node Level）
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
  句柄层级（Handle Level）
  ====================================================
  --handle 非必填
      VFNodeConnectionType：表示上述节点的handels类型
      CONNECT_ALL_DATA：表示上述节点的所有handels类型
  ====================================================
  变量层级（Variable Level）
  ====================================================
  --hid 非必填
    CONNECT_ALL_DATA：表示上述节点的所有handels
    string 上述节点的handle的id
    不填，则只收集到handle层级
  ====================================================
  --level 必填，输出层级
    CONNECT_NODE_LEVEL
    CONNECT_HANDLE_LEVEL
    CONNECT_VAR_LEVEL
  ====================================================
  --notop 非必填，为true可用于在只有一个node的时候，去掉根节点
  ====================================================
  --outfmt 必填
    CONNECT_ALL_DATA：表示输出对应原始数据
      节点层级 [<node_id>]
      句柄层级 {<node_id>: {<handle_type>: [<handle_id>]}}
      变量层级 [<RefVarItem>]
    CONNECT_DATA_TO_SELECT: 数组形式
      节点层级 [<node_id>]
      句柄层级 [<node_id>, <handle_type>, <handle_id>][]
      变量层级 [<RefVarItem>]
  ====================================================
  */

  // 返回缓存
  const key = selectedNodeId.value + args.join('-')
  if (key in _CacheConnectionsByArgs) {
    return _CacheConnectionsByArgs[key]
  }
  // 解析参数
  const parsed_args: {
    level: string | undefined
    node: string | undefined
    child: string | undefined
    inhid: string | undefined
    handle: string | undefined
    hid: string | undefined
    outfmt: string | undefined
    notop: boolean | undefined
  } = {
    level: undefined,
    node: undefined,
    child: undefined,
    inhid: undefined,
    handle: undefined,
    hid: undefined,
    outfmt: undefined,
    notop: undefined,
  }
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]
    if (arg.startsWith('--')) {
      const key = arg.slice(2)
      if (!(key in parsed_args)) continue

      // 对于布尔标志，直接设置为true
      if (key === 'notop') {
        parsed_args[key] = true
        continue
      }

      // 检查是否有下一个参数作为值
      if (i + 1 >= args.length) continue
      const nextArg = args[i + 1]

      // 确保下一个参数不是另一个选项
      if (nextArg.startsWith('--')) continue
      ;(parsed_args as any)[key] = nextArg
      i++ // 跳过已处理的值
    }
  }
  if (!parsed_args.node || !parsed_args.level || !parsed_args.outfmt) {
    _CacheConnectionsByArgs[key] = null
    return _CacheConnectionsByArgs[key]
  }

  // ====================================================
  // 节点层级（Node Level）
  // ====================================================
  const nodeIds: string[] = []
  const nodeType = parsed_args.node

  if (nodeType === CONNECT_CUR_NODE) {
    // 当前节点
    nodeIds.push(nodeId.value)
  } else if (nodeType === CONNECT_PARENT_NODE) {
    // 父节点
    if (curSelectedNode.value.parentNode) {
      nodeIds.push(curSelectedNode.value.parentNode)
    }
  } else if (nodeType === CONNECT_CHILD_NODE) {
    // 子节点
    const childName = parsed_args.child
    if (!childName) {
      _CacheConnectionsByArgs[key] = null
      return _CacheConnectionsByArgs[key]
    }
    if (curSelectedNode.value.data.isNestedNode()) {
      if (childName === CONNECT_ALL_DATA) {
        // 所有子节点
        Object.values(curSelectedNode.value.data.Nesting.ANodes)
          .filter((anode) => anode.Nid)
          .forEach((anode) => nodeIds.push(anode.Nid!))
      } else {
        // 特定子节点
        const anode = curSelectedNode.value.data.Nesting.ANodes[childName]
        if (anode?.Nid) {
          nodeIds.push(anode.Nid)
        }
      }
    }
  } else if (nodeType === CONNECT_PRE_NODE) {
    // 前置节点
    const inHandle = parsed_args.inhid
    if (!inHandle) {
      _CacheConnectionsByArgs[key] = null
      return _CacheConnectionsByArgs[key]
    }
    const inHandles =
      inHandle === CONNECT_ALL_DATA
        ? [...curSelectedNode.value.data.Connections.Inputs.Order]
        : [inHandle]

    // 获取所有连接到这些输入handles的源节点
    inHandles.forEach((handle) => {
      const edges = getHandleConnections({
        id: handle,
        type: 'target',
        nodeId: nodeId.value,
      })
      Object.values(edges).forEach((edge) => nodeIds.push(edge.source))
    })
  } else {
    nodeIds.push(nodeType)
  }
  if (parsed_args.level === CONNECT_NODE_LEVEL) {
    if (parsed_args.outfmt === CONNECT_ALL_DATA || parsed_args.outfmt === CONNECT_DATA_TO_SELECT) {
      _CacheConnectionsByArgs[key] = nodeIds
      return _CacheConnectionsByArgs[key]
    } else {
      _CacheConnectionsByArgs[key] = null
      return _CacheConnectionsByArgs[key]
    }
  }
  // ====================================================
  // 句柄层级（Handle Level）
  let handleType = parsed_args.handle
  if (!handleType) handleType = CONNECT_ALL_DATA
  const handleTypes: VFNodeConnectionType[] = []
  const handleIds: [string, VFNodeConnectionType, string][] = []
  if (handleType === CONNECT_ALL_DATA) {
    //  遍历VFNodeConnectionType
    for (const key in VFNodeConnectionType) {
      handleTypes.push(VFNodeConnectionType[key as keyof typeof VFNodeConnectionType])
    }
  } else if (handleType in VFNodeConnectionType) {
    handleTypes.push(VFNodeConnectionType[handleType as keyof typeof VFNodeConnectionType])
  }
  for (const nid of nodeIds) {
    const node = findNode(nid) as NodeWithVFData
    if (!node) continue
    for (const ctype of handleTypes) {
      const connections = node.data.Connections[ctype].Order
      for (const hid of connections) {
        handleIds.push([nid, ctype, hid])
      }
    }
  }
  if (parsed_args.level === CONNECT_HANDLE_LEVEL) {
    if (parsed_args.outfmt === CONNECT_ALL_DATA) {
      const res: Record<string, Record<string, string[]>> = {}
      for (const [nid, ctype, hid] of handleIds) {
        if (!(nid in res)) {
          res[nid] = {}
        }
        if (!(ctype in res[nid])) {
          res[nid][ctype] = []
        }
        res[nid][ctype].push(hid)
      }
      if (parsed_args.notop && Object.keys(res).length === 1) {
        const res_handles = res[Object.keys(res)[0]]
        if (Object.keys(res_handles).length === 1) {
          _CacheConnectionsByArgs[key] = res_handles[Object.keys(res_handles)[0]]
          return _CacheConnectionsByArgs[key]
        }
        _CacheConnectionsByArgs[key] = res[Object.keys(res)[0]]
        return _CacheConnectionsByArgs[key]
      }
      _CacheConnectionsByArgs[key] = res
      return _CacheConnectionsByArgs[key]
    } else if (parsed_args.outfmt === CONNECT_DATA_TO_SELECT) {
      _CacheConnectionsByArgs[key] = handleIds
      return _CacheConnectionsByArgs[key]
    } else {
      _CacheConnectionsByArgs[key] = null
      return _CacheConnectionsByArgs[key]
    }
  }
  // ====================================================
  // 变量层级（Variable Level）
  // ====================================================
  let handleId = parsed_args.hid
  if (!handleId) handleId = CONNECT_ALL_DATA
  let varItems: RefVarItem[] = []
  for (const [nid, ctype, hid] of handleIds) {
    console.log(nid, ctype, hid)
    if (handleId === CONNECT_ALL_DATA) {
      varItems.push(...recursiveFindVariables(nid, ctype, [hid]))
    } else if (handleId === hid) {
      varItems.push(...recursiveFindVariables(nid, ctype, [hid]))
    }
  }
  varItems = uniqueVarItems(varItems)
  if (parsed_args.level === CONNECT_VAR_LEVEL) {
    if (parsed_args.outfmt === CONNECT_ALL_DATA || parsed_args.outfmt === CONNECT_DATA_TO_SELECT) {
      _CacheConnectionsByArgs[key] = varItems
      return _CacheConnectionsByArgs[key]
    } else {
      _CacheConnectionsByArgs[key] = null
      return _CacheConnectionsByArgs[key]
    }
  }
  return null
}
provide('getConnectionsByArgs', getConnectionsByArgs)

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
      Object.keys(_CacheConnectionsByArgs).forEach((key) => {
        delete _CacheConnectionsByArgs[key]
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
        [PAYLOADS_ID]: pid,
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
