import requests 


url = "https://api.onlinecompiler.io"
token = "175b56114db75925eec8517c098ec0e2"


def get_language_code(language: str) -> str:
    mapping = {
        "python": "python-3.14",
        "javascript": "nodejs-20",
        "typescript": "typescript-5.0",
        "c": "c-11",
        "cpp": "cpp-17",
        "java": "java-17"
    }

    return mapping.get(language.lower(), "python-3.14")  # default





def run_code(code: str, input_data: str = "", language: str = "python"):
    compiler = get_language_code(language)

    response = requests.post(
        "https://api.onlinecompiler.io/api/run-code-sync/",
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
        },
        json={
            "compiler": compiler,
            "code": code,
            "input": input_data,
        },
    )

    result = response.json()
    return {
        "output": result.get("stdout") or result.get("output") or "",
        "error": result.get("stderr") or result.get("compile_output") or "",
    }