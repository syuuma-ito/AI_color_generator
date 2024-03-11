import google.ai.generativelanguage as glm
from rich.console import Console

from generate_color_code import generate_color_code

console = Console()

json_schema = {
    "title": "color code",
    "type": "object",
    "properties": {
        "color": {
            "type": "array",
            "description": "The color code",
            "items": {
                "type": "string",
                "pattern": "^#([\da-fA-F]{6}|[\da-fA-F]{3})$",
                "description": "The hexadecimal color code",
            },
            "minItems": 5,
            "maxItems": 5,
        },
    },
}


user_prompt = input(">>> ")

with console.status("Generating color code..."):
    res = generate_color_code(user_prompt, json_schema)
if res is None:
    print("生成に失敗しました。")
    exit()
color = res["color"]
console.rule()
for c in color:
    console.print(f"████████████████████████████████████", style=f"bold {c}", end=" ")
    console.print(f"({c})")
console.rule()
