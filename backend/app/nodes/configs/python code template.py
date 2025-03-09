@{CODEPYTHON}-FUNCTION-main
_CODEINPUT_b64 = "@{CODEINPUT}-BASE64-string"
class _CI_FUNC_WRAPPER:
    @staticmethod
    def _CI_B64TOJSON(base64_string):
        import base64
        import json

        json_string = base64.b64decode(base64_string).decode("utf-8")
        return json.loads(json_string)

    @staticmethod
    def _CI_JSONTOB64(json_obj):
        import base64
        import json

        json_string = json.dumps(json_obj)
        base64_string = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
        return base64_string




if __name__ == "__main__":
    import traceback

    try:
        _CI_CODEINPUT_DICT = _CI_FUNC_WRAPPER._CI_B64TOJSON(_CODEINPUT_b64)
        _CI_result = main(**_CI_CODEINPUT_DICT)
        _CI_result_b64 = _CI_FUNC_WRAPPER._CI_JSONTOB64(_CI_result)
        print("@CODEOUTPUT-START")
        print("@CODEOUTPUT-BASE64")
        print(_CI_result_b64)
        print("@CODEOUTPUT-END")
    except Exception as e:
        # 获取e的文件行数和报错信息
        error_message = traceback.format_exc()

        print("@CODEOUTPUT-START")
        print("@CODEOUTPUT-ERROR")
        print(error_message)
        print("@CODEOUTPUT-END")
