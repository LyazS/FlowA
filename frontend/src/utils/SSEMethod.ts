import { fetchEventSource, type EventSourceMessage } from '@microsoft/fetch-event-source'

type OnOpenCallback = (response: Response) => Promise<void>
type OnMessageCallback = (ev: EventSourceMessage) => void
type OnCloseCallback = () => void
type OnErrorCallback = (err: any) => number | null | undefined | void

export function SubscribeSSE(
  onOpen: OnOpenCallback,
  onMessage: OnMessageCallback,
  onClose: OnCloseCallback,
  onError: OnErrorCallback,
) {
  let controller: AbortController | null = null

  async function subscribe(
    url: string,
    method: string = 'GET',
    headers: Record<string, string> | null = null,
    body: any = null,
  ) {
    // Abort any existing subscription
    if (controller) {
      controller.abort()
    }

    // Create a new AbortController
    controller = new AbortController()
    const signal = controller.signal

    try {
      const sseconfig = {
        method: method,
        signal: signal,
        ...(headers !== null && { headers }),
        ...(body !== null && { body: JSON.stringify(body) }),
        async onopen(event: Response) {
          if (signal.aborted) {
            return
          }
          await onOpen(event)
        },
        onmessage(event: EventSourceMessage) {
          if (signal.aborted) {
            return
          }
          onMessage(event)
        },
        onclose() {
          onClose()
          controller?.abort()
        },
        onerror(err: any) {
          onError(err)
          controller?.abort()
          throw err
        },
      }

      console.log('Subscribing to SSE:', url)
      await fetchEventSource(url, sseconfig)
    } catch (err) {
      console.error('fetchEventSource error:', err)
      onError(err)
      controller?.abort()
    }
  }

  function unsubscribe() {
    if (controller) {
      controller.abort()
      console.log('SSE subscription unsubscribed.')
    }
  }

  return {
    subscribe,
    unsubscribe,
  }
}
