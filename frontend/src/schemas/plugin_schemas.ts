import { z } from 'zod'
import {
  type CodeEditorLanguage,
  type VFNodeHandleData,
  VFNodeConnectionType,
  type VFNodeContentData,
} from '@/components/nodes/VFNodeInterface'
import { InsertPos } from '@/components/nodes/VFNodeClass'

// 特殊定义 =====================================================================
// 路径定义
export const THIS_NODE_DATA = '@THIS_NODE_DATA@' as const
export const COMPONENT_CONTEXT = '@COMPONENT_CONTEXT@' as const
export const VFOR_DATA = '@VFOR_DATA@' as const
export const NODE_CONFIG_DATA = '@NODE_CONFIG_DATA@' as const
export const PAYLOADS_ID = '@PAYLOADS_ID@' as const
export const ARG_CONTEXT = '@ARG_CONTEXT@' as const
// 专供FUNCTION_CONTEXT
// export const GENERATE_UUID = '@GENERATE_UUID@' as const
// 连接项定义，路径为[CONNECT_*, <Handle Type>, <Handle Id>], 如果没有<Handle Id>则默认获取所有<Handle Id>
export const CONNECT_DATA = '@CONNECT_DATA@' as const
export const CONNECT_DATA_TO_SELECT = '@CONNECT_DATA_TO_SELECT@' as const
// 连接项的参数定义
export const CONNECT_ALL_DATA = '@CONNECT_ALL_DATA@'
export const CONNECT_CUR_NODE = '@CONNECT_CUR_NODE@'
export const CONNECT_PARENT_NODE = '@CONNECT_PARENT_NODE@'
export const CONNECT_CHILD_NODE = '@CONNECT_CHILD_NODE@'
export const CONNECT_PRE_NODE = '@CONNECT_PRE_NODE@'
export const CONNECT_NODE_LEVEL = '@CONNECT_NODE_LEVEL@'
export const CONNECT_HANDLE_LEVEL = '@CONNECT_HANDLE_LEVEL@'
export const CONNECT_VAR_LEVEL = '@CONNECT_VAR_LEVEL@'
// 类型定义
export const TYPE_VFOR = '@VFOR@' as const
export const TYPE_VSPAN = '@VSPAN@' as const
export const TYPE_CONDITION_COMPARE = '@CONDITION_COMPARE@' as const
export const TYPE_CONDITION_LOGICAL = '@CONDITION_LOGICAL@' as const
export const TYPE_CONDITION_DIRECT = '@CONDITION_DIRECT@' as const
export const TYPE_CONDITION_VBIND = '@CONDITION_VBIND@' as const
export const TYPE_CONDITION_VALUE = '@CONDITION_VALUE@' as const
export enum FunctionPropType {
  // Operate =======================
  SETCONTEXT = '@SETCONTEXT@',
  ADDITEM = '@ADDITEM@',
  REMOVEITEM = '@REMOVEITEM@',
  APPENDITEM = '@APPENDITEM@',
  ADDPAYLOAD = '@ADDPAYLOAD@',
  REMOVEPAYLOAD = '@REMOVEPAYLOAD@',
  ADDRESULT = '@ADDRESULT@',
  REMOVERESULT = '@REMOVERESULT@',
  ADDRESULT2OUT = '@ADDRESULT2OUT@',
  REMOVERESULT4OUT = '@REMOVERESULT4OUT@',
  ADDHANDLE = '@ADDHANDLE@',
  REMOVEHANDLE = '@REMOVEHANDLE@',
  ADDHANDLEDATA = '@ADDHANDLEDATA@',
  REMOVEHANDLEDATA = '@REMOVEHANDLEDATA@',
  UPDATENODEINTERNAL = '@UPDATENODEINTERNAL@',
  OPENEDITOR = '@OPENEDITOR@',
  // Return =======================
  UPLOADIMAGE = '@UPLOADIMAGE@',
  GENERATEUUID = '@GENERATEUUID@',
  FORMATSTRING = '@FORMATSTRING@',
}
export enum PropVarType {
  Value = '@VALUE@',
  VBind = '@VBIND@',
  VModel = '@VMODEL@',
  OperateFunc = '@OPERATEFUNC@',
  ReturnFunc = '@RETURNFUNC@',
  AReturnFunc = '@ARETURNFUNC@',
}

// =============================================================================
// 接口定义
export interface PropVarBase {
  FA_Type__: PropVarType
}

export interface ValueProp<T = any> extends PropVarBase {
  FA_Type__: PropVarType.Value
  FA_Data__: T
}

export interface VBindProp extends PropVarBase {
  FA_Type__: PropVarType.VBind
  FA_Data__: (ValueProp | VBindProp)[]
  FA_Replace__?: string
}

export interface VModelProp extends PropVarBase {
  FA_Type__: PropVarType.VModel
  FA_Data__: (ValueProp | VBindProp)[]
}

// 函数参数接口定义
export interface FuncArg_SETCONTEXT {
  Key: ReadOnlyPropVar
  Value: ReadOnlyPropVar
}

