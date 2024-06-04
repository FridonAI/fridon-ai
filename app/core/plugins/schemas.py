from pydantic.v1 import BaseModel


class BaseToolInput(BaseModel):
    @classmethod
    def class_parameters_as_string(cls) -> str:
        explanation = []
        for field_name, field_info in cls.__fields__.items():
            field_type = field_info.type_
            description = field_info.field_info.description or "No description"
            explanation.append(f"{field_name} ({field_type.__name__}) - {description}")
        return "\n".join(explanation)