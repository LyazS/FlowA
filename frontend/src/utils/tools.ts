import { fetchEventSource } from '@microsoft/fetch-event-source'
import type { EventSourceMessage } from '@microsoft/fetch-event-source'
import { h } from 'vue'
import { NIcon } from 'naive-ui'

interface SSEConfig {
  method: string
  signal: AbortSignal
  headers?: Record<string, string>
  body?: BodyInit
  onopen?: (response: Response) => Promise<void>
  onmessage?: (ev: EventSourceMessage) => void
  onclose?: () => void
  onerror?: (err: any) => void
  openWhenHidden?: boolean
}

const getFullUuid = (): string => {
  if (typeof crypto === 'object') {
    if (typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID()
    }
    if (typeof crypto.getRandomValues === 'function' && typeof Uint8Array === 'function') {
      const callback = (c: string): string => {
        const num = Number(c)
        return (num ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (num / 4)))).toString(
          16,
        )
      }
      return '10000000-1000-4000-8000-100000000000'.replace(/[018]/g, callback)
    }
  }
  let timestamp = new Date().getTime()
  let perforNow =
    (typeof performance !== 'undefined' && performance.now && performance.now() * 1000) || 0
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c: string) => {
    let random = Math.random() * 16
    if (timestamp > 0) {
      random = (timestamp + random) % 16 | 0
      timestamp = Math.floor(timestamp / 16)
    } else {
      random = (perforNow + random) % 16 | 0
      perforNow = Math.floor(perforNow / 16)
    }
    return (c === 'x' ? random : (random & 0x3) | 0x8).toString(16)
  })
}

export const getUuid = (): string => {
  return getFullUuid().replace(/-/g, '')
}
/**
 * Generates a unique node ID in the format 'NID{...}'.
 * This format is used to distinguish node IDs from traditional UUIDs.
 * Example: NID{123e4567e89b12d3a456426655440000}
 */
export const generateNodeId = (): string => {
  return `NID{${getUuid()}}`
}
export const regexMatchNodeId = (nid: string): { id: string; nested: string[] } => {
  // 匹配整个字符串结构，并提取中间内容
  const mainMatch = /^NID\{([^}]+)}/.exec(nid)
  if (!mainMatch) {
    console.error('Invalid node id:', nid)
    throw new Error('Invalid node id')
  }

  const content = mainMatch[1]
  const id = content.split('#')[0] // 提取 id（第一个 # 之前的部分）

  // 匹配所有非空的嵌套说明（# 后至少一个字符）
  const nested = Array.from(content.matchAll(/#([^#]+)/g), (match) => match[1])

  return { id, nested }
}
export const concatNestedNodeId = (id: string, nested: string[]): string => {
  // Step 1: 验证并提取原始 id 的内容
  const idMatch = /^NID\{([^}]+)}/.exec(id)
  if (!idMatch) {
    console.error('Invalid node id:', id)
    throw new Error('Invalid node id')
  }

  // Step 2: 获取基础内容
  const baseContent = idMatch[1]

  // Step 3: 拼接 nested 参数
  const nestedPart = nested.length > 0 ? `#${nested.join('#')}` : ''

  // Step 4: 组装完整结构
  return `NID{${baseContent}${nestedPart}}`
}

export const sortKeys = (obj: Record<string, any>): string[] =>
  Object.keys(obj).sort((a, b) => a.localeCompare(b))

export const getValueByPath = (obj: Record<string, any>, path: (string | number)[]): any => {
  try {
    return path.reduce(
      (acc: any, key: string | number) => (acc && acc[key] !== undefined ? acc[key] : undefined),
      obj,
    )
  } catch (error) {
    console.error('Invalid path:', path, error)
    return undefined
  }
}

export const setValueByPath = (
  obj: Record<string, any>,
  path: (string | number)[],
  value: any,
): void => {
  try {
    const [head, ...tail] = path
    if (tail.length === 0) {
      obj[head] = value
    } else {
      if (obj[head] === undefined) {
        obj[head] = {}
      }
      setValueByPath(obj[head], tail, value)
    }
  } catch (error) {
    console.error('Invalid path:', path, error)
  }
}

export const isPathConnected = (obj: Record<string, any>, path: (string | number)[]): boolean => {
  try {
    const value = getValueByPath(obj, path)
    return value !== undefined
  } catch (error) {
    return false
  }
}

export function SubscribeSSE(
  url: string,
  method: string,
  headers: Record<string, string> | null,
  body: BodyInit | null,
  onOpen: (event: Response) => Promise<void>,
  onMessage: (event: EventSourceMessage) => void,
  onClose: () => void,
  onError: (err: any) => void,
) {
  const controller = new AbortController()
  const signal = controller.signal

  async function subscribe(): Promise<void> {
    try {
      let sseconfig: SSEConfig = {
        method: method,
        signal: signal,
        ...(headers !== null && { headers }),
        ...(body !== null && { body }),
        async onopen(event: Response) {
          if (signal.aborted) {
            return
          }
          await onOpen(event)
        },
        onmessage(event: EventSourceMessage) {
          if (signal.aborted) return
          onMessage(event)
        },
        onclose() {
          controller.abort()
          onClose()
        },
        onerror(err) {
          controller.abort()
          onError(err)
        },
      }
      console.log('Subscribing to SSE:', url)
      await fetchEventSource(url, sseconfig)
    } catch (err) {
      console.error('fetchEventSource error:', err)
      await onError(err as Error)
      controller.abort()
    }
  }

  function unsubscribe(): void {
    controller.abort()
    console.log('SSE subscription unsubscribed.')
  }

  return {
    subscribe,
    unsubscribe,
  }
}

export function deepFreeze<T>(obj: T): T {
  const propNames = Object.getOwnPropertyNames(obj)

  for (const name of propNames) {
    const value = (obj as any)[name]
    if (typeof value === 'object' && value !== null) {
      deepFreeze(value)
    }
  }

  return Object.freeze(obj)
}

export function isPlainObject(value: any): boolean {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const prototype = Object.getPrototypeOf(value)
  return prototype === Object.prototype || prototype === null
}

export function isString(value: any): value is string {
  return typeof value === 'string'
}

export function isJsonString(value: any): boolean {
  try {
    JSON.parse(value)
    return true
  } catch (e) {
    return false
  }
}

export const downloadJson = (jsonData: string, filename: string): void => {
  const blob = new Blob([jsonData], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()

  URL.revokeObjectURL(url)
  document.body.removeChild(link)
}

export const renderIcon = (icon: any) => {
  return () => {
    return h(NIcon, null, {
      default: () => h(icon),
    })
  }
}

export const formatDateString = (dateString: string): string => {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 通用错误处理工具
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  return `系统异常: ${JSON.stringify(error)}`
}
