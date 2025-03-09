import type { SelectOption, AutoCompleteOption, AutoCompleteGroupOption } from 'naive-ui'

interface HeaderItem {
  label: string
  key: string
  value: string
  description: string
}

interface CombinedHeader {
  label: string
  headers: HeaderItem[]
}

interface SelectGroup {
  type: 'group'
  key: string
  label: string
  children: SelectOption[]
}

// 内容协商
const contentNegotiation: HeaderItem[] = [
  {
    label: 'JSON数据',
    key: 'Content-Type',
    value: 'application/json',
    description: '发送JSON格式的数据',
  },
  {
    label: '表单数据',
    key: 'Content-Type',
    value: 'application/x-www-form-urlencoded',
    description: '发送表单编码数据',
  },
  {
    label: '多部分表单',
    key: 'Content-Type',
    value: 'multipart/form-data',
    description: '上传文件或多部分数据',
  },
  {
    label: '纯文本',
    key: 'Content-Type',
    value: 'text/plain',
    description: '发送纯文本数据',
  },
  {
    label: 'HTML文档',
    key: 'Content-Type',
    value: 'text/html',
    description: '发送HTML格式数据',
  },
  {
    label: 'XML数据',
    key: 'Content-Type',
    value: 'application/xml',
    description: '发送XML格式数据',
  },
  {
    label: '接受类型',
    key: 'Accept',
    value: 'application/json, text/plain, */*',
    description: '指定客户端接受的内容类型',
  },
  {
    label: '接受字符集',
    key: 'Accept-Charset',
    value: 'utf-8, iso-8859-1;q=0.5',
    description: '指定客户端接受的字符编码',
  },
  {
    label: '接受语言',
    key: 'Accept-Language',
    value: 'zh-CN,zh;q=0.9,en;q=0.8',
    description: '指定客户端接受的语言',
  },
]

// 缓存控制
const cacheControl: HeaderItem[] = [
  {
    label: '禁止缓存',
    key: 'Cache-Control',
    value: 'no-cache, no-store, must-revalidate',
    description: '完全禁止缓存',
  },
  {
    label: '验证缓存',
    key: 'Cache-Control',
    value: 'no-cache',
    description: '强制向服务端验证缓存是否过期',
  },
  {
    label: '私有缓存',
    key: 'Cache-Control',
    value: 'private, max-age=3600',
    description: '仅允许浏览器缓存1小时',
  },
  {
    label: '公共缓存',
    key: 'Cache-Control',
    value: 'public, max-age=86400',
    description: '允许中间代理缓存1天',
  },
  {
    label: '协商缓存',
    key: 'If-None-Match',
    value: '',
    description: '配合ETag进行缓存验证',
  },
  {
    label: '条件请求',
    key: 'If-Modified-Since',
    value: '',
    description: '配合Last-Modified进行缓存验证',
  },
]

// 认证授权
const authentication: HeaderItem[] = [
  {
    label: 'Bearer认证',
    key: 'Authorization',
    value: 'Bearer {token}',
    description: '使用Bearer token进行认证',
  },
  {
    label: 'Basic认证',
    key: 'Authorization',
    value: 'Basic {base64(username:password)}',
    description: '使用Basic认证方式',
  },
  {
    label: 'API密钥',
    key: 'X-API-Key',
    value: '{apiKey}',
    description: '使用API Key进行认证',
  },
  {
    label: 'Session认证',
    key: 'Cookie',
    value: 'sessionId={sessionId}',
    description: '使用Cookie进行会话认证',
  },
]

// 请求上下文
const context: HeaderItem[] = [
  {
    label: '来源页面',
    key: 'Referer',
    value: 'https://example.com/page',
    description: '请求的来源页面URL',
  },
  {
    label: '用户代理',
    key: 'User-Agent',
    value:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    description: '客户端应用程序信息',
  },
  {
    label: '来源域名',
    key: 'Origin',
    value: 'https://example.com',
    description: '跨域请求的来源域名',
  },
  {
    label: '真实IP',
    key: 'X-Real-IP',
    value: '',
    description: '客户端的真实IP地址',
  },
  {
    label: '转发IP',
    key: 'X-Forwarded-For',
    value: '',
    description: '请求经过的代理服务器IP',
  },
]

// CORS跨域
const cors: HeaderItem[] = [
  {
    label: '允许源',
    key: 'Access-Control-Allow-Origin',
    value: '*',
    description: '允许跨域访问的源',
  },
  {
    label: '允许方法',
    key: 'Access-Control-Allow-Methods',
    value: 'GET, POST, PUT, DELETE, OPTIONS',
    description: '允许的HTTP请求方法',
  },
  {
    label: '允许头部',
    key: 'Access-Control-Allow-Headers',
    value: 'Content-Type, Authorization, X-Requested-With',
    description: '允许的请求头字段',
  },
  {
    label: '允许凭证',
    key: 'Access-Control-Allow-Credentials',
    value: 'true',
    description: '是否允许发送Cookie',
  },
  {
    label: '暴露头部',
    key: 'Access-Control-Expose-Headers',
    value: 'Content-Length, X-Custom-Header',
    description: '允许浏览器访问的响应头',
  },
  {
    label: '预检过期',
    key: 'Access-Control-Max-Age',
    value: '3600',
    description: '预检请求的有效期',
  },
]

