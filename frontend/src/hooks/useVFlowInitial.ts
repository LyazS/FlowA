import { ref, reactive, markRaw, onBeforeMount, type Ref, type Component } from 'vue'
import { VFNode, createVFNodeFromData } from '@/components/nodes/VFNodeClass'
import { postData, getData, type FAWorkflowOperationResponse } from '@/utils/requestMethod'
import Logger from '@/utils/Logger'
import type {
  BaseComponent,
  VFProvider,
  VFUIPlugin,
  VFPlugin,
} from '@/schemas/plugin_schemas'
import basenode from '@/components/nodes/all_nodes_vue/basenode.vue'
import attached_node from '@/components/nodes/all_nodes_vue/attached_node.vue'

interface VFlowInitInstance {
  AllProviders: Ref<Record<string, VFProvider>>
  AllVFNodeTypes: Record<string, Component>
  AllNodeCreateFuncs: Ref<Record<string, () => VFNode>>
  AllTestNodes: Ref<Record<string, VFNode>>
  AllUIComponents: Ref<Record<string, BaseComponent>>
  AllNodeConfig: Ref<Record<string, any>>
  importAllNodes: () => Promise<void>
  createVFNode: (ntype: string) => VFNode
}

// 单例模式
let instance: VFlowInitInstance | null = null

export const useVFlowInitial = (): VFlowInitInstance => {
  if (instance) return instance

  const logger = new Logger('Initial')

  const AllProviders = ref<Record<string, VFProvider>>({})
  const AllVFNodeTypes = reactive<Record<string, Component>>({})
  const AllNodeCreateFuncs = ref<Record<string, () => VFNode>>({})
  const AllTestNodes = ref<Record<string, VFNode>>({})
  const AllUIComponents = ref<Record<string, BaseComponent>>({})
  const AllNodeConfig = ref<Record<string, any>>({})

  const importAllNodes = async () => {
    const response = await getData<Record<string, VFProvider>>('node/initinfo')
    logger.debug('getCreateInfo', response)
    AllProviders.value = response
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

    const allconfig_response = await getData<Record<string, any>>('node/allconfig')
    AllNodeConfig.value = allconfig_response

    logger.debug('AllNodeCreateFuncs', AllNodeCreateFuncs.value)
    logger.debug('AllTestNodes', AllTestNodes.value)
    logger.debug('AllUIComponents', AllUIComponents.value)
    logger.debug('AllNodeConfig', AllNodeConfig.value)
  }

  const createVFNode = (ntype: string) => {
    return AllNodeCreateFuncs.value[ntype]()
  }

  instance = {
    AllProviders,
    AllVFNodeTypes,
    AllNodeCreateFuncs,
    AllTestNodes,
    AllUIComponents,
    AllNodeConfig,
    importAllNodes,
    createVFNode,
  }

  return instance
}
