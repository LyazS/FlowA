import { type AllVariableTypes } from './select_schemas'
import { type SelectOption } from 'naive-ui'

const _LengthTypeSelections = [
  { label: '长度等于', value: 'len_eq' },
  { label: '长度不等于', value: 'len_ne' },
  { label: '长度大于', value: 'len_gt' },
  { label: '长度大于等于', value: 'len_gte' },
  { label: '长度小于', value: 'len_lt' },
  { label: '长度小于等于', value: 'len_lte' },
] as const satisfies readonly SelectOption[]

const _StartEndTypeSelections = [
  { label: '开头是', value: 'startwith' },
  { label: '结尾是', value: 'endwith' },
] as const satisfies readonly SelectOption[]

const _NullTypeSelections = [
  { label: '为空', value: 'isnull' },
  { label: '不为空', value: 'notnull' },
] as const satisfies readonly SelectOption[]

const _EqualTypeSelections = [
  { label: '等于', value: 'eq' },
  { label: '不等于', value: 'ne' },
] as const satisfies readonly SelectOption[]

const _NotEuqalTypeSelections = [
  { label: '大于', value: 'gt' },
  { label: '大于等于', value: 'gte' },
  { label: '小于', value: 'lt' },
  { label: '小于等于', value: 'lte' },
] as const satisfies readonly SelectOption[]

const _ContainsTypeSelections = [
  { label: '包含', value: 'contains' },
  { label: '不包含', value: 'notcontains' },
] as const satisfies readonly SelectOption[]

const _BooleanTypeSelections = [
  { label: '为true', value: 'istrue' },
  { label: '为false', value: 'isfalse' },
] as const satisfies readonly SelectOption[]

export const LengthTypeSelections = [..._LengthTypeSelections] as SelectOption[]
export const StartEndTypeSelections = [..._StartEndTypeSelections] as SelectOption[]
export const NullTypeSelections = [..._NullTypeSelections] as SelectOption[]
export const EqualTypeSelections = [..._EqualTypeSelections] as SelectOption[]
export const NotEuqalTypeSelections = [..._NotEuqalTypeSelections] as SelectOption[]
export const ContainsTypeSelections = [..._ContainsTypeSelections] as SelectOption[]
export const BooleanTypeSelections = [..._BooleanTypeSelections] as SelectOption[]

const _CondTypeSelections = [
  ..._LengthTypeSelections,
  ..._StartEndTypeSelections,
  ..._NullTypeSelections,
  ..._EqualTypeSelections,
  ..._NotEuqalTypeSelections,
  ..._ContainsTypeSelections,
  ..._BooleanTypeSelections,
] as const satisfies readonly SelectOption[]

export type CompareOpType = (typeof _CondTypeSelections)[number]['value']

export interface CondBranchData {
  refdata: string
  operator: CompareOpType
  comparetype: AllVariableTypes
  value: string
}

export interface CondBranchDict {
  label: string
  data: {
    condType: string
    conditions: CondBranchData[]
  }
}
