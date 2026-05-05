# Модуль AI-движка
# Этот файл отвечает за:
# - сбор промптов (анализ + трансформация)
# - отправку запроса в LLM
# - обработку (парсинг) ответа модели
# - защиту от ошибок модели (кривой формат ответа)


from app.core.models import TransformRequest, TransformResponse


class AIEngine:
    """Связывает prompt_builder и LLM"""

    def __init__(self, prompt_builder, llm_client):
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def transform(self, request: TransformRequest) -> TransformResponse:
        """
        Основной метод:
        1. Анализирует текст
        2. Переписывает текст
        3. Разбирает ответ модели
        """

        # -------------------------------------------------
        # 🔹 1. Анализ текста
        # -------------------------------------------------
        try:
            analyze_prompt = self.prompt_builder.build_analyze_prompt(
                request.text)
            analysis = self.llm_client.generate(analyze_prompt)
        except Exception as e:
            print("🔥 ANALYZE ERROR:", e)
            analysis = "Не удалось выполнить анализ"

        # -------------------------------------------------
        # 🔹 2. Трансформация текста
        # -------------------------------------------------
        try:
            transform_prompt = self.prompt_builder.build_transform_prompt(
                request)
            result = self.llm_client.generate(transform_prompt)

        except Exception as e:
            print("🔥 LLM ERROR:", e)
            return TransformResponse(
                adapted_text="Ошибка генерации текста",
                neutral_text="Ошибка генерации",
                explanation="Модель не ответила корректно"
            )

        # -------------------------------------------------
        # 🔹 3. Парсинг ответа модели (САМОЕ УЯЗВИМОЕ МЕСТО)
        # -------------------------------------------------
        try:
            parts = result.split("2. Нейтральная версия:")
            adapted = parts[0].replace("1. Адаптированный текст:", "").strip()

            rest = parts[1].split("3. Объяснение:")
            neutral = rest[0].strip()
            explanation = rest[1].strip()

        except Exception as e:
            print("⚠️ PARSE ERROR:", e)
            print("RAW RESULT:\n", result)

            # fallback — если модель ответила криво
            adapted = result
            neutral = "Не удалось выделить нейтральную версию"
            explanation = "Модель вернула нестандартный формат ответа"

        # -------------------------------------------------
        # 🔹 4. Возвращаем результат
        # -------------------------------------------------
        return TransformResponse(
            adapted_text=adapted,
            neutral_text=neutral,
            explanation=explanation + "\n\n📊 Анализ:\n" + analysis
        )
