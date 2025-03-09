import re
import base64
import json
import subprocess

with open(
    "app/nodes/configs/python code template.py",
    "r",
    encoding="utf-8",
) as f:
    code_string = f.read()
main_code = """
def main(arg1, arg2):
    print("Hello, world!")
    a=1/0
    return arg1 + arg2
"""
input_string = json.dumps({"arg1": 1, "arg2": 2}, ensure_ascii=False)
input_string_b64 = base64.b64encode(input_string.encode("utf-8")).decode("utf-8")

code_string = code_string.replace("@{CODEPYTHON}-FUNCTION-main", main_code).replace(
    "@{CODEINPUT}-BASE64-string", input_string_b64
)
result = subprocess.run(
    ["python", "-Xfrozen_modules=off", "-c", code_string],
    capture_output=True,
    text=True,
)

stdout = result.stdout
stderr = result.stderr
if len(stdout) <= 0:
    print("代码格式问题:\n", stderr)

pattern = r"@CODEOUTPUT-START(.*?)@CODEOUTPUT-END"
output_result = re.findall(pattern, stdout, re.S)
if len(output_result) > 0:
    output_type, res = output_result[0].strip().split("\n", 1)
    if output_type == "@CODEOUTPUT-BASE64":
        json_string = base64.b64decode(res).decode("utf-8")
        res_json = json.loads(json_string)
        print("结果:\n", res_json)
        pass
    elif output_type == "@CODEOUTPUT-ERROR":
        print("出错:\n", res)
