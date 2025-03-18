import { ref, type Ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import {
  useVueFlow,
  type GraphNode,
  type XYPosition,
  type Connection,
  type GraphEdge,
  type FlowExportObject,
} from '@vue-flow/core'
import { useVFlowInitial } from '@/hooks/useVFlowInitial'
import { useVFlowSaver } from '@/services/useVFlowSaver'
import { getUuid, setValueByPath } from '@/utils/tools'
import {
  VFNodeFlag,
  type NestedVFNodeData,
  type AttachedVFNodeData,
  VFNodeAttachingPosType,
} from '@/components/nodes/VFNodeInterface'
import type { NodeWithVFData } from '@/schemas/schemas'
import { type VFNode, createVFNodeFromData } from '@/components/nodes/VFNodeClass'
import Logger from '@/utils/Logger'

export interface NodeAddInfo {
  type: 'client' | 'attached'
  ntype: string
  nid: string | null
  parentNodeId: string | null | undefined
  pos: XYPosition
}

interface NestedNodeType {
  parentNode: string | null
  children: string[]
}

interface NodeManagementInstance {
  AllNodeCounters: Ref<Record<string, number>>
  NestedNodeGraph: Ref<Record<string, NestedNodeType>>
  initNodeManagement: () => void
  getNestedNodeById: (nid: string) => NestedNodeType
  buildNestedNodeGraph: () => void
  recursiveUpdateNodeSize: (nodeId: string | null | undefined) => void
  addNodeToVFlow: (info: NodeAddInfo) => void
  removeNodeFromVFlow: (node: GraphNode) => void
  resetNodeState: (node: GraphNode) => void
  addEdgeToVFlow: (params: GraphEdge) => void
  removeEdgeFromVFlow: (edges: GraphEdge[]) => void
  loadVflow: (data: FlowExportObject) => void
}
let instance: NodeManagementInstance | null = null

export const useVFlowManager = (): NodeManagementInstance => {
  if (instance) return instance

  const logger = new Logger('Manager')

  const { getNodes, findNode, addNodes, removeNodes, addEdges, removeEdges, fromObject } =
    useVueFlow()
  const { AllTestNodes, createVFNode } = useVFlowInitial()
  const { autoSaveWorkflow } = useVFlowSaver()

  const AllNodeCounters = ref<Record<string, number>>({})
  const NestedNodeGraph = ref<Record<string, NestedNodeType>>({})

  const initNodeManagement = () => {
    for (const ntype in AllTestNodes.value) {
      AllNodeCounters.value[ntype] = 0
    }
  }

  const resetCounter = () => {
    for (const ntype of Object.keys(AllNodeCounters.value)) {
      AllNodeCounters.value[ntype] = 0
    }
    for (const node of getNodes.value) {
      if (node.data.ntype in AllNodeCounters.value) {
        AllNodeCounters.value[node.data.ntype] += 1
      }
    }
  }

  const getNestedNodeById = (nid: string): NestedNodeType => {
    return NestedNodeGraph.value[nid]
  }
  const buildNestedNodeGraph = (): void => {
    NestedNodeGraph.value = {}
    for (const node of getNodes.value) {
      NestedNodeGraph.value[node.id] = { parentNode: node.parentNode || null, children: [] }
    }
    for (const [nid, node] of Object.entries(NestedNodeGraph.value)) {
      if (node.parentNode) {
        NestedNodeGraph.value[node.parentNode].children.push(nid)
      }
    }
    // logger.debug('getNodes', getNodes.value)
    // logger.debug('buildNestedNodeGraph', NestedNodeGraph.value)
  }

  const recursiveUpdateNodeSize = (nodeId: string | null | undefined) => {
    if (!nodeId) return
    let vf_node = findNode(nodeId)
    let nested_node = getNestedNodeById(nodeId)
    if (!vf_node || !nested_node) return
    const childnums = nested_node.children.reduce((acc, childId) => {
      const vf_node_child = findNode(childId) as NodeWithVFData
      // 子节点不计算
      if (!vf_node_child) return acc
      if (!(VFNodeFlag.IsAttached & vf_node_child.data.Flag)) acc += 1
      return acc
    }, 0)
    if (childnums <= 0) return

    const vf_node_pos = vf_node.position
    const vf_node_data = vf_node.data as NestedVFNodeData
    // 遍历子节点，计算最小包围盒
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity
    for (const childId of nested_node.children) {
      const vf_node_child = findNode(childId) as NodeWithVFData
      if (!vf_node_child) continue
      // 固定位置的子节点不计算
      if (VFNodeFlag.IsAttached & vf_node_child.data.Flag) continue
      minX = Math.min(minX, vf_node_child.position.x + vf_node_pos.x)
      minY = Math.min(minY, vf_node_child.position.y + vf_node_pos.y)
      maxX = Math.max(
        maxX,
        vf_node_child.position.x + vf_node_pos.x + vf_node_child.data.Size.Width,
      )
      maxY = Math.max(
        maxY,
        vf_node_child.position.y + vf_node_pos.y + vf_node_child.data.Size.Height,
      )
    }

    // 按照最小尺寸更新父节点尺寸
    let vf_node_tgt_wd =
      maxX - minX + vf_node_data.Nesting.Pad.Left + vf_node_data.Nesting.Pad.Right
    let vf_node_tgt_ht =
      maxY - minY + vf_node_data.Nesting.Pad.Top + vf_node_data.Nesting.Pad.Bottom
    vf_node_data.Size.Width = Math.max(vf_node_tgt_wd, vf_node_data.MinSize.Width)
    vf_node_data.Size.Height = Math.max(vf_node_tgt_ht, vf_node_data.MinSize.Height)

    vf_node.style = {
      ...(vf_node.style || {}), // 处理 undefined 情况
      width: `${vf_node_data.Size.Width}px`,
      height: `${vf_node_data.Size.Height}px`,
    }

    // 更新子节点位置
    for (const childId of nested_node.children) {
      const vf_node_child = findNode(childId)
      if (!vf_node_child) continue
      const cdata = vf_node_child.data as VFNode
      // 固定位置的子节点
      if (cdata.isAttachedNode()) {
        if (cdata.Attaching.Pos.YType == VFNodeAttachingPosType.Bottom) {
          const yOffset = cdata.Attaching.Pos.YOffset * vf_node_data.Nesting.APad.Gap
          vf_node_child.position.y =
            vf_node_data.Size.Height - vf_node_data.Nesting.APad.Bottom - yOffset
        } else if (cdata.Attaching.Pos.YType == VFNodeAttachingPosType.Center) {
          vf_node_child.position.y = vf_node_data.Size.Height / 2 - vf_node_data.Nesting.APad.Bottom
        }
        if (cdata.Attaching.Pos.XType == VFNodeAttachingPosType.Right) {
          vf_node_child.position.x = vf_node_data.Size.Width - vf_node_data.Nesting.APad.Right
        } else if (cdata.Attaching.Pos.XType == VFNodeAttachingPosType.Center) {
          vf_node_child.position.x = vf_node_data.Size.Width / 2 - vf_node_data.Nesting.APad.Right
        }
        if (cdata.Attaching.Pos.YType != VFNodeAttachingPosType.Top)
          vf_node_child.position.y -= cdata.Size.Height / 2
        if (cdata.Attaching.Pos.XType != VFNodeAttachingPosType.Left)
          vf_node_child.position.x -= cdata.Size.Width / 2
      } else {
        vf_node_child.position.x += vf_node_pos.x - (minX - vf_node_data.Nesting.Pad.Left)
        vf_node_child.position.y += vf_node_pos.y - (minY - vf_node_data.Nesting.Pad.Top)
      }
    }

    // 更新父节点位置
    vf_node.position = {
      x: minX - vf_node_data.Nesting.Pad.Left,
      y: minY - vf_node_data.Nesting.Pad.Top,
    }

    // 递归更新父节点大小
    recursiveUpdateNodeSize(nested_node.parentNode)
  }

  const recursiveAddNodeToVFlow = (nodeinfo: NodeAddInfo) => {
    logger.debug('nodeinfo:', nodeinfo)
    const nodetype = nodeinfo.ntype
    const parentNode = findNode(nodeinfo.parentNodeId)

    const initnode = createVFNode(nodetype)
    const offset_size = {
      Width: initnode.Size.Width + 8,
      Height: initnode.Size.Height + 8,
    }
    let new_node_id = nodeinfo.nid || getUuid()
    if (parentNode) {
      const pdata = parentNode.data as VFNode
      if (pdata.isNestedNode()) {
        const nest_regex = /#(\w+)/g
        const pid_matches = parentNode.id.match(nest_regex) || []
        logger.debug('parentNode id matches', pid_matches)
        new_node_id += pid_matches.join('')
        if (pdata.Nesting.Tag) {
          new_node_id += `#${pdata.Nesting.Tag}`
        }
      }
    }

    initnode.Size.Width = offset_size.Width
    initnode.Size.Height = offset_size.Height
    const nodecount = AllNodeCounters.value[nodetype]
    const new_node_label = nodecount > 0 ? `${initnode.Label}${nodecount}` : initnode.Label
    AllNodeCounters.value[nodetype] += 1
    initnode.PlaceholderLabel = new_node_label
    initnode.Label = new_node_label

    const new_node = {
      id: new_node_id,
      type: initnode.VType,
      data: initnode,
      style: {
        width: `${offset_size.Width}px`,
        height: `${offset_size.Height}px`,
      },
      draggable: undefined as boolean | undefined,
      selectable: undefined as boolean | undefined,
      parentNode: undefined as string | undefined,
      position: { x: 0, y: 0 },
    }

    // 设置全局position
    if (nodeinfo.type === 'attached' && !!parentNode) {
      const pdata = parentNode.data as VFNode & NestedVFNodeData
      if (initnode.Attaching!.Pos.YType == VFNodeAttachingPosType.Top) {
        const yOffset = initnode.Attaching!.Pos.YOffset * pdata.Nesting.APad.Gap
        new_node.position.y = parentNode.position.y + pdata.Nesting.APad.Top + yOffset
      } else if (initnode.Attaching!.Pos.YType == VFNodeAttachingPosType.Bottom) {
        const yOffset = initnode.Attaching!.Pos.YOffset * pdata.Nesting.APad.Gap
        new_node.position.y =
          parentNode.position.y + pdata.Size.Height - pdata.Nesting.APad.Bottom - yOffset
      } else if (initnode.Attaching!.Pos.YType == VFNodeAttachingPosType.Center) {
        new_node.position.y =
          parentNode.position.y + pdata.Size.Height / 2 - pdata.Nesting.APad.Bottom
      }
      if (initnode.Attaching!.Pos.XType == VFNodeAttachingPosType.Left) {
        new_node.position.x = parentNode.position.x + pdata.Nesting.APad.Left
      } else if (initnode.Attaching!.Pos.XType == VFNodeAttachingPosType.Right) {
        new_node.position.x = parentNode.position.x + pdata.Size.Width - pdata.Nesting.APad.Right
      } else if (initnode.Attaching!.Pos.XType == VFNodeAttachingPosType.Center) {
        new_node.position.x =
          parentNode.position.x + pdata.Size.Width / 2 - pdata.Nesting.APad.Right
      }

      new_node.draggable = false
      new_node.selectable = false
      new_node.position.x -= offset_size.Width / 2
      new_node.position.y -= offset_size.Height / 2
      logger.debug('add attached node in', (initnode as VFNode & AttachedVFNodeData).Attaching.Pos)
    } else if (nodeinfo.type === 'client') {
      new_node.position.x = nodeinfo.pos.x
      new_node.position.y = nodeinfo.pos.y
    }
    // 递归设置局部position
    if (nodeinfo.parentNodeId) {
      new_node.parentNode = nodeinfo.parentNodeId
      let curparentnode: string | null = nodeinfo.parentNodeId
      while (curparentnode) {
        if (curparentnode) {
          new_node.position.x -= findNode(curparentnode)!.position.x
          new_node.position.y -= findNode(curparentnode)!.position.y
        }
        curparentnode = getNestedNodeById(curparentnode)?.parentNode
      }
    }

    addNodes(new_node)

    if (initnode.isNestedNode()) {
      logger.log(`add ${Object.keys(initnode.Nesting.ANodes).length} fixed nested nodes`)
      for (const [aname, anode] of Object.entries(initnode.Nesting.ANodes)) {
        const anid = recursiveAddNodeToVFlow({
          ntype: anode.NType,
          nid: null,
          type: 'attached',
          parentNodeId: new_node.id,
          pos: { x: 0, y: 0 },
        })
        initnode.Nesting.ANodes[aname].Nid = anid
      }
    }
    return new_node_id
  }

  const addNodeToVFlow = (nodeinfo: NodeAddInfo) => {
    recursiveAddNodeToVFlow(nodeinfo)
    buildNestedNodeGraph()
    recursiveUpdateNodeSize(nodeinfo.parentNodeId)
    autoSaveWorkflow()
  }

  const removeNodeFromVFlow = (node: GraphNode) => {
    removeNodes(node, true, true)
    autoSaveWorkflow()
  }

  const resetNodeState = (node: GraphNode) => {
    ;(node.data as VFNode).resetState()
  }

  const addEdgeToVFlow = (params: GraphEdge) => {
    if (!params.sourceHandle || !params.targetHandle) return
    let is_match_port =
      (params.sourceHandle.startsWith('output') && params.targetHandle.startsWith('input')) ||
      (params.sourceHandle.startsWith('callbackUser') &&
        params.targetHandle.startsWith('callbackFunc'))
    let is_diff_node = params.source !== params.target
    let is_same_parent =
      getNestedNodeById(params.source)?.parentNode === getNestedNodeById(params.target)?.parentNode
    let is_all_attached =
      (findNode(params.source)?.data as VFNode).isAttachedNode() &&
      (findNode(params.target)?.data as VFNode).isAttachedNode()
    logger.debug(
      'is_match_port',
      is_match_port,
      'is_diff_node',
      is_diff_node,
      'is_same_parent',
      is_same_parent,
      'is_all_attached',
      is_all_attached,
    )
    if (is_match_port && is_diff_node && !!is_same_parent && !is_all_attached) {
      logger.debug('add edge')
      params.type = 'normal'
      addEdges(params)
      autoSaveWorkflow()
    }
  }

  const removeEdgeFromVFlow = (edges: GraphEdge[]) => {
    removeEdges(edges)
    autoSaveWorkflow()
  }

  const loadVflow = async (flow: FlowExportObject) => {
    removeNodes(getNodes.value)
    await nextTick()
    if (flow) {
      for (const node of flow.nodes) {
        node.data = createVFNodeFromData(node.data)
        node.data.resetState()
      }
      fromObject(flow)
      buildNestedNodeGraph()
      resetCounter()
    }
  }

  instance = {
    AllNodeCounters,
    NestedNodeGraph,
    initNodeManagement,
    getNestedNodeById,
    buildNestedNodeGraph,
    recursiveUpdateNodeSize,
    addNodeToVFlow,
    removeNodeFromVFlow,
    resetNodeState,
    addEdgeToVFlow,
    removeEdgeFromVFlow,
    loadVflow,
  }
  return instance
}
