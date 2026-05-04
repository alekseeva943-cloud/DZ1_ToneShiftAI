
from dataclasses import dataclass
from typing import Optional


@dataclass
class TransformRequest:
    """
    Модель запроса на трансформацию текста.

    Поля:
    text: исходный текст для обработки
    goal: цель трансформации (например, "увеличить вовлеченность")
    audience: целевая аудитория
    tone: желаемый тон текста (например, "дружелюбный")
    formality: уровень формальности текста (необязательно)
    length: желаемая длина текста (необязательно)
    """
    text: str
    goal: str
    audience: str
    tone: str
    formality: Optional[str] = None
    length: Optional[str] = None


@dataclass
class TransformResponse:
    """
    Модель ответа после трансформации текста.

    Поля:
    adapted_text: адаптированный текст согласно параметрам запроса
    neutral_text: нейтральная версия текста без стилистических изменений
    explanation: объяснение, что было изменено и почему
    """
    adapted_text: str
    neutral_text: str
    explanation: str
