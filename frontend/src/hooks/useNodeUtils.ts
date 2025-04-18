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
export interface RefItemValue {
  nid: string
  path: FromInnerPath
}

interface NodeUtilsInstance {
  findVarFromIO: (nid: string, findconnect: VFNodeConnectionType, hid: string) => VarItem[]
  recursiveFindVariables: (
    nid: string,
    handleType: VFNodeConnectionType,
    handles: string[] | null,
  ) => VarItem[]
  uniqueVarItems: (varitems: VarItem[]) => VarItem[]
  mapVarItemToSelect: (item: VarItem) => SelectOption
}
let instance: NodeUtilsInstance | null = null

export const useNodeUtils = () => {
  if (instance) return instance
  const { findNode, getHandleConnections } = useVueFlow()

  const findVarFromIO = (
    nid: string,
    findconnect: VFNodeConnectionType,
    hid: string,
  ): VarItem[] => {
    const result: VarItem[] = []
    const thenode = findNode(nid) as NodeWithVFData

    if (!thenode || !thenode.data.Connections[findconnect]?.ById[hid]) {
      return result
    }
    const thenodedata = thenode.data as VFNodeData
    const connection = thenodedata.Connections[findconnect].ById[hid].Data

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
        handles = thenodedata.Connections.Inputs.Order
      } else if (handleType === VFNodeConnectionType.Attach) {
        handles = thenodedata.Connections.Attach.Order
      } else if (handleType === VFNodeConnectionType.Inputs) {
        handles = thenodedata.Connections.Inputs.Order
      } else if (handleType === VFNodeConnectionType.Outputs) {
        handles = thenodedata.Connections.Outputs.Order
      } else {
        handles = []
      }
    }
    handles.forEach((hid) => {
      result.push(...findVarFromIO(nid, handleType, hid))
    })

    return result
  }

  const uniqueVarItems = (varitems: VarItem[]): VarItem[] => {
    // 使用Map来高效去重，键为唯一标识字符串，值为VarItem对象
    const uniqueMap = new Map<string, VarItem>()

    // 为每个VarItem创建唯一键并存入Map
    varitems.forEach((item) => {
      const key = `${item.NodeId}:${item.DataPath.ContentName}:${item.DataPath.ContentId}`
      if (!uniqueMap.has(key)) {
        uniqueMap.set(key, item)
      }
    })

    // 返回Map中的所有值
    return Array.from(uniqueMap.values())
  }

  const mapVarItemToSelect = (item: VarItem): SelectOption => {
    return {
      label: `${item.NodeLabel}/${item.DataLabel}/${item.DataType}`,
      // value: `${item.NodeId}/${item.DataPath.ContentName}/${item.DataPath.ContentId}`,
      value: JSON.stringify({
        // 符合 RefItemValue 类型
        nid: item.NodeId,
        path: item.DataPath,
      }),
    }
  }

  instance = {
    findVarFromIO,
    recursiveFindVariables,
    uniqueVarItems,
    mapVarItemToSelect,
  }
  return instance
}
