// import 'default-passive-events'
import { ref, reactive, watch, type Ref } from 'vue'
import {
  useVueFlow,
  type NodeMouseEvent,
  type EdgeMouseEvent,
  type Node,
  type GraphEdge,
  type Connection,
  type NodeDragEvent,
} from '@vue-flow/core'
import { useVFlowManager } from '@/hooks/useVFlowManager'
import {
  useContextMenu,
  type NodeContextMenuEvent,
  type EdgeContextMenuEvent,
  type PaneContextMenuEvent,
  type ContextMenuEvent,
} from '@/hooks/useContextMenu'
import { useVFlowSaver } from '@/services/useVFlowSaver'
import { selectedNodeId, isEditorMode } from '@/hooks/useVFlowAttribute'
import { type VFNode } from '@/components/nodes/VFNodeClass'

// 单例模式类型
type VFlowEventsInstance = {}

let instance: VFlowEventsInstance | null = null

export const useVFlowEvents = (): VFlowEventsInstance => {
  if (instance) return instance

  const {
    getNestedNodeById,
    buildNestedNodeGraph,
    recursiveUpdateNodeSize,
    addNodeToVFlow,
    removeNodeFromVFlow,
    addEdgeToVFlow,
  } = useVFlowManager()

  const { showContextMenu } = useContextMenu()
  const {
    findNode,
    onConnect,
    onNodeDrag,
    onNodeClick,
    onNodeContextMenu,
    onPaneContextMenu,
    onPaneClick,
    onEdgeContextMenu,
  } = useVueFlow()

  const { autoSaveWorkflow } = useVFlowSaver()

  // 节点选择事件
  const selcetNodeEvent = (event: NodeMouseEvent) => {
    const node = event.node
    const nodedata = node.data as VFNode
    if (nodedata.isAttachedNode()) return
    if (selectedNodeId.value === node.id) return

    // 选择新点
    if (selectedNodeId.value) {
      console.log(`Node ${selectedNodeId.value} deselected`)
    }
    console.log(`Node ${node.id} selected`)
    const foundnode = findNode(node.id)
    if (foundnode) {
      selectedNodeId.value = node.id
    } else {
      selectedNodeId.value = null
      console.debug('Node not found')
    }
  }
  const deselcetNodeEvent = () => {
    console.log(`Node ${selectedNodeId.value} deselected`)
    selectedNodeId.value = null
  }

  // vueflow事件监听
  onPaneClick((event: MouseEvent) => {
    deselcetNodeEvent()
  })

  onNodeClick((event: NodeMouseEvent) => {
    selcetNodeEvent(event)
  })

  onNodeDrag((event: NodeDragEvent) => {
    event.nodes.forEach((node) => {
      if (node.parentNode) {
        recursiveUpdateNodeSize(node.parentNode)
      }
    })
    autoSaveWorkflow()
  })

  onNodeContextMenu((event: NodeMouseEvent) => {
    console.log('右键节点')
    event.event.preventDefault()
    if (!isEditorMode.value) return
    const event_cm: ContextMenuEvent = {
      type: 'node',
      event: event.event as MouseEvent,
      node: event.node,
    }
    showContextMenu(event_cm)
  })

  onPaneContextMenu((event: MouseEvent) => {
    console.log('右键空白')
    event.preventDefault()
    if (!isEditorMode.value) return
    const event_cm: ContextMenuEvent = {
      type: 'pane',
      event: event,
    }
    showContextMenu(event_cm)
  })

  onEdgeContextMenu((event: EdgeMouseEvent) => {
    console.log('右键连线')
    event.event.preventDefault()
    if (!isEditorMode.value) return
    const event_cm: ContextMenuEvent = {
      type: 'edge',
      event: event.event as MouseEvent,
      edge: event.edge,
    }
    showContextMenu(event_cm)
  })

  onConnect((connection: Connection) => {
    addEdgeToVFlow(connection as GraphEdge)
  })

  instance = {}

  return instance
}
