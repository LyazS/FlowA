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
  VFNodeAttachingPos,
  VFNodeConnectionDataAttachedType,
  type NestedVFNodeData,
  type AttachedVFNodeData,
} from '@/components/nodes/VFNodeInterface'
import { type VFNode, createVFNodeFromData } from '@/components/nodes/VFNodeClass'

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
    // console.debug('getNodes', getNodes.value)
    // console.debug('buildNestedNodeGraph', NestedNodeGraph.value)
  }

  const recursiveUpdateNodeSize = (nodeId: string | null | undefined) => {
    if (!nodeId) return
    let vf_node = findNode(nodeId)
    let nested_node = getNestedNodeById(nodeId)
    if (!vf_node || !nested_node) return
    const childnums = nested_node.children.reduce((acc, childId) => {
      const vf_node_child = findNode(childId)
      // 子节点不计算
      if (!vf_node_child) return acc
      if (!(VFNodeFlag.isAttached & vf_node_child.data.flag)) acc += 1
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
      const vf_node_child = findNode(childId)
      if (!vf_node_child) continue
      // 固定位置的子节点不计算
      if (VFNodeFlag.isAttached & vf_node_child.data.flag) continue
      minX = Math.min(minX, vf_node_child.position.x + vf_node_pos.x)
      minY = Math.min(minY, vf_node_child.position.y + vf_node_pos.y)
      maxX = Math.max(
        maxX,
        vf_node_child.position.x + vf_node_pos.x + vf_node_child.data.size.width,
      )
      maxY = Math.max(
        maxY,
        vf_node_child.position.y + vf_node_pos.y + vf_node_child.data.size.height,
      )
    }

    // 按照最小尺寸更新父节点尺寸
    let vf_node_tgt_wd =
      maxX - minX + vf_node_data.nesting.pad.left + vf_node_data.nesting.pad.right
    let vf_node_tgt_ht =
      maxY - minY + vf_node_data.nesting.pad.top + vf_node_data.nesting.pad.bottom
    vf_node_data.size.width = Math.max(vf_node_tgt_wd, vf_node_data.min_size.width)
    vf_node_data.size.height = Math.max(vf_node_tgt_ht, vf_node_data.min_size.height)

    vf_node.style = {
      ...(vf_node.style || {}), // 处理 undefined 情况
      width: `${vf_node_data.size.width}px`,
      height: `${vf_node_data.size.height}px`,
    }

    // 更新子节点位置
    for (const childId of nested_node.children) {
      const vf_node_child = findNode(childId)
      if (!vf_node_child) continue
      const cdata = vf_node_child.data as VFNode
      // 固定位置的子节点
      if (cdata.isAttachedNode()) {
        const [yPart, yPos, xPart, xPos] = cdata.attaching.pos
        if (yPart == VFNodeAttachingPos.bottom) {
          const yOffset = yPos * vf_node_data.nesting.attached_pad.gap
          vf_node_child.position.y =
            vf_node_data.size.height - vf_node_data.nesting.attached_pad.bottom - yOffset
        } else if (yPart == VFNodeAttachingPos.center) {
          vf_node_child.position.y =
            vf_node_data.size.height / 2 - vf_node_data.nesting.attached_pad.bottom
        }
        if (xPart == VFNodeAttachingPos.right) {
          vf_node_child.position.x =
            vf_node_data.size.width - vf_node_data.nesting.attached_pad.right
        } else if (xPart == VFNodeAttachingPos.center) {
          vf_node_child.position.x =
            vf_node_data.size.width / 2 - vf_node_data.nesting.attached_pad.right
        }
        if (yPart != VFNodeAttachingPos.top) vf_node_child.position.y -= cdata.size.height / 2
        if (xPart != VFNodeAttachingPos.left) vf_node_child.position.x -= cdata.size.width / 2
      } else {
        vf_node_child.position.x += vf_node_pos.x - (minX - vf_node_data.nesting.pad.left)
        vf_node_child.position.y += vf_node_pos.y - (minY - vf_node_data.nesting.pad.top)
      }
    }

    // 更新父节点位置
    vf_node.position = {
      x: minX - vf_node_data.nesting.pad.left,
      y: minY - vf_node_data.nesting.pad.top,
    }

    // 递归更新父节点大小
    recursiveUpdateNodeSize(nested_node.parentNode)
  }

  const recursiveAddNodeToVFlow = (nodeinfo: NodeAddInfo) => {
    console.debug('nodeinfo:', nodeinfo)
    const nodetype = nodeinfo.ntype
    const parentNode = findNode(nodeinfo.parentNodeId)

    const initnode = createVFNode(nodetype)
    const offset_size = {
      width: initnode.size.width + 8,
      height: initnode.size.height + 8,
    }
    let new_node_id = nodeinfo.nid || getUuid()
    if (parentNode) {
      const pdata = parentNode.data as VFNode
      if (pdata.isNestedNode()) {
        const nest_regex = /#(\w+)/g
        const pid_matches = parentNode.id.match(nest_regex) || []
        console.debug('parentNode id matches', pid_matches)
        new_node_id += pid_matches.join('')
        if (pdata.nesting.tag) {
          new_node_id += `#${pdata.nesting.tag}`
        }
      }
    }

    initnode.size.width = offset_size.width
    initnode.size.height = offset_size.height
    const nodecount = AllNodeCounters.value[nodetype]
    const new_node_label = nodecount > 0 ? `${initnode.label}${nodecount}` : initnode.label
    AllNodeCounters.value[nodetype] += 1
    initnode.placeholderlabel = new_node_label
    initnode.label = new_node_label

    const new_node = {
      id: new_node_id,
      type: initnode.vtype,
      data: initnode,
      style: {
        width: `${offset_size.width}px`,
        height: `${offset_size.height}px`,
      },
      draggable: undefined as boolean | undefined,
      selectable: undefined as boolean | undefined,
      parentNode: undefined as string | undefined,
      position: { x: 0, y: 0 },
    }

    // 设置全局position
    if (nodeinfo.type === 'attached' && !!parentNode) {
      const pdata = parentNode.data as VFNode & NestedVFNodeData
      const [yPart, yPos, xPart, xPos] = initnode.attaching!.pos
      if (yPart == VFNodeAttachingPos.top) {
        const yOffset = yPos * pdata.nesting.attached_pad.gap
        new_node.position.y = parentNode.position.y + pdata.nesting.attached_pad.top + yOffset
      } else if (yPart == VFNodeAttachingPos.bottom) {
        const yOffset = yPos * pdata.nesting.attached_pad.gap
        new_node.position.y =
          parentNode.position.y + pdata.size.height - pdata.nesting.attached_pad.bottom - yOffset
      } else if (yPart == VFNodeAttachingPos.center) {
        new_node.position.y =
          parentNode.position.y + pdata.size.height / 2 - pdata.nesting.attached_pad.bottom
      }
      if (xPart == VFNodeAttachingPos.left) {
        new_node.position.x = parentNode.position.x + pdata.nesting.attached_pad.left
      } else if (xPart == VFNodeAttachingPos.right) {
        new_node.position.x =
          parentNode.position.x + pdata.size.width - pdata.nesting.attached_pad.right
      } else if (xPart == VFNodeAttachingPos.center) {
        new_node.position.x =
          parentNode.position.x + pdata.size.width / 2 - pdata.nesting.attached_pad.right
      }

      new_node.draggable = false
      new_node.selectable = false
      new_node.position.x -= offset_size.width / 2
      new_node.position.y -= offset_size.height / 2
      console.debug('add attached node in', (initnode as VFNode & AttachedVFNodeData).attaching.pos)
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
      console.log(`add ${Object.keys(initnode.nesting.attached_nodes).length} fixed nested nodes`)
      for (const antype of Object.keys(initnode.nesting.attached_nodes)) {
        const anid = recursiveAddNodeToVFlow({
          ntype: antype,
          nid: null,
          type: 'attached',
          parentNodeId: new_node.id,
          pos: { x: 0, y: 0 },
        })
        initnode.nesting.attached_nodes[antype as VFNodeConnectionDataAttachedType]!.nid = anid
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
    console.debug(
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
      console.debug('add edge')
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
