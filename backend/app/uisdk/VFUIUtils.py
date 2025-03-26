from app.uisdk.VFUISchemas import PropVar, ValueProp, PropVarType


def cvtProps2PropVar(props: dict):
    result_props = {}
    for key, value in props.items():
        if not isinstance(value, PropVar):
            result_props[key] = ValueProp(Data=value)
        else:
            result_props[key] = value
    return result_props
