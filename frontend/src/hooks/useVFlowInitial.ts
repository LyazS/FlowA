import { ref, reactive, markRaw, onBeforeMount, type Ref, type Component } from 'vue'
import { VFNode, createVFNodeFromData } from '@/components/nodes/VFNodeClass'
import { postData, getData, type FAWorkflowOperationResponse } from '@/utils/requestMethod'
import Logger from '@/utils/Logger'
import type {
  BaseComponent,
  VFProvider,
  VFUIPlugin,
  VFPlugin,
  VFPluginSetting,
} from '@/schemas/plugin_schemas'
import basenode from '@/components/nodes/all_nodes_vue/basenode.vue'
import attached_node from '@/components/nodes/all_nodes_vue/attached_node.vue'

interface VFlowInitInstance {
  AllVFNodeTypes: Record<string, Component>
  AllNodeCreateFuncs: Ref<Record<string, () => VFNode>>
  AllTestNodes: Ref<Record<string, VFNode>>
  AllUIComponents: Ref<Record<string, BaseComponent>>
  importAllNodes: () => Promise<void>
  createVFNode: (ntype: string) => VFNode
}

// 单例模式
let instance: VFlowInitInstance | null = null

export const useVFlowInitial = (): VFlowInitInstance => {
  if (instance) return instance

  const logger = new Logger('Initial')

  const AllVFNodeTypes = reactive<Record<string, Component>>({})
  const AllNodeCreateFuncs = ref<Record<string, () => VFNode>>({})
  const AllTestNodes = ref<Record<string, VFNode>>({})
  const AllUIComponents = ref<Record<string, BaseComponent>>({})

  const importAllNodes = async () => {
    // const modules = import.meta.glob('../components/nodes/all_nodes_ts/**.ts') as Record<
    //   string,
    //   () => Promise<NodeModule>
    // >

    // const promises = Object.keys(modules).map(async (key) => {
    //   const module = await modules[key]()
    //   const test_node = module.createNode()
    //   AllNodeCreateFuncs.value[test_node.ntype] = module.createNode
    //   AllTestNodes.value[test_node.ntype] = test_node
    //   if (!AllVFNodeTypes.hasOwnProperty(test_node.vtype)) {
    //     AllVFNodeTypes[test_node.vtype] = markRaw(module.NodeVue)
    //   }
    // })

    // await Promise.all(promises)
    // logger.debug('All nodes imported')

    const response = await getData<Record<string, VFProvider>>('node/initinfo')
    logger.debug('getCreateInfo', response)
    for (const provider in response) {
      for (const plugin of response[provider].Plugins) {
        // 获取插件的创建信息
        const createInfo = plugin.CreateInfo
        if (createInfo) {
          const ntype = createInfo.NType
          // 存储节点创建函数
          AllNodeCreateFuncs.value[ntype] = () => createVFNodeFromData(createInfo)
          // 创建测试节点实例
          const testNode = AllNodeCreateFuncs.value[ntype]()
          AllTestNodes.value[ntype] = testNode
          // 如果视图类型不存在，则添加对应的组件
          if (!AllVFNodeTypes.hasOwnProperty(createInfo.VType)) {
            if (createInfo.VType === 'basenode') {
              AllVFNodeTypes[createInfo.VType] = markRaw(basenode)
            } else if (createInfo.VType === 'attached_node') {
              AllVFNodeTypes[createInfo.VType] = markRaw(attached_node)
            }
          }
        }
      }
      for (const uiplugin of response[provider].UIPlugins) {
        if (uiplugin.Type == 'FANode') {
          AllUIComponents.value[uiplugin.Name] = uiplugin.Component
        }
      }
    }
    logger.debug('AllNodeCreateFuncs', AllNodeCreateFuncs.value)
    logger.debug('AllTestNodes', AllTestNodes.value)
    logger.debug('AllUIComponents', AllUIComponents.value)
  }

  const createVFNode = (ntype: string) => {
    return AllNodeCreateFuncs.value[ntype]()
  }

  instance = {
    AllVFNodeTypes,
    AllNodeCreateFuncs,
    AllTestNodes,
    AllUIComponents,
    importAllNodes,
    createVFNode,
  }

  return instance
}
