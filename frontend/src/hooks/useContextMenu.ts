// hooks/useContextMenu.ts
import { ref, reactive, type Ref } from 'vue'
import { useVueFlow, type GraphNode, type GraphEdge } from '@vue-flow/core'
import { type NodeAddInfo, useVFlowManager } from './useVFlowManager'
import { useVFlowInitial } from './useVFlowInitial'
import { useVFlowRequest } from '@/services/useVFlowRequest'
import { VFNodeFlag } from '@/components/nodes/VFNodeInterface'
import { VFNode } from '@/components/nodes/VFNodeClass'
import Logger from '@/utils/Logger'
import { selectedNodeId } from '@/hooks/useVFlowAttribute'
import { useCopyPasteNode } from './useCopyPasteNode'

// 定义菜单项类型
interface MenuItem {
  label: string
  onClick?: () => void
  children?: MenuItem[]
}

// 定义菜单选项类型
interface MenuOptions {
  theme: string
  zIndex: number
  minWidth: number
  x: number
  y: number
  items: MenuItem[]
}

interface BaseContextMenuEvent {
  event: MouseEvent
}

export interface NodeContextMenuEvent extends BaseContextMenuEvent {
  type: 'node'
  node: GraphNode
  edge?: never // 明确排除其他类型
}

export interface EdgeContextMenuEvent extends BaseContextMenuEvent {
  type: 'edge'
  edge: GraphEdge
  node?: never
}

export interface PaneContextMenuEvent extends BaseContextMenuEvent {
  type: 'pane'
  node?: never
  edge?: never
}
// 最终的事件类型是这三个的联合类型
export type ContextMenuEvent = NodeContextMenuEvent | EdgeContextMenuEvent | PaneContextMenuEvent
// 定义上下文菜单实例类型
interface ContextMenuInstance {
  showMenu: Ref<boolean>
  menuOptions: MenuOptions
  initContextMenu: () => void
  showContextMenu: (event_cm: ContextMenuEvent) => void
}

// 单例模式
let instance: ContextMenuInstance | null = null

