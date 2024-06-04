from pydantic.v1 import BaseModel


class BaseToolInput(BaseModel):
    def parameters_as_string(self) -> str:
        explanation = []
        for field_name, field_info in self.__fields__.items():
            field_type = field_info.type_
            description = field_info.field_info.description or "No description"
            explanation.append(f"{field_name} ({field_type.__name__}) - {description}")
        return "\n".join(explanation)