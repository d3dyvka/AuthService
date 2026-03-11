from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self) -> None:
        errors = []
        if len(self.value) < 8:
            errors.append("Пароль не может быть меньше 8 символов")
        if not any(c.isdigit() for c in self.value):
            errors.append("Пароль должен содержать хотя бы 1 число")
        if not any(c.isalpha() for c in self.value):
            errors.append("Пароль должен содержать хотя бы 1 букву")
        if errors:
            raise ValueError("; ".join(errors))

    def __str__(self) -> str:
        return str(self.value)