# car_diagnostics.py
import json
import re
import os

class CarDiagnostics:
    def __init__(self, file_path="car_problems.json"):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"car_problems.json not found at {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def find_problem(self, user_input: str):
        text = user_input.lower()
        for problem in self.data.get("emergencies", []):
            for keyword in problem["keywords"]:
                if re.search(rf"\b{re.escape(keyword)}\b", text):
                    return problem
        return None

    def get_response(self, user_input: str) -> str:
        problem = self.find_problem(user_input)
        if not problem:
            return (
                "I couldn’t find an exact match for that issue. "
                "Could you describe what seems wrong in more detail?"
            )

        name = problem["problem_name"]
        quick = problem["quick_solution"]
        safety = problem["safety_warning"]
        steps = "\n".join([f"- {step}" for step in problem["detailed_steps"]])

        return (
            f"🚨 **{name} Detected!**\n"
            f"**Quick Solution:** {quick}\n"
            f"**Safety Warning:** {safety}\n"
            f"**Detailed Steps:**\n{steps}"
        )
