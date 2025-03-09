from typing import Any, List, Dict, Union
import copy
from enum import Enum
import asyncio
from pydantic_core import core_schema
from typing_extensions import Annotated
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue


class RefOptions(Enum):
    set = "set"
    setitem = "setitem"
    delitem = "delitem"
    append = "append"
    pop = "pop"
    pass


class RefTriggerData(BaseModel):
    path: List[Union[str, int]]
    operation: RefOptions
    new_value: Any
    old_value: Any
    pass


class Ref:
    def __init__(self, value):
        self._dependencies = set()  # 初始化 _dependencies
        self._value = self._wrap_value(
            value,
            lambda triggerdata: self._trigger(triggerdata),
        )

    def __deepcopy__(self, memo):
        # 创建一个新的 Ref 实例，复制 _value 但不复制 _dependencies
        new_instance = self.__class__(copy.deepcopy(self._value, memo))
        # 如果需要，可以在这里复制其他属性
        return new_instance

    def _wrap_value(self, value, trigger):
        # 如果是列表或字典，包装为响应式对象
        if isinstance(value, list):
            return ReactiveList(value, trigger)
        elif isinstance(value, dict):
            return ReactiveDict(value, trigger)
        elif isinstance(value, Ref):
            value.add_dependency(trigger)
            return value
        else:
            return value

    @property
    def value(self):
        self._track()
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            old_value = self._value
            self._value = self._wrap_value(
                new_value,
                lambda triggerdata: self._trigger(triggerdata),
            )
            self._trigger(
                RefTriggerData(
                    path=[],
                    operation=RefOptions.set,
                    new_value=new_value,
                    old_value=old_value,
                )
            )

    def _track(self):
        # 模拟依赖收集
        # print("Tracking dependency...")
        pass

    def _trigger(self, triggerdata: RefTriggerData):
        # 触发所有依赖回调，并传递路径、操作类型、新值和旧值
        for callback in self._dependencies:
            callback(triggerdata)

    def add_dependency(self, callback):
        # 添加依赖回调
        self._dependencies.add(callback)

    def __repr__(self):
        return self._value.__repr__()


class ReactiveDict(dict):
    def __init__(self, mapping, trigger_callback):
        super().__init__(mapping)
        self._trigger_callback = trigger_callback
        # 将嵌套的字典或列表转换为响应式对象
        for key, value in self.items():
            v = self._wrap_value(
                value,
                lambda triggerdata, key=key: self._trigger_callback(
                    RefTriggerData(
                        path=[key] + triggerdata.path,
                        operation=triggerdata.operation,
                        new_value=triggerdata.new_value,
                        old_value=triggerdata.old_value,
                    )
                ),
            )
            super().__setitem__(key, v)

    def _wrap_value(self, value, trigger):
        # 如果是列表或字典，包装为响应式对象
        if isinstance(value, list):
            return ReactiveList(value, trigger)
        elif isinstance(value, dict):
            return ReactiveDict(value, trigger)
        elif isinstance(value, Ref):
            value.add_dependency(trigger)
            return value
        else:
            return value

    def __setitem__(self, key, value):
        old_value = self.get(key)
        value = self._wrap_value(
            value,
            lambda triggerdata, key=key: self._trigger_callback(
                RefTriggerData(
                    path=[key] + triggerdata.path,
                    operation=triggerdata.operation,
                    new_value=triggerdata.new_value,
                    old_value=triggerdata.old_value,
                )
            ),
        )
        super().__setitem__(key, value)
        self._trigger_callback(
            RefTriggerData(
                path=[key],
                operation=RefOptions.setitem,
                new_value=value,
                old_value=old_value,
            )
        )  # 传递路径、操作类型、新值和旧值

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(result, Ref):
            return result.value
        return result

    def __delitem__(self, key):
        old_value = self.get(key)
        super().__delitem__(key)
        self._trigger_callback(
            RefTriggerData(
                path=[key],
                operation=RefOptions.delitem,
                new_value=None,
                old_value=old_value,
            )
        )  # 传递路径、操作类型、新值和旧值