export const useContextMenu = (): ContextMenuInstance => {
  if (instance) return instance

  const logger = new Logger('ContextMenu')

  const { screenToFlowCoordinate, removeEdges } = useVueFlow()
  const { AllTestNodes, AllProviders } = useVFlowInitial()
  const {
    removeNodeFromVFlow,
    removeEdgeFromVFlow,
    buildNestedNodeGraph,
    recursiveUpdateNodeSize,
    addNodeToVFlow,
  } = useVFlowManager()
  const { copyNode, pasteNode } = useCopyPasteNode()

  const showMenu = ref(false)
  const menuOptions = reactive<MenuOptions>({
    theme: 'mac dark',
    zIndex: 3,
    minWidth: 50,
    x: 0,
    y: 0,
    items: [],
  })

  // 预构建的多级菜单项（按Provider和Path分组）
  const prebuiltPaneNodeMenu = ref<MenuItem[]>([])
  const prebuiltNestedNodeMenu = ref<MenuItem[]>([])

  // 当前右键点击事件
  let currentEvent: ContextMenuEvent | undefined

  // 创建添加节点的通用处理函数
  const createAddNodeHandler = (ntype: string) => {
    return () => {
      if (!currentEvent) return

      logger.log('add node', ntype)
      const node_info: NodeAddInfo = {
        type: 'client',
        ntype: ntype,
        parentNodeId: currentEvent.node?.id,
        pos: {
          ...screenToFlowCoordinate({
            x: currentEvent.event.clientX,
            y: currentEvent.event.clientY,
          }),
        },
      }
      addNodeToVFlow(node_info)
      currentEvent = undefined
    }
  }

  // 构建分层菜单
  const buildHierarchicalMenu = (nodes: any[]) => {
    // 创建一个映射，用于存储每个Provider的节点
    const providerMap: Record<string, MenuItem> = {}

    // 遍历所有Provider
    for (const providerKey in AllProviders.value) {
      const provider = AllProviders.value[providerKey]

      // 为每个Provider创建一个菜单项
      providerMap[providerKey] = {
        label: provider.Label,
        children: []
      }

      // 遍历Provider的所有插件
      for (const plugin of provider.Plugins) {
        // 检查该插件对应的节点是否在传入的节点列表中
        const node = nodes.find(n => n.NType === plugin.CreateInfo?.NType)
        if (!node) continue

        // 如果插件有Path，则按Path分组
        if (plugin.Path) {
          // 清理Path前后的斜杠，然后按斜杠分割成多级
          const cleanPath = plugin.Path.replace(/^\/+|\/+$/g, '')
          const pathParts = cleanPath.split('/').filter(part => part.length > 0)

          if (pathParts.length > 0) {
            // 从Provider的子菜单开始
            let currentMenu = providerMap[providerKey].children!
            let currentPath = ''

            // 为每一级Path创建对应的菜单项
            for (let i = 0; i < pathParts.length; i++) {
              const part = pathParts[i]
              currentPath += (currentPath ? '/' : '') + part

              // 查找当前路径是否已有菜单项
              let pathMenuItem = currentMenu.find(item => item.label === part)

              // 如果没有，则创建一个
              if (!pathMenuItem) {
                pathMenuItem = {
                  label: part,
                  children: []
                }
                currentMenu.push(pathMenuItem)
              }

              // 确保children数组存在
              if (!pathMenuItem.children) {
                pathMenuItem.children = []
              }

              // 移动到下一级菜单
              currentMenu = pathMenuItem.children
            }

            // 将节点添加到最后一级Path的子菜单中
            currentMenu.push({
              label: node.Label,
              onClick: createAddNodeHandler(node.NType)
            })
          } else {
            // 如果Path为空或只有斜杠，则直接添加到Provider的子菜单中
            providerMap[providerKey].children!.push({
              label: node.Label,
              onClick: createAddNodeHandler(node.NType)
            })
          }
        } else {
          // 如果插件没有Path，则直接添加到Provider的子菜单中
          providerMap[providerKey].children!.push({
            label: node.Label,
            onClick: createAddNodeHandler(node.NType)
          })
        }
      }

      // 如果Provider没有子菜单，则删除该Provider
      if (providerMap[providerKey].children!.length === 0) {
        delete providerMap[providerKey]
      }
    }

    // 将Provider映射转换为菜单项数组
    return Object.values(providerMap)
  }

  const initContextMenu = () => {
    // 初始化节点列表并直接构建菜单
    const nodesInPane = Object.entries(AllTestNodes.value)
      .sort((a, b) => a[0].localeCompare(b[0])) // 按key排序
      .map(([_, item]) => item) // 使用下划线表示未使用的变量
      .filter((item) => !item.isAttachedNode())

    const nodesInNest = Object.entries(AllTestNodes.value)
      .sort((a, b) => a[0].localeCompare(b[0])) // 按key排序
      .map(([_, item]) => item) // 使用下划线表示未使用的变量
      .filter((item) => !item.isAttachedNode() && !(VFNodeFlag.IsPassive & item.Flag))

    // 构建分层菜单（按Provider和Path分组）
    prebuiltPaneNodeMenu.value = buildHierarchicalMenu(nodesInPane)
    prebuiltNestedNodeMenu.value = buildHierarchicalMenu(nodesInNest)

    logger.debug('nodesInPane', nodesInPane)
    logger.debug('nodesInNest', nodesInNest)
    logger.debug('prebuiltPaneNodeMenu', prebuiltPaneNodeMenu.value)
    logger.debug('prebuiltNestedNodeMenu', prebuiltNestedNodeMenu.value)
  }

  const onClickContextMenuRmNode = (event_cm: NodeContextMenuEvent) => {
    logger.debug('删除节点')
    const node = event_cm.node
    const parent_id = node.parentNode
    removeNodeFromVFlow(node)
    buildNestedNodeGraph()
    recursiveUpdateNodeSize(parent_id)
  }

  const AddNodeList = (event_cm: ContextMenuEvent) => {
    // 更新当前事件引用
    currentEvent = event_cm

    // 根据上下文选择预构建的菜单项
    if (event_cm.type == 'node' && (event_cm.node.data as VFNode).isNestedNode()) {
      return prebuiltNestedNodeMenu.value
    } else {
      return prebuiltPaneNodeMenu.value
    }
  }

  const onClickContextMenuRmEdge = (event_cm: EdgeContextMenuEvent) => {
    logger.debug('删除边')
    removeEdgeFromVFlow([event_cm.edge])
  }

  const showContextMenu = (event_cm: ContextMenuEvent) => {
    menuOptions.x = event_cm.event.clientX
    menuOptions.y = event_cm.event.clientY
    showMenu.value =
      (event_cm.type === 'node' && !(event_cm.node.data as VFNode).isAttachedNode()) ||
      event_cm.type === 'pane' ||
      event_cm.type === 'edge'
    let show_add_node =
      (event_cm.type === 'node' && (event_cm.node.data as VFNode).isNestedNode()) ||
      event_cm.type === 'pane'
    let show_rm_node = event_cm.type === 'node' && !(event_cm.node.data as VFNode).isAttachedNode()
    let show_rm_edge = event_cm.type === 'edge'
    let show_copy = event_cm.type === 'node' && !(event_cm.node.data as VFNode).isAttachedNode()
    let show_paste_root = event_cm.type === 'pane'
    let show_paste_nest = event_cm.type === 'node' && (event_cm.node.data as VFNode).isNestedNode()
    menuOptions.items = []

    if (show_add_node) {
      menuOptions.items.push({
        label: '添加节点',
        children: AddNodeList(event_cm),
      })
    }
    if (show_rm_node) {
      menuOptions.items.push({
        label: '删除节点',
        onClick: () => onClickContextMenuRmNode(event_cm as NodeContextMenuEvent),
      })
    }
    if (show_rm_edge) {
      menuOptions.items.push({
        label: '删除边',
        onClick: () => onClickContextMenuRmEdge(event_cm as EdgeContextMenuEvent),
      })
    }
    if (show_copy) {
      menuOptions.items.push({
        label: '复制节点',
        onClick: () => {
          copyNode((event_cm as NodeContextMenuEvent).node)
        },
      })
    }
    if (show_paste_nest) {
      menuOptions.items.push({
        label: '粘贴节点',
        onClick: () => {
          pasteNode((event_cm as NodeContextMenuEvent).node.id, {
            x: event_cm.event.clientX,
            y: event_cm.event.clientY,
          })
        },
      })
    }
    if (show_paste_root) {
      menuOptions.items.push({
        label: '粘贴节点',
        onClick: () => {
          pasteNode(null, {
            x: event_cm.event.clientX,
            y: event_cm.event.clientY,
          })
        },
      })
    }
  }

  instance = {
    showMenu,
    menuOptions,
    initContextMenu,
    showContextMenu,
  }

  return instance
}
