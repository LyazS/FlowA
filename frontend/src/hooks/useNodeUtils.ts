import {
  type VFNodeData,
  VFNodeConnectionType,
  type VFNodeHandleData,
  VFNodeConnectionDataType,
} from '@/components/nodes/VFNodeInterface'
import { type SelectOption } from 'naive-ui'
import { useVueFlow } from '@vue-flow/core'
import type { VarItem4Selections } from '@/schemas/schemas'

interface NodeUtilsInstance {
  findVarFromIO: (
    nid: string,
    findconnect: VFNodeConnectionType,
    hid: string,
  ) => VarItem4Selections[]
  recursiveFindVariables: (
    nid: string,
    findSelf: string[],
    findAttach: string[],
    findNext: string[],
    findAllInput: boolean,
    findInput: string[],
    findAllOutput: boolean,
    findOutput: string[],
  ) => VarItem4Selections[]
  mapVarItemToSelect: (item: VarItem4Selections) => SelectOption
}
let instance: NodeUtilsInstance | null = null

export const useNodeUtils = () => {
  if (instance) return instance
  const { findNode, getHandleConnections } = useVueFlow()

  const findVarFromIO = (
    nid: string,
    findconnect: VFNodeConnectionType,
    hid: string,
  ): VarItem4Selections[] => {
    const result: VarItem4Selections[] = []
    const thenode = findNode(nid)

    if (!thenode || !thenode.data.connections[findconnect]?.[hid]) {
      return result
    }
    const thenodedata = thenode.data as VFNodeData
    const connection = thenodedata.connections[findconnect][hid].data

    for (const c_data of Object.values(connection) as Array<VFNodeHandleData>) {
      if (c_data.type === VFNodeConnectionDataType.FromInner && c_data.path) {
        const pathData = thenode.data[c_data.path[0]]?.byId?.[c_data.path[1]]
        if (pathData) {
          result.push({
            nodeId: nid,
            nlabel: thenode.data.label,
            dpath: c_data.path,
            dlabel: pathData.label,
            dkey: pathData.key,
            dtype: pathData.type,
          })
        }
      } else if (c_data.type === VFNodeConnectionDataType.FromOuter && c_data.inputKey) {
        const edges = getHandleConnections({
          id: c_data.inputKey,
          type: 'target',
          nodeId: nid,
        })

        for (const edge of Object.values(edges)) {
          result.push(
            ...recursiveFindVariables(edge.source, [], [], [], false, [], false, [
              edge.sourceHandle!,
            ]),
          )
        }
      } else if (
        c_data.type === VFNodeConnectionDataType.FromAttached &&
        c_data.atype &&
        thenode.data.nesting?.attached_nodes
      ) {
        const attachedNode = thenode.data.nesting.attached_nodes[c_data.atype]
        if (attachedNode) {
          result.push(
            ...recursiveFindVariables(
              attachedNode.nid,
              c_data.atype === 'attached_node_output' ? ['self'] : [],
              [],
              [],
              false,
              [],
              c_data.atype === 'attached_node_input',
              [],
            ),
          )
        }
      } else if (c_data.type === VFNodeConnectionDataType.FromParent && thenode.parentNode) {
        result.push(
          ...recursiveFindVariables(thenode.parentNode, [], ['attach'], [], true, [], false, []),
        )
      }
    }
    return result
  }

  const recursiveFindVariables = (
    nid: string,
    findSelf: string[] = [],
    findAttach: string[] = [],
    findNext: string[] = [],
    findAllInput: boolean = false,
    findInput: string[] = [],
    findAllOutput: boolean = false,
    findOutput: string[] = [],
  ): VarItem4Selections[] => {
    const result: VarItem4Selections[] = []
    const thenode = findNode(nid)
    if (!thenode) return result

    const thenodedata = thenode.data as VFNodeData
    let processedFindInput = [...findInput]
    let processedFindOutput = [...findOutput]

    if (findAllInput) {
      processedFindInput = Object.keys(thenodedata.connections.inputs)
    }
    if (findAllOutput) {
      processedFindOutput = Object.keys(thenodedata.connections.outputs)
    }

    ;[
      { type: VFNodeConnectionType.self, handles: findSelf },
      { type: VFNodeConnectionType.attach, handles: findAttach },
      { type: VFNodeConnectionType.next, handles: findNext },
      { type: VFNodeConnectionType.inputs, handles: processedFindInput },
      { type: VFNodeConnectionType.outputs, handles: processedFindOutput },
    ].forEach(({ type, handles }) => {
      handles.forEach((hid) => {
        result.push(...findVarFromIO(nid, type, hid))
      })
    })

    return result
  }

  const mapVarItemToSelect = (item: VarItem4Selections): SelectOption => {
    return {
      label: `${item.nlabel}/${item.dlabel}/${item.dkey}/${item.dtype}`,
      value: `${item.nodeId}/${item.dpath[0]}/${item.dpath[1]}`,
    }
  }

  instance = {
    findVarFromIO,
    recursiveFindVariables,
    mapVarItemToSelect,
  }
  return instance
}