export interface FuncArg_ADDITEM {
  DstPath: VBindProp
  ItemKey: ReadOnlyPropVar
  ItemValue: any
}

export interface FuncArg_REMOVEITEM {
  DstPath: VBindProp
  ItemKey: ReadOnlyPropVar
}

export interface FuncArg_APPENDITEM {
  DstPath: VBindProp
  ItemValue: any
  Position: InsertPos
}

export interface FuncArg_ADDPAYLOAD {
  Payload: VFNodeContentData
  PayloadId?: ReadOnlyPropVar
  Position: InsertPos
}

export interface FuncArg_REMOVEPAYLOAD {
  PayloadId: ReadOnlyPropVar
}

export interface FuncArg_ADDRESULT {
  Result: VFNodeContentData
  ResultId?: ReadOnlyPropVar
  Position: InsertPos
}

export interface FuncArg_REMOVERESULT {
  ResultId: ReadOnlyPropVar
}

export interface FuncArg_ADDRESULT2OUT {
  Result: VFNodeContentData
  HandleId: ReadOnlyPropVar
  Position: InsertPos
  ResultId?: ReadOnlyPropVar
  DataId?: ReadOnlyPropVar
}

export interface FuncArg_REMOVERESULT4OUT {
  ResultId: ReadOnlyPropVar
}

export interface FuncArg_ADDHANDLE {
  HandleType: VFNodeConnectionType
  HandleId: ReadOnlyPropVar
  Position: InsertPos
  HandleLabel?: ReadOnlyPropVar
}

export interface FuncArg_REMOVEHANDLE {
  HandleType: VFNodeConnectionType
  HandleId: ReadOnlyPropVar
}

export interface FuncArg_ADDHANDLEDATA {
  HandleType: VFNodeConnectionType
  HandleId: ReadOnlyPropVar
  Data: VFNodeHandleData
  DataId?: ReadOnlyPropVar
}

export interface FuncArg_REMOVEHANDLEDATA {
  HandleType: VFNodeConnectionType
  HandleId: ReadOnlyPropVar
  DataId: ReadOnlyPropVar
}

export interface FuncArg_OPENEDITOR {
  Language: CodeEditorLanguage
  DstPath: VBindProp
}

export interface FuncArg_FORMATSTRING {
  FString: string
  Args: Record<string, ReadOnlyPropVar>
}

// 函数属性基类
export interface _FuncPropBase {
  Func: FunctionPropType
  Arg: any
}

// 特定函数类型接口
export interface SETCONTEXT_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.SETCONTEXT
  Arg: FuncArg_SETCONTEXT
}

export interface ADDITEM_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.ADDITEM
  Arg: FuncArg_ADDITEM
}

export interface REMOVEITEM_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.REMOVEITEM
  Arg: FuncArg_REMOVEITEM
}

export interface APPENDITEM_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.APPENDITEM
  Arg: FuncArg_APPENDITEM
}

export interface ADDPAYLOAD_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.ADDPAYLOAD
  Arg: FuncArg_ADDPAYLOAD
}

export interface REMOVEPAYLOAD_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.REMOVEPAYLOAD
  Arg: FuncArg_REMOVEPAYLOAD
}

export interface ADDRESULT_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.ADDRESULT
  Arg: FuncArg_ADDRESULT
}
export interface REMOVERESULT_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.REMOVERESULT
  Arg: FuncArg_REMOVERESULT
}

export interface ADDRESULT2OUT_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.ADDRESULT2OUT
  Arg: FuncArg_ADDRESULT2OUT
}

export interface REMOVERESULT4OUT_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.REMOVERESULT4OUT
  Arg: FuncArg_REMOVERESULT4OUT
}

export interface ADDHANDLE_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.ADDHANDLE
  Arg: FuncArg_ADDHANDLE
}

export interface REMOVEHANDLE_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.REMOVEHANDLE
  Arg: FuncArg_REMOVEHANDLE
}

export interface ADDHANDLEDATA_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.ADDHANDLEDATA
  Arg: FuncArg_ADDHANDLEDATA
}

export interface REMOVEHANDLEDATA_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.REMOVEHANDLEDATA
  Arg: FuncArg_REMOVEHANDLEDATA
}

export interface UPDATENODEINTERNAL_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.UPDATENODEINTERNAL
  Arg: any
}

export interface OPENEDITOR_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.OPENEDITOR
  Arg: FuncArg_OPENEDITOR
}

export interface UPLOADIMAGE_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.UPLOADIMAGE
  Arg: null
}

export interface GENERATEUUID_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.GENERATEUUID
  Arg: null
}
export interface FORMATSTRING_FuncProp extends _FuncPropBase {
  Func: FunctionPropType.FORMATSTRING
  Arg: FuncArg_FORMATSTRING
}
// 单个函数属性联合类型
export type Operate_FuncProps =
  | SETCONTEXT_FuncProp
  | ADDITEM_FuncProp
  | REMOVEITEM_FuncProp
  | APPENDITEM_FuncProp
  | ADDPAYLOAD_FuncProp
  | REMOVEPAYLOAD_FuncProp
  | ADDRESULT_FuncProp
  | REMOVERESULT_FuncProp
  | ADDRESULT2OUT_FuncProp
  | REMOVERESULT4OUT_FuncProp
  | ADDHANDLE_FuncProp
  | REMOVEHANDLE_FuncProp
  | ADDHANDLEDATA_FuncProp
  | REMOVEHANDLEDATA_FuncProp
  | UPDATENODEINTERNAL_FuncProp
  | OPENEDITOR_FuncProp
