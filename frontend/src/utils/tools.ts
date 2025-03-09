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