class ReactiveList(list):
    def __init__(self, iterable, trigger_callback):
        super().__init__(iterable)
        self._trigger_callback = trigger_callback
        # 将嵌套的字典或列表转换为响应式对象
        for i, item in enumerate(self):
            v = self._wrap_value(
                item,
                lambda triggerdata, i=i: self._trigger_callback(
                    RefTriggerData(
                        path=[i] + triggerdata.path,
                        operation=triggerdata.operation,
                        new_value=triggerdata.new_value,
                        old_value=triggerdata.old_value,
                    )
                ),
            )
            super().__setitem__(i, v)

    def _wrap_value(self, value, trigger):
        # 如果是列表或字典，包装为响应式对象
        if isinstance(value, list):
            return ReactiveList(value, trigger)
        elif isinstance(value, dict):
            return ReactiveDict(value, trigger)
        elif isinstance(value, Ref):
            value.add_dependency(trigger)
            return value
        else:
            return value

    def __setitem__(self, key, value):
        old_value = self[key]
        value = self._wrap_value(
            value,
            lambda triggerdata, key=key: self._trigger_callback(
                RefTriggerData(
                    path=[key] + triggerdata.path,
                    operation=triggerdata.operation,
                    new_value=triggerdata.new_value,
                    old_value=triggerdata.old_value,
                )
            ),
        )
        super().__setitem__(key, value)
        self._trigger_callback(
            RefTriggerData(
                path=[key],
                operation=RefOptions.setitem,
                new_value=value,
                old_value=old_value,
            )
        )  # 传递路径、操作类型、新值和旧值

    def __getitem__(self, key):
        result = super().__getitem__(key)
        if isinstance(result, Ref):
            return result.value
        return result

    def __delitem__(self, key):
        old_value = self[key]
        super().__delitem__(key)
        self._trigger_callback(
            RefTriggerData(
                path=[key],
                operation=RefOptions.delitem,
                new_value=None,
                old_value=old_value,
            )
        )  # 传递路径、操作类型、新值和旧值

    def append(self, value):
        nowlen = len(self)
        value = self._wrap_value(
            value,
            lambda triggerdata, nowlen=nowlen: self._trigger_callback(
                RefTriggerData(
                    path=[nowlen] + triggerdata.path,
                    operation=triggerdata.operation,
                    new_value=triggerdata.new_value,
                    old_value=triggerdata.old_value,
                )
            ),
        )
        super().append(value)
        self._trigger_callback(
            RefTriggerData(
                path=[],
                operation=RefOptions.append,
                new_value=value,
                old_value=None,
            )
        )  # 路径只到列表本身

    def pop(self, index=-1):
        old_value = self[index]
        result = super().pop(index)
        self._trigger_callback(
            RefTriggerData(
                path=[],
                operation=RefOptions.pop,
                new_value=None,
                old_value=old_value,
            )
        )  # 路径只到列表本身

        return result


# Pydantic ===============================================


def serialize_ref(value):
    if isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, list):
        return [serialize_ref(item) for item in value]
    elif isinstance(value, dict):
        return {key: serialize_ref(val) for key, val in value.items()}
    elif isinstance(value, Ref):
        return serialize_ref(value.value)
    else:
        return str(value)  # 默认转换为字符串