export type Return_FuncProps = GENERATEUUID_FuncProp | FORMATSTRING_FuncProp
export type AsyncReturn_FuncProps = UPLOADIMAGE_FuncProp
// 函数属性接口
export interface OperateFunctionProp extends PropVarBase {
  FA_Type__: PropVarType.OperateFunc
  FA_Funcs__: Operate_FuncProps[]
}
export interface ReturnFunctionProp extends PropVarBase {
  FA_Type__: PropVarType.ReturnFunc
  FA_Func__: Return_FuncProps
}
export interface AsyncReturnFunctionProp extends PropVarBase {
  FA_Type__: PropVarType.AReturnFunc
  FA_Func__: AsyncReturn_FuncProps
}

export type PropVar =
  | ValueProp
  | VBindProp
  | VModelProp
  | OperateFunctionProp
  | ReturnFunctionProp
  | AsyncReturnFunctionProp
export type ReadOnlyPropVar = ValueProp | VBindProp | ReturnFunctionProp | AsyncReturnFunctionProp
export type BaseComponent = NormalComponent | SpanComponent | ForLoopComponent

// 使用 zod 进行类型验证
export const ValuePropSchema = z
  .object({
    FA_Type__: z.enum([PropVarType.Value]),
    FA_Data__: z.any(),
  })
  .strict()
export const VBindPropSchema = z
  .object({
    FA_Type__: z.enum([PropVarType.VBind]),
    FA_Data__: z.array(z.any()),
    FA_Replace__: z.string().nullable().optional(),
  })
  .strict()
export const VModelPropSchema = z
  .object({
    FA_Type__: z.enum([PropVarType.VModel]),
    FA_Data__: z.array(z.any()),
  })
  .strict()
export const VOpFuncPropSchema = z
  .object({
    FA_Type__: z.enum([PropVarType.OperateFunc]),
    FA_Funcs__: z.array(z.any()),
  })
  .strict()
export const VRetFuncPropSchema = z
  .object({
    FA_Type__: z.enum([PropVarType.ReturnFunc]),
    FA_Func__: z.any(),
  })
  .strict()
export const VARetFuncPropSchema = z
  .object({
    FA_Type__: z.enum([PropVarType.AReturnFunc]),
    FA_Func__: z.any(),
  })
  .strict()

// 普通组件类型
export interface NormalComponent {
  Type: string
  Props?: Record<string, PropVar>
  Slots?: Record<string, BaseComponent | BaseComponent[]>
  IfCondition?: Condition
}

// span绑定组件（@VSPAN@）
export interface SpanComponent {
  Type: typeof TYPE_VSPAN
  Data: ReadOnlyPropVar
  IfCondition?: Condition
  Replace?: string
  // 特殊绑定组件不允许有子组件
  Slots?: never
  Props?: never
  Items?: never
  Template?: never
}

// 循环组件 (@VFOR@)
export interface ForLoopComponent {
  Type: typeof TYPE_VFOR
  Items: ReadOnlyPropVar
  ItemLabel: string
  IndexLabel: string
  Template: BaseComponent | BaseComponent[]
  IfCondition?: Condition
  // 特殊绑定组件不允许有子组件
  Slots?: never
  Props?: never
}

// 条件判断系统
export type Condition = CompareCondition | LogicalCondition | DirectCondition

// 直接条件（修改为与Python模型一致的结构）
export interface DirectCondition {
  Type: typeof TYPE_CONDITION_DIRECT
  Condition: ReadOnlyPropVar
}

// 比较条件
export interface CompareCondition {
  Type: typeof TYPE_CONDITION_COMPARE
  Left: ReadOnlyPropVar
  Operator: '==' | '!=' | '>' | '<' | '>=' | '<='
  Right: ReadOnlyPropVar
}

// 逻辑组合条件
export interface LogicalCondition {
  Type: typeof TYPE_CONDITION_LOGICAL
  Operator: 'AND' | 'OR'
  Conditions: Condition[]
}

// 插件系统
export interface VFPluginSetting {
  Execute: string
}

export interface VFPlugin {
  Type: string
  Name: string
  Label: string
  Description: string
  Execute: string
  Setting: VFPluginSetting
  CreateInfo: any
  NeedOptions: any
}

export interface VFUIPlugin {
  Type: string
  Name: string
  Component: BaseComponent
}

export interface VFProvider {
  Provider: string
  Label: string
  Version: string
  Description: string
  Author: string
  Icon?: string
  ProviderSetting: VFPluginSetting
  Plugins: VFPlugin[]
  UIPlugins: VFUIPlugin[]
}
