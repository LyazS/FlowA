import nunjucks from 'nunjucks'
import { marked } from 'marked'
import katex from 'katex'

// 定义类型接口
interface Task {
  nid: string
  template: string
  content: Record<string, any>
}

interface Content {
  [key: string]: any
  marked: typeof marked
}

// 配置 Nunjucks 环境（修复参数问题）
const nunjucks_env = nunjucks.configure({ autoescape: true })

const renderMarkdownWithLatex = (markdown: string): string => {
  // 用于存储捕获的 LaTeX 公式
  const latexBlocks: string[] = []
  const inlineLatex: string[] = []
  const displayLatex: string[] = []
  const inlineParenLatex: string[] = []

  // 处理 ```latex 代码块
  let processedMarkdown = markdown.replace(
    /```latex\s*([\s\S]*?)\s*```/g,
    (match: string, latex: string) => {
      const containsOtherLatex =
        /(\$\$.*?\$\$|\\$$.*?\\\]|\$.*?\$|\\\(.*?\\\)|\\begin\{.*?\}.*?\\end\{.*?\})/gs.test(latex)

      if (containsOtherLatex) {
        let processedLatex = latex.replace(/\$\$(.*?)\$\$/gs, (m: string, inner: string) => {
          latexBlocks.push(inner)
          return `@@BLOCK${latexBlocks.length - 1}@@`
        })

        processedLatex = processedLatex.replace(/\\\[(.*?)\\\]/gs, (m: string, inner: string) => {
          displayLatex.push(inner)
          return `@@DISPLAY${displayLatex.length - 1}@@`
        })

        processedLatex = processedLatex.replace(/\$(.*?)\$/g, (m: string, inner: string) => {
          inlineLatex.push(inner)
          return `@@INLINE${inlineLatex.length - 1}@@`
        })

        processedLatex = processedLatex.replace(/\\\((.*?)\\\)/g, (m: string, inner: string) => {
          inlineParenLatex.push(inner)
          return `@@INLINEPAREN${inlineParenLatex.length - 1}@@`
        })

        processedLatex = processedLatex.replace(
          /\\begin{(\w+\*?)}(.*?)\\end{\1}/gs,
          (m: string, env: string, inner: string) => {
            latexBlocks.push(`\\begin{${env}}${inner}\\end{${env}}`)
            return `@@BLOCK${latexBlocks.length - 1}@@`
          },
        )

        return processedLatex
      } else {
        const containsNewline = /\n/.test(latex)
        if (containsNewline) {
          latexBlocks.push(latex.trim())
          return `@@BLOCK${latexBlocks.length - 1}@@`
        } else {
          inlineLatex.push(latex.trim())
          return `@@INLINE${inlineLatex.length - 1}@@`
        }
      }
    },
  )

  // 处理 $$...$$
  processedMarkdown = processedMarkdown.replace(/\$\$(.*?)\$\$/gs, (m: string, inner: string) => {
    latexBlocks.push(inner)
    return `@@BLOCK${latexBlocks.length - 1}@@`
  })

  // 处理 \[...$$
  processedMarkdown = processedMarkdown.replace(/\\\[(.*?)\\\]/gs, (m: string, inner: string) => {
    displayLatex.push(inner)
    return `@@DISPLAY${displayLatex.length - 1}@@`
  })

  // 处理 $...$
  processedMarkdown = processedMarkdown.replace(/\$(.*?)\$/g, (m: string, inner: string) => {
    inlineLatex.push(inner)
    return `@@INLINE${inlineLatex.length - 1}@@`
  })

  // 处理 $...$
  processedMarkdown = processedMarkdown.replace(/\\$(.*?)\\$/g, (m: string, inner: string) => {
    inlineParenLatex.push(inner)
    return `@@INLINEPAREN${inlineParenLatex.length - 1}@@`
  })

  // 处理 \begin{}...\end{}
  processedMarkdown = processedMarkdown.replace(
    /\\begin{(\w+\*?)}(.*?)\\end{\1}/gs,
    (m: string, env: string, inner: string) => {
      latexBlocks.push(`\\begin{${env}}${inner}\\end{${env}}`)
      return `@@BLOCK${latexBlocks.length - 1}@@`
    },
  )

  // 渲染 Markdown
  const html = marked.parse(processedMarkdown) as string

  // 替换块级公式
  const replacedHtml = html
    .replace(/@@BLOCK(\d+)@@/g, (m: string, index: string) => {
      const latex = latexBlocks[parseInt(index)]
      try {
        return katex.renderToString(latex, {
          displayMode: true,
          throwOnError: false,
          output: 'mathml',
        })
      } catch (e) {
        return `$$${latex}$$`
      }
    })
    .replace(/@@DISPLAY(\d+)@@/g, (m: string, index: string) => {
      const latex = displayLatex[parseInt(index)]
      try {
        return katex.renderToString(latex, {
          displayMode: true,
          throwOnError: false,
          output: 'mathml',
        })
      } catch (e) {
        return `\\[${latex}\\]`
      }
    })
    .replace(/@@INLINE(\d+)@@/g, (m: string, index: string) => {
      const latex = inlineLatex[parseInt(index)]
      try {
        return katex.renderToString(latex, {
          throwOnError: false,
          output: 'mathml',
        })
      } catch (e) {
        return `$${latex}$`
      }
    })
    .replace(/@@INLINEPAREN(\d+)@@/g, (m: string, index: string) => {
      const latex = inlineParenLatex[parseInt(index)]
      try {
        return katex.renderToString(latex, {
          throwOnError: false,
          output: 'mathml',
        })
      } catch (e) {
        return `\\(${latex}\\)`
      }
    })

  return replacedHtml
}

// 添加过滤器
nunjucks_env.addFilter('markdown', function (str: string) {
  return renderMarkdownWithLatex(str)
})

// Worker 消息处理（添加类型断言）
;(self as unknown as Worker).onmessage = function (event: MessageEvent<{ tasks: Task[] }>) {
  const { tasks } = event.data

  tasks.forEach(({ nid, template, content }) => {
    try {
      const rendered = nunjucks_env.renderString(template, {
        ...content,
        marked,
      } as Content)
      ;(self as unknown as Worker).postMessage({
        nid,
        success: true,
        rendered,
      })
    } catch (error) {
      ;(self as unknown as Worker).postMessage({
        nid,
        success: false,
        error: (error as Error).message,
      })
    }
  })
}
