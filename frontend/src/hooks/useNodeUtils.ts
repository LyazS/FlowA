import {
  type VFNodeData,
  VFNodeConnectionType,
  type VFNodeHandleData,
  VFNodeConnectionDataType,
} from '@/components/nodes/VFNodeInterface'
import { type SelectOption } from 'naive-ui'
import { useVueFlow } from '@vue-flow/core'
import type { NodeWithVFData, VarItem4Selections } from '@/schemas/schemas'

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
  const resolveValueByPath = (path: (string | number)[], dataContext: any): any => {
    return path.reduce((acc, key) => acc?.[key], dataContext)
  }
  const findVarFromIO = (
    nid: string,
    findconnect: VFNodeConnectionType,
    hid: string,
  ): VarItem4Selections[] => {
    const result: VarItem4Selections[] = []
    const thenode = findNode(nid) as NodeWithVFData

    if (!thenode || !thenode.data.Connections[findconnect]?.[hid]) {
      return result
    }
    const thenodedata = thenode.data as VFNodeData
    const connection = thenodedata.Connections[findconnect][hid].Data

    for (const c_data of Object.values(connection) as Array<VFNodeHandleData>) {
      if (c_data.Type === VFNodeConnectionDataType.FromInner && c_data.Path) {
        const pathData = resolveValueByPath(c_data.Path, thenode.data)
        if (pathData) {
          result.push({
            nodeId: nid,
            nlabel: thenodedata.Label,
            dpath: c_data.Path,
            dlabel: pathData.Label,
            dkey: pathData.Key,
            dtype: pathData.Type,
          })
        }
      } else if (c_data.Type === VFNodeConnectionDataType.FromOuter && c_data.HandleId) {
        const edges = getHandleConnections({
          id: c_data.HandleId,
          type: 'target',
          nodeId: nid,
        })

        for (const edge of Object.values(edges)) {
          result.push(
            ...recursiveFindVariables(edge.source, [], [], false, [], false, [edge.sourceHandle!]),
          )
        }
      } else if (c_data.Type === VFNodeConnectionDataType.FromAttached && c_data.ANode) {
        for (const [aname, hdata] of Object.entries(c_data.ANode)) {
          const anode = findNode(thenode.data.Nesting?.ANodes?.[aname]?.Nid)
          if (anode) {
            const { ConnectionType, HandleId } = hdata
            result.push(
              ...recursiveFindVariables(
                anode.id,
                ConnectionType === VFNodeConnectionType.Self ? [HandleId] : [],
                ConnectionType === VFNodeConnectionType.Attach ? [HandleId] : [],
                false,
                ConnectionType === VFNodeConnectionType.Inputs ? [HandleId] : [],
                false,
                ConnectionType === VFNodeConnectionType.Outputs ? [HandleId] : [],
              ),
            )
          }
        }
      } else if (c_data.Type === VFNodeConnectionDataType.FromParent && thenode.parentNode) {
        result.push(
          ...recursiveFindVariables(
            thenode.parentNode,
            [],
            [c_data.HandleId!],
            false,
            [],
            false,
            [],
          ),
        )
      }
    }
    return result
  }

  const recursiveFindVariables = (
    nid: string,
    findSelf: string[] = [],
    findAttach: string[] = [],
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
      processedFindInput = Object.keys(thenodedata.Connections.Inputs)
    }
    if (findAllOutput) {
      processedFindOutput = Object.keys(thenodedata.Connections.Outputs)
    }

    ;[
      { type: VFNodeConnectionType.Self, handles: findSelf },
      { type: VFNodeConnectionType.Attach, handles: findAttach },
      { type: VFNodeConnectionType.Inputs, handles: processedFindInput },
      { type: VFNodeConnectionType.Outputs, handles: processedFindOutput },
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