class _RefTypePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:

        def validate_from_any(value: Any) -> Ref:
            result = Ref(value)
            return result

        from_any_schema = core_schema.no_info_plain_validator_function(
            validate_from_any
        )

        # def serialize_value(value):
        #     if isinstance(value, (str, int, float, bool)):
        #         return value
        #     elif isinstance(value, list):
        #         return [serialize_value(item) for item in value]
        #     elif isinstance(value, dict):
        #         return {key: serialize_value(val) for key, val in value.items()}
        #     elif isinstance(value, Ref):
        #         return serialize_value(value.value)
        #     else:
        #         return str(value)  # 默认转换为字符串

        return core_schema.json_or_python_schema(
            json_schema=from_any_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(Ref),
                    from_any_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: serialize_ref(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.any_schema())


RefType = Annotated[Ref, _RefTypePydanticAnnotation]
# ========================================================


# 运行所有测试
if __name__ == "__main__":

    def update_callback(triggerdata: RefTriggerData):
        print(f"Update detected at path: {triggerdata.path}")
        print(f"Operation: {triggerdata.operation}")
        print(f"New value: {triggerdata.new_value}")
        print(f"Old value: {triggerdata.old_value}")
        print("------")

    # 测试 1: 基本类型（整数）
    def test_primitive():
        print("=== 测试 1: 基本类型（整数） ===")
        count = Ref(0)
        count.add_dependency(update_callback)
        count.value = 1
        count.value += 1
        print()

    # 测试 2: 基本类型（字符串）
    def test_string():
        print("=== 测试 2: 基本类型（字符串） ===")
        name = Ref("Alice")
        name.add_dependency(update_callback)
        name.value = "Bob"
        name.value += " Smith"
        print()

    # 测试 3: 列表（嵌套基本类型）
    def test_list_with_primitives():
        print("=== 测试 3: 列表（嵌套基本类型） ===")
        items = Ref([1, 2, 3])
        items.add_dependency(update_callback)
        items.value.append(4)
        items.value[0] = 10
        items.value.pop()
        print("len: ", len(items.value))
        print()

    # 测试 4: 字典（嵌套基本类型）
    def test_dict_with_primitives():
        print("=== 测试 4: 字典（嵌套基本类型） ===")
        user = Ref({"name": "Alice", "age": 25})
        user.add_dependency(update_callback)
        user.value["age"] = 26
        user.value["city"] = "New York"
        user.value["name"] += " Smith"
        del user.value["city"]

        print()

    # 测试 5: 列表（嵌套字典）
    def test_list_with_dict():
        print("=== 测试 5: 列表（嵌套字典） ===")
        items = Ref([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])
        items.add_dependency(update_callback)
        items.value[0]["age"] += 1
        items.value.append({"name": "Charlie", "age": 35})
        items.value.append([])
        items.value[3].append({"name": "Dave", "age": 40})
        items.value[3][0]["age"] += 1
        print("len: ", len(items.value))
        print()

    # 测试 6: 字典（嵌套列表）
    def test_dict_with_list():
        print("=== 测试 6: 字典（嵌套列表） ===")
        user = Ref({"name": "Alice", "scores": [80, 90, 85]})
        user.add_dependency(update_callback)
        user.value["scores"].append(95)
        user.value["scores"][0] = 100
        print()

    # 测试 7: 复杂嵌套（字典中嵌套列表，列表中嵌套字典）
    def test_complex_nesting():
        print("=== 测试 7: 复杂嵌套（字典中嵌套列表，列表中嵌套字典） ===")
        data = Ref(
            {
                "users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}],
                "metadata": {"total": 2, "timestamp": "2023-10-01"},
            }
        )
        data.add_dependency(update_callback)
        data.value["users"][0]["age"] += 1
        data.value["metadata"]["total"] += 1
        data.value["users"].append({"name": "Charlie", "age": 35})
        print()

    def test_reset():
        print("=== 测试 reset ===")
        data = Ref(
            {
                "users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}],
                "metadata": {"total": 2, "timestamp": "2023-10-01"},
            }
        )
        data.add_dependency(update_callback)
        data.value = [{"name": "Charlie", "age": 35}]
        print()

    def test_deepcopy():
        print("=== 测试 deepcopy ===")
        import copy

        data = Ref([1, 2, 3])
        data.value.append(4)
        data_copy = copy.deepcopy(data)
        data_copy.value.append(5)
        print(data.value)  # [1, 2, 3, 4]
        print(data_copy.value)  # [1, 2, 3, 4, 5]

    def test_pydantic():
        print("=== 测试 pydantic ===")
        from pydantic import BaseModel

        class User(BaseModel):
            name: RefType
            age: RefType
            friend: RefType

        bob = RefType({"name": "Bob", "age": 30})
        user = User(name="Alice", age=25, friend=[])
        user.name.add_dependency(update_callback)
        user.age.add_dependency(update_callback)
        user.friend.add_dependency(update_callback)
        user.age.value += 1
        user.name.value = None
        user.friend.value.append(bob)
        user.friend.value[0]["age"] += 1
        print(user.model_dump_json())

    def test_chain_nested_refs():
        print("=== 测试 chain_nested_refs ===")
        data = RefType(0)
        mat = RefType([])
        mat.add_dependency(
            lambda triggerdata: {
                print("mat", end=" "),
                update_callback(triggerdata),
            }
        )
        mat.value.append(data)
        mat2 = RefType({"a": []})
        mat2.add_dependency(
            lambda triggerdata: {
                print("mat2", end=" "),
                update_callback(triggerdata),
            }
        )
        mat2.value["a"].append(data)
        print(mat.value)
        print(mat2.value)
        data.value = 2
        print(mat.value)
        print(mat2.value)
        mat.value[0] = 3
        print(data)

    # ==================================================
    test_primitive()
    test_string()
    test_list_with_primitives()
    test_dict_with_primitives()
    test_list_with_dict()
    test_dict_with_list()
    test_complex_nesting()
    test_reset()
    test_deepcopy()
    test_pydantic()
    test_chain_nested_refs()
