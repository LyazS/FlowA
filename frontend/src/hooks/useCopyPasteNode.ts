import { ref } from 'vue'
import { useVueFlow, type GraphNode, type GraphEdge, type XYPosition } from '@vue-flow/core'
import { getUuid } from '@/utils/tools'
import { VFNode, createVFNodeFromData } from '@/components/nodes/VFNodeClass'
import { type NodeWithVFData } from '@/schemas/schemas'

interface CopyPasteInstance {
  copyNode: () => void
  pasteNode: (parentNode: string | null, position: XYPosition) => number
}
interface CopyPasteData {
  nodes: Record<string, GraphNode>
  edges: GraphEdge[]
}
let instance: CopyPasteInstance | null = null

export const useCopyPasteNode = (): CopyPasteInstance => {
  if (instance) return instance

  const {
    getSelectedNodes,
    getConnectedEdges,
    screenToFlowCoordinate,
    getHandleConnections,
    findNode,
    addNodes,
  } = useVueFlow()

  let copiedDataJson: string = ''

  const copyNode = () => {
    const copiedDatas: CopyPasteData = {
      nodes: {},
      edges: [],
    }
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
    copiedDataJson = JSON.stringify(copiedDatas)
  }

  const pasteNode = (parentNode: string | null, clientPosition: XYPosition) => {
    if (copiedDataJson === '') {
      return 0
    }
    for (const node of getSelectedNodes.value) {
      node.selected = false
    }
    const copiedDatas: CopyPasteData = JSON.parse(copiedDataJson)
    const nodeidMap = new Map<string, string>()
    const pNode = findNode(parentNode) as NodeWithVFData
    for (const nodeid of Object.keys(copiedDatas.nodes)) {
      if (pNode && pNode.data.isNestedNode()) {
        nodeidMap.set(nodeid, getUuid() + `#${pNode.data.Nesting.Tag}`)
      } else {
        nodeidMap.set(nodeid, getUuid())
      }
    }
    // 全局替换nodeid
    let pastedDataJSON = copiedDataJson
    for (const [oldId, newId] of nodeidMap.entries()) {
      const regex = new RegExp(oldId, 'g')
      pastedDataJSON = pastedDataJSON.replace(regex, newId)
    }
    const pastedDatas = JSON.parse(pastedDataJSON) as CopyPasteData

    const pastedNodes: GraphNode[] = []
    const pastedNodesCenter = { x: 0, y: 0 }
    for (const node of Object.values(pastedDatas.nodes)) {
      pastedNodesCenter.x += node.position.x
      pastedNodesCenter.y += node.position.y
    }
    pastedNodesCenter.x /= Object.keys(pastedDatas.nodes).length
    pastedNodesCenter.y /= Object.keys(pastedDatas.nodes).length
    const position = screenToFlowCoordinate(clientPosition)
    const offsetX = position.x - pastedNodesCenter.x
    const offsetY = position.y - pastedNodesCenter.y
    for (const node of Object.values(pastedDatas.nodes)) {
      node.position.x += offsetX
      node.position.y += offsetY
      node.data = createVFNodeFromData(node.data)
      pastedNodes.push(node)
    }
    addNodes(pastedNodes)

    return pastedNodes.length
  }

  instance = {
    copyNode,
    pasteNode,
  }

  return instance
}
