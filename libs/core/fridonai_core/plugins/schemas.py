from pydantic import BaseModel


class BaseToolInput(BaseModel):
    @classmethod
    def class_parameters_as_string(cls) -> str:
        explanation = []
        for field_name, field_info in cls.model_fields.items():
            description = field_info.description or ""
            explanation.append(f"{field_name} - {description}")
        return "\n".join(explanation)