// hooks/useContextMenu.ts
import { ref, reactive, type Ref } from 'vue'
import { useVueFlow, type GraphNode, type GraphEdge } from '@vue-flow/core'
import { type NodeAddInfo, useVFlowManager } from './useVFlowManager'
import { useVFlowInitial } from './useVFlowInitial'
import { useVFlowRequest } from '@/services/useVFlowRequest'
import { VFNodeFlag } from '@/components/nodes/VFNodeInterface'
import { VFNode } from '@/components/nodes/VFNodeClass'
// 定义菜单项类型
interface MenuItem {
  label: string
  onClick?: () => void
  children?: MenuItem[]
}

// 定义菜单选项类型
interface MenuOptions {
  theme: string
  zIndex: number
  minWidth: number
  x: number
  y: number
  items: MenuItem[]
}

interface BaseContextMenuEvent {
  event: MouseEvent
}

export interface NodeContextMenuEvent extends BaseContextMenuEvent {
  type: 'node'
  node: GraphNode
  edge?: never // 明确排除其他类型
}

export interface EdgeContextMenuEvent extends BaseContextMenuEvent {
  type: 'edge'
  edge: GraphEdge
  node?: never
}

export interface PaneContextMenuEvent extends BaseContextMenuEvent {
  type: 'pane'
  node?: never
  edge?: never
}
// 最终的事件类型是这三个的联合类型
export type ContextMenuEvent = NodeContextMenuEvent | EdgeContextMenuEvent | PaneContextMenuEvent
// 定义上下文菜单实例类型
interface ContextMenuInstance {
  showMenu: Ref<boolean>
  menuOptions: MenuOptions
  initContextMenu: () => void
  showContextMenu: (event_cm: ContextMenuEvent) => void
}

// 单例模式
let instance: ContextMenuInstance | null = null

export const useContextMenu = (): ContextMenuInstance => {
  if (instance) return instance
  const { screenToFlowCoordinate, removeEdges } = useVueFlow()
  const { AllTestNodes } = useVFlowInitial()
  const {
    removeNodeFromVFlow,
    removeEdgeFromVFlow,
    buildNestedNodeGraph,
    recursiveUpdateNodeSize,
    addNodeToVFlow,
  } = useVFlowManager()

  const AddNodesInPane = ref<VFNode[]>([])
  const AddNodesInNest = ref<VFNode[]>([])
  const showMenu = ref(false)
  const menuOptions = reactive<MenuOptions>({
    theme: 'mac dark',
    zIndex: 3,
    minWidth: 50,
    x: 0,
    y: 0,
    items: [],
  })

  const initContextMenu = () => {
    AddNodesInPane.value = Object.entries(AllTestNodes.value)
      .sort((a, b) => a[0].localeCompare(b[0])) // 按key排序
      .map(([key, item]) => item)
      .filter((item) => !item.isAttachedNode())
    AddNodesInNest.value = Object.entries(AllTestNodes.value)
      .sort((a, b) => a[0].localeCompare(b[0])) // 按key排序
      .map(([key, item]) => item)
      .filter((item) => !item.isAttachedNode() && !(VFNodeFlag.isPassive & item.flag))
    // console.debug('AddNodesInPane', AddNodesInPane.value)
    // console.debug('AddNodesInNest', AddNodesInNest.value)
  }

  const onClickContextMenuRmNode = (event_cm: NodeContextMenuEvent) => {
    console.debug('删除节点')
    const node = event_cm.node
    const parent_id = node.parentNode

    removeNodeFromVFlow(node)
    buildNestedNodeGraph()
    recursiveUpdateNodeSize(parent_id)
  }

  const AddNodeList = (event_cm: ContextMenuEvent) => {
    let nodelist = AddNodesInPane.value
    if (event_cm.type == 'node') {
      if ((event_cm.node.data as VFNode).isNestedNode()) {
        nodelist = AddNodesInNest.value
      }
    }
    return nodelist.map((item) => ({
      label: item.label,
      onClick: () => {
        console.log('add node', item.ntype)
        const node_info: NodeAddInfo = {
          type: 'client',
          ntype: item.ntype,
          nid: null,
          parentNodeId: event_cm.node?.id,
          pos: {
            ...screenToFlowCoordinate({
              x: event_cm.event.clientX,
              y: event_cm.event.clientY,
            }),
          },
        }
        addNodeToVFlow(node_info)
      },
    }))
  }

  const onClickContextMenuRmEdge = (event_cm: EdgeContextMenuEvent) => {
    console.debug('删除边')
    removeEdgeFromVFlow([event_cm.edge])
  }

  const showContextMenu = (event_cm: ContextMenuEvent) => {
    menuOptions.x = event_cm.event.clientX
    menuOptions.y = event_cm.event.clientY
    showMenu.value =
      (event_cm.type === 'node' && !(event_cm.node.data as VFNode).isAttachedNode()) ||
      event_cm.type === 'pane' ||
      event_cm.type === 'edge'
    let show_add_node =
      (event_cm.type === 'node' && (event_cm.node.data as VFNode).isNestedNode()) ||
      event_cm.type === 'pane'
    let show_rm_node = event_cm.type === 'node' && !(event_cm.node.data as VFNode).isAttachedNode()
    let show_rm_edge = event_cm.type === 'edge'
    menuOptions.items = []

    if (show_add_node) {
      menuOptions.items.push({
        label: '添加节点',
        children: AddNodeList(event_cm),
      })
    }
    if (show_rm_node) {
      menuOptions.items.push({
        label: '删除节点',
        onClick: () => onClickContextMenuRmNode(event_cm as NodeContextMenuEvent),
      })
    }
    if (show_rm_edge) {
      menuOptions.items.push({
        label: '删除边',
        onClick: () => onClickContextMenuRmEdge(event_cm as EdgeContextMenuEvent),
      })
    }
  }

  instance = {
    showMenu,
    menuOptions,
    initContextMenu,
    showContextMenu,
  }

  return instance
}
