import {
  type VFNodeData,
  VFNodeConnectionType,
  type VFNodeHandleData,
  VFNodeConnectionDataType,
  type VFNodeContentData,
  type FromInnerPath,
} from '@/components/nodes/VFNodeInterface'
import { type SelectOption } from 'naive-ui'
import { useVueFlow } from '@vue-flow/core'
import type { NodeWithVFData } from '@/schemas/schemas'

export interface VarItem {
  NodeId: string | number
  NodeLabel: string
  DataPath: FromInnerPath
  DataLabel: string
  DataType: string
}
export interface HandleVarItem4Selects {
  Label: string
  Data: VarItem[]
}
interface NodeUtilsInstance {
  findVarFromIO: (nid: string, findconnect: VFNodeConnectionType, hid: string) => VarItem[]
  recursiveFindVariables: (
    nid: string,
    handleType: VFNodeConnectionType,
    handles: string[] | null,
  ) => VarItem[]
  mapVarItemToSelect: (item: VarItem) => SelectOption
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
  ): VarItem[] => {
    const result: VarItem[] = []
    const thenode = findNode(nid) as NodeWithVFData

    if (!thenode || !thenode.data.Connections[findconnect]?.[hid]) {
      return result
    }
    const thenodedata = thenode.data as VFNodeData
    const connection = thenodedata.Connections[findconnect][hid].Data

    for (const c_data of Object.values(connection) as Array<VFNodeHandleData>) {
      if (c_data.Type === VFNodeConnectionDataType.FromInner && c_data.Path) {
        const pathData: VFNodeContentData =
          thenode.data[c_data.Path.ContentName].ById[c_data.Path.ContentId]
        if (pathData) {
          result.push({
            NodeId: nid,
            NodeLabel: thenodedata.Label,
            DataPath: c_data.Path,
            DataLabel: pathData.Label,
            DataType: pathData.Type,
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
            ...recursiveFindVariables(edge.source, VFNodeConnectionType.Outputs, [
              edge.sourceHandle!,
            ]),
          )
        }
      } else if (c_data.Type === VFNodeConnectionDataType.FromAttached && c_data.ANode) {
        for (const [aname, hdata] of Object.entries(c_data.ANode)) {
          const anode = findNode(thenode.data.Nesting?.ANodes?.[aname]?.Nid)
          if (anode) {
            const { ConnectionType, HandleId } = hdata
            result.push(...recursiveFindVariables(anode.id, ConnectionType, [HandleId]))
          }
        }
      } else if (c_data.Type === VFNodeConnectionDataType.FromParent && thenode.parentNode) {
        result.push(
          ...recursiveFindVariables(thenode.parentNode, VFNodeConnectionType.Attach, [
            c_data.HandleId!,
          ]),
        )
      }
    }
    return result
  }

  const recursiveFindVariables = (
    nid: string,
    handleType: VFNodeConnectionType,
    handles: string[] | null,
  ): VarItem[] => {
    const result: VarItem[] = []
    const thenode = findNode(nid)
    if (!thenode) return result

    const thenodedata = thenode.data as VFNodeData

    if (!handles) {
      if (handleType === VFNodeConnectionType.Self) {
        handles = Object.keys(thenodedata.Connections.Inputs)
      } else if (handleType === VFNodeConnectionType.Attach) {
        handles = Object.keys(thenodedata.Connections.Attach)
      } else if (handleType === VFNodeConnectionType.Inputs) {
        handles = Object.keys(thenodedata.Connections.Inputs)
      } else if (handleType === VFNodeConnectionType.Outputs) {
        handles = Object.keys(thenodedata.Connections.Outputs)
      } else {
        handles = []
      }
    }
    handles.forEach((hid) => {
      result.push(...findVarFromIO(nid, handleType, hid))
    })

    return result
  }

  const mapVarItemToSelect = (item: VarItem): SelectOption => {
    return {
      label: `${item.NodeLabel}/${item.DataLabel}/${item.DataType}`,
      value: `${item.NodeId}/${item.DataPath.ContentName}/${item.DataPath.ContentId}`,
    }
  }

  instance = {
    findVarFromIO,
    recursiveFindVariables,
    mapVarItemToSelect,
  }
  return instance
}