// 内容编码
const contentEncoding: HeaderItem[] = [
  {
    label: '压缩编码',
    key: 'Accept-Encoding',
    value: 'gzip, deflate, br',
    description: '客户端支持的压缩算法',
  },
  {
    label: '传输编码',
    key: 'Transfer-Encoding',
    value: 'chunked',
    description: '分块传输编码',
  },
  {
    label: '内容长度',
    key: 'Content-Length',
    value: '',
    description: '请求体的字节长度',
  },
]

// 安全相关
const security: HeaderItem[] = [
  {
    label: '安全策略',
    key: 'Content-Security-Policy',
    value: "default-src 'self'",
    description: '内容安全策略',
  },
  {
    label: '框架选项',
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN',
    description: '防止点击劫持',
  },
  {
    label: 'XSS防护',
    key: 'X-XSS-Protection',
    value: '1; mode=block',
    description: '开启XSS过滤',
  },
  {
    label: '内容类型',
    key: 'X-Content-Type-Options',
    value: 'nosniff',
    description: '禁止MIME类型嗅探',
  },
  {
    label: '引用策略',
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
    description: '控制Referer头的内容',
  },
]

// 代理和负载均衡
const proxy: HeaderItem[] = [
  {
    label: '代理认证',
    key: 'Proxy-Authorization',
    value: 'Basic {credentials}',
    description: '代理服务器认证信息',
  },
  {
    label: '负载均衡',
    key: 'X-Load-Balancer',
    value: '',
    description: '负载均衡器信息',
  },
]

// 自定义业务
const custom: HeaderItem[] = [
  {
    label: '请求追踪',
    key: 'X-Request-ID',
    value: '',
    description: '请求的唯一标识符',
  },
  {
    label: '设备类型',
    key: 'X-Device-Type',
    value: 'web',
    description: '客户端设备类型',
  },
  {
    label: '应用版本',
    key: 'X-App-Version',
    value: '1.0.0',
    description: '客户端应用版本',
  },
  {
    label: '时区信息',
    key: 'X-Time-Zone',
    value: 'Asia/Shanghai',
    description: '客户端时区信息',
  },
]

const combinedHeaders: CombinedHeader[] = [
  { label: '内容协商', headers: contentNegotiation },
  { label: '缓存控制', headers: cacheControl },
  { label: '认证授权', headers: authentication },
  { label: '请求上下文', headers: context },
  { label: 'CORS跨域', headers: cors },
  { label: '内容编码', headers: contentEncoding },
  { label: '安全相关', headers: security },
  { label: '代理相关', headers: proxy },
  { label: '用户自定义', headers: custom },
]
const buildHeaders = (
  cbheaders: CombinedHeader[],
): [AutoCompleteGroupOption[], Record<string, AutoCompleteOption[]>] => {
  const keySelectGroup: AutoCompleteGroupOption[] = []
  const valueSelect: Record<string, AutoCompleteOption[]> = {}

  for (const cbheader of cbheaders) {
    const plabel = cbheader.label
    const group: AutoCompleteGroupOption = {
      type: 'group',
      key: plabel,
      label: plabel,
      children: [],
    }

    for (const headers of cbheader.headers) {
      const { key, value } = headers
      if (!valueSelect.hasOwnProperty(key)) {
        valueSelect[key] = []
        group.children.push({ label: key, value: key })
      }
      if (value !== '') {
        valueSelect[key].push({ label: value, value: value })
      }
    }
    keySelectGroup.push(group)
  }

  // 清理空的 valueSelect
  for (const key in valueSelect) {
    if (valueSelect[key].length === 0) {
      delete valueSelect[key]
    }
  }

  return [keySelectGroup, valueSelect]
}
const [HeaderKeySelectGroup, HeaderValueSelect] = buildHeaders(combinedHeaders)

const HttpMethodSelect: SelectOption[] = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' },
  { label: 'HEAD', value: 'HEAD' },
  { label: 'PATCH', value: 'PATCH' },
]

const HttpBodyTypeSelect: SelectOption[] = [
  { label: '无', value: 'none' },
  { label: 'JSON', value: 'json' },
  { label: 'x-www-form-urlencoded', value: 'x-www-form-urlencoded' },
  { label: 'form-data', value: 'form-data' },
  { label: '纯文本', value: 'text' },
  // { label: "文件", value: "file" },
]

const FormDataContentTypeSelect: SelectOption[] = [
  { label: 'String', value: 'String' },
  { label: 'File', value: 'File' },
]

const HttpContentTypeSelect: SelectOption[] = [
  { label: 'application/json', value: 'application/json' },
  { label: 'application/x-www-form-urlencoded', value: 'application/x-www-form-urlencoded' },
  { label: 'multipart/form-data', value: 'multipart/form-data' },
  { label: 'text/plain', value: 'text/plain' },
  { label: 'text/html', value: 'text/html' },
  { label: 'application/xml', value: 'application/xml' },
  { label: 'image/jpeg', value: 'image/jpeg' },
  { label: '其他', value: 'other' },
]

export interface Http_Header {
  key: string
  value: string
}
export interface Http_Body {
  type: string
  content1: string
  content2: Array<{ key: string; value: string }>
  content3: Array<{ key: string; type: string; value: string }>
}

export interface Http_Cookie {
  key: string
  value: string
}

export interface Timeout {
    label: string
    cpValue: {
      value: number
    }
  }
export {
  HeaderKeySelectGroup,
  HeaderValueSelect,
  HttpMethodSelect,
  HttpBodyTypeSelect,
  FormDataContentTypeSelect,
  HttpContentTypeSelect,
}
