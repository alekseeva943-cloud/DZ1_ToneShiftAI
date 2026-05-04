from app.core.models import TransformRequest


class PromptBuilder:
    def load_prompt(self, filename: str) -> str:
        with open(f"app/prompts/{filename}", "r", encoding="utf-8") as file:
            return file.read()

    def build_transform_prompt(self, request: TransformRequest) -> str:
        template = self.load_prompt("transform.txt")

        return template.format(
            goal=request.goal,
            audience=request.audience,
            tone=request.tone,
            text=request.text
        )

    def build_analyze_prompt(self, text: str) -> str:
        template = self.load_prompt("analyze.txt")
        return template.format(text=text)
