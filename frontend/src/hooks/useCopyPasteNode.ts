import { ref } from 'vue'
import { useVueFlow, type GraphNode, type GraphEdge, type XYPosition } from '@vue-flow/core'
import { VFNode, createVFNodeFromData } from '@/components/nodes/VFNodeClass'
import { type NodeWithVFData } from '@/schemas/schemas'
import { useMessage } from 'naive-ui'
import { generateNodeId, regexMatchNodeId, concatNestedNodeId, setValueByPath } from '@/utils/tools'
import { useVFlowManager } from '@/hooks/useVFlowManager'
import { useVFlowSaver } from '@/services/useVFlowSaver'

interface CopyPasteInstance {
  copyNode: (node?: GraphNode) => void
  pasteNode: (parentNode: string | null, position: XYPosition) => void
}
interface CopyPasteData {
  nodes: Record<string, NodeWithVFData>
  edges: GraphEdge[]
}
let instance: CopyPasteInstance | null = null

export const useCopyPasteNode = (): CopyPasteInstance => {
  if (instance) return instance
  const message = useMessage()

  const {
    getSelectedNodes,
    getConnectedEdges,
    screenToFlowCoordinate,
    getHandleConnections,
    findNode,
    addNodes,
    addEdges,
  } = useVueFlow()
  const { buildNestedNodeGraph, recursiveUpdateNodeSize } = useVFlowManager()
  const { autoSaveWorkflow } = useVFlowSaver()

  let copiedDataJson: string = ''

  const copyNode = (node?: GraphNode) => {
    const copiedDatas: CopyPasteData = {
      nodes: {},
      edges: [],
    }
    if (node) {
      copiedDatas.nodes[node.id] = node
    } else {
      for (const node of getSelectedNodes.value) {
        copiedDatas.nodes[node.id] = node
      }
      const edges = getConnectedEdges(getSelectedNodes.value)
      for (const edge of edges) {
        const srcid = edge.source
        const tgtid = edge.target
        if (srcid in copiedDatas.nodes && tgtid in copiedDatas.nodes) {
          copiedDatas.edges.push(edge)
        }
      }
    }
    const copiedDataStore: CopyPasteData = JSON.parse(JSON.stringify(copiedDatas))
    for (const node of Object.values(copiedDataStore.nodes)) {
      const parentId = node.parentNode
      if (!(parentId && parentId in copiedDataStore.nodes)) {
        let curPNode = findNode(parentId)
        while (curPNode) {
          node.position.x += curPNode.position.x
          node.position.y += curPNode.position.y
          curPNode = findNode(curPNode.parentNode)
        }
      }
    }
    copiedDataJson = JSON.stringify(copiedDataStore)
    message.info(`已复制${Object.keys(copiedDatas.nodes).length}个节点`)
  }

  const pasteNode = (parentNode: string | null, clientPosition: XYPosition): void => {
    if (copiedDataJson === '') {
      return
    }
    // 先清除已经选中状态
    for (const node of getSelectedNodes.value) {
      node.selected = false
    }

    const pastedDatas = JSON.parse(copiedDataJson) as CopyPasteData
    for (const node of Object.values(pastedDatas.nodes)) {
      node.data = createVFNodeFromData(node.data)
    }

    // 获取节点层级
    const layoutNodes: { layout: number; node: GraphNode }[] = []
    for (const node of Object.values(pastedDatas.nodes)) {
      const { nested } = regexMatchNodeId(node.id)
      layoutNodes.push({ layout: nested.length, node })
    }
    layoutNodes.sort((a, b) => a.layout - b.layout)

    // 先计算节点偏移
    const pastedNodesCenter = { x: 0, y: 0 }
    let centerCount = 0
    for (const { layout, node } of layoutNodes) {
      const curPNodeId = node.parentNode
      if (!(curPNodeId && curPNodeId in pastedDatas.nodes)) {
        pastedNodesCenter.x += node.position.x
        pastedNodesCenter.y += node.position.y
        centerCount += 1
      }
    }
    pastedNodesCenter.x /= centerCount
    pastedNodesCenter.y /= centerCount
    const position = screenToFlowCoordinate(clientPosition)
    const offsetX = position.x - pastedNodesCenter.x
    const offsetY = position.y - pastedNodesCenter.y

    // 提取父节点的偏移
    const pNode = findNode(parentNode) as NodeWithVFData | null
    const pNodeOffset = { x: 0, y: 0 }
    let pNode_parent = pNode as NodeWithVFData | null
    while (pNode_parent) {
      pNodeOffset.x += pNode_parent.position.x
      pNodeOffset.y += pNode_parent.position.y
      pNode_parent = findNode(pNode_parent.parentNode) as NodeWithVFData | null
    }

    // 按照顺序修正节点id
    const nodeMapOld2New = new Map<string, string>()

    const pastedNodes: GraphNode[] = []
    for (const { layout, node } of layoutNodes) {
      // 如果父节点在copy数据里，则说明是子节点
      // 否则，就是根节点
      const curPNodeId = node.parentNode
      if (curPNodeId && curPNodeId in pastedDatas.nodes) {
        // 如果父节点是嵌套节点，则需要拼接父节点id
        const curPNode = pastedDatas.nodes[curPNodeId]
        const curPNode_newid = nodeMapOld2New.get(curPNodeId)
        if (curPNode.data.isNestedNode() && curPNode_newid) {
          const { id: pid, nested: pNested } = regexMatchNodeId(curPNode_newid)
          const newid = concatNestedNodeId(generateNodeId(), [
            ...pNested,
            curPNode.data.Nesting.Tag,
          ])
          nodeMapOld2New.set(node.id, newid)
        } else {
          throw new Error(`${curPNodeId}应该是嵌套节点或者${curPNode_newid}应该不为空`)
        }
      } else {
        // 如果父节点是null，说明是根节点，可以去掉嵌套
        nodeMapOld2New.set(node.id, generateNodeId())
        if (pNode) {
          node.parentNode = pNode.id
        } else {
          node.parentNode = undefined
        }
        node.position.x += offsetX - pNodeOffset.x
        node.position.y += offsetY - pNodeOffset.y
      }

      pastedNodes.push(node)
    }
    // 转换为json统一替换id
    let pastedDatasJSON = JSON.stringify({ nodes: pastedNodes, edges: pastedDatas.edges })
    for (const [oldId, newId] of nodeMapOld2New.entries()) {
      const regex = new RegExp(oldId, 'g')
      pastedDatasJSON = pastedDatasJSON.replace(regex, newId)
    }
    const pastedDatasParsed = JSON.parse(pastedDatasJSON) as CopyPasteData
    for (const node of Object.values(pastedDatasParsed.nodes)) {
      node.data = createVFNodeFromData(node.data)
    }
    // 最终添加
    addNodes(Object.values(pastedDatasParsed.nodes))
    buildNestedNodeGraph()
    for (const node of Object.values(pastedDatasParsed.nodes)) {
      if (node.parentNode) {
        recursiveUpdateNodeSize(node.parentNode)
      } else {
        recursiveUpdateNodeSize(node.id)
      }
    }
    addEdges(pastedDatasParsed.edges)

    autoSaveWorkflow()

    message.success(`已粘贴${Object.keys(pastedDatasParsed.nodes).length}个节点`)
  }

  instance = {
    copyNode,
    pasteNode,
  }

  return instance
}
