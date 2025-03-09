import axios, { AxiosError, type AxiosResponse } from 'axios'
// 定义后端响应类型
export interface FAWorkflowOperationResponse<T = any> {
  type: 'success' | 'error'
  message?: string
  data?: T
}

// 统一请求函数
async function axiosRequest<T = any>(url: string, method: 'get' | 'post', data?: any): Promise<T> {
  try {
    const response = await axios({
      method,
      url: `${import.meta.env.VITE_API_URL}/${url}`,
      data: method === 'post' ? data : undefined,
    })

    const result: FAWorkflowOperationResponse = response.data

    // 根据业务逻辑判断是否视为成功
    if (result.type !== 'success') {
      throw new Error(result.message || 'Request failed')
    }

    return result.data as T // 返回有效数据
  } catch (error) {
    const axiosError = error as AxiosError<FAWorkflowOperationResponse>

    // 构造友好错误信息
    let errorMsg = '请求失败'
    if (axiosError.response?.data?.message) {
      errorMsg += `: ${axiosError.response.data.message}`
    } else if (axiosError.message) {
      errorMsg += `: ${axiosError.message}`
    }

    throw new Error(errorMsg) // 统一抛出可读错误
  }
}

// 封装GET/POST方法
export const getData = <T = any>(url: string) => axiosRequest<T>(url, 'get')
export const postData = <T = any>(url: string, data?: any) => axiosRequest<T>(url, 'post', data)
