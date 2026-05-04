# Модуль AI-движка

from app.core.models import TransformRequest, TransformResponse


class AIEngine:
    """Связывает prompt и LLM"""

    def __init__(self, prompt_builder, llm_client):
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def transform(self, request: TransformRequest) -> TransformResponse:
        # 1. анализ текста
        analyze_prompt = self.prompt_builder.build_analyze_prompt(request.text)
        analysis = self.llm_client.generate(analyze_prompt)

        # 2. трансформация
        transform_prompt = self.prompt_builder.build_transform_prompt(request)
        result = self.llm_client.generate(transform_prompt)

        # 3. парсинг результата
        parts = result.split("2. Нейтральная версия:")
        adapted = parts[0].replace("1. Адаптированный текст:", "").strip()

        rest = parts[1].split("3. Объяснение:")
        neutral = rest[0].strip()
        explanation = rest[1].strip()

        return TransformResponse(
            adapted_text=adapted,
            neutral_text=neutral,
            explanation=explanation + "\n\n📊 Анализ:\n" + analysis
        )
