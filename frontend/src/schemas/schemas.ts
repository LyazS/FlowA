import { type GraphNode } from '@vue-flow/core'
import { type VFNode } from '@/components/nodes/VFNodeClass'

export type NodeWithVFData = Omit<GraphNode, 'data'> & { data: VFNode }

export type HeaderType = 'default' | 'error' | 'info' | 'success' | 'warning'

export interface VarItem4Selections {
  nodeId: string | number
  nlabel: string
  dpath: (string | number)[]
  dlabel: string
  dkey: string
  dtype: string
}

export interface InputNode {
  srcid: string
  srcohid: string
}
