from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from detector.issues import detect_issues
from refactor.fixer import refactor_code
from tester.tester import test_code
from utils.rollback import save_backup

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeInput(BaseModel):
    code: str


def detect_language(code):
    if "#include" in code:
        return "C/C++"
    elif "public class" in code:
        return "Java"
    else:
        return "Python"


def highlight_changes(old, new):
    old_lines = old.split("\n")
    new_lines = new.split("\n")
    result = []

    for i in range(max(len(old_lines), len(new_lines))):
        o = old_lines[i] if i < len(old_lines) else ""
        n = new_lines[i] if i < len(new_lines) else ""

        if o != n:
            result.append(f"❌ {o}\n✅ {n}")

    return result


@app.post("/analyze/")
def analyze(input: CodeInput):
    try:
        issues = detect_issues(input.code)
        language = detect_language(input.code)
        score = max(0, 100 - len(issues) * 10)

        return {
            "issues": issues,
            "language": language,
            "score": score
        }
    except Exception as e:
        return {"issues": [], "error": str(e)}


@app.post("/refactor/")
def refactor(input: CodeInput):
    try:
        save_backup(input.code)

        new_code = refactor_code(input.code)
        if not new_code:
            new_code = input.code

        test_result = test_code(input.code, new_code)
        changes = highlight_changes(input.code, new_code)

        return {
            "refactored_code": new_code,
            "test_passed": test_result,
            "changes": changes
        }

    except Exception as e:
        return {
            "refactored_code": input.code,
            "test_passed": False,
            "changes": [],
            "error": str(e)
        }
    try:
        save_backup(input.code)

        new_code = refactor_code(input.code)
        if not new_code:
            new_code = input.code

        test_result = test_code(input.code, new_code)
        changes = highlight_changes(input.code, new_code)

        return {
            "refactored_code": new_code,
            "test_passed": test_result,
            "changes": changes
        }

    except Exception as e:
        return {
            "refactored_code": input.code,
            "test_passed": False,
            "changes": [],
            "error": str(e)
        }