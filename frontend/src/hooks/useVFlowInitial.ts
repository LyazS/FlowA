import { ref, reactive, markRaw, onBeforeMount, type Ref, type Component } from 'vue'
import { VFNode } from '@/components/nodes/VFNodeClass'

interface VFlowInitInstance {
  AllVFNodeTypes: Record<string, Component>
  AllNodeCreateFuncs: Ref<Record<string, () => VFNode>>
  AllTestNodes: Ref<Record<string, VFNode>>
  importAllNodes: () => Promise<void>
  createVFNode: (ntype: string) => VFNode
}

// 单例模式
let instance: VFlowInitInstance | null = null

export const useVFlowInitial = (): VFlowInitInstance => {
  if (instance) return instance

  const AllVFNodeTypes = reactive<Record<string, Component>>({})
  const AllNodeCreateFuncs = ref<Record<string, () => VFNode>>({})
  const AllTestNodes = ref<Record<string, VFNode>>({})

  interface NodeModule {
    createNode: () => VFNode
    NodeVue: Component
  }

  const importAllNodes = async () => {
    const modules = import.meta.glob('../components/nodes/all_nodes_ts/**.ts') as Record<
      string,
      () => Promise<NodeModule>
    >

    const promises = Object.keys(modules).map(async (key) => {
      const module = await modules[key]()
      const test_node = module.createNode()
      AllNodeCreateFuncs.value[test_node.ntype] = module.createNode
      AllTestNodes.value[test_node.ntype] = test_node
      if (!AllVFNodeTypes.hasOwnProperty(test_node.vtype)) {
        AllVFNodeTypes[test_node.vtype] = markRaw(module.NodeVue)
      }
    })

    await Promise.all(promises)
    console.debug('All nodes imported')
  }

  const createVFNode = (ntype: string) => {
    return AllNodeCreateFuncs.value[ntype]()
  }

  instance = {
    AllVFNodeTypes,
    AllNodeCreateFuncs,
    AllTestNodes,
    importAllNodes,
    createVFNode,
  }

  return instance
}
