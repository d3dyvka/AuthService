from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self) -> None:
        errors = []
        if len(self.value) < 8:
            errors.append("Password must be at least 8 characters")
        if not any(c.isdigit() for c in self.value):
            errors.append("Password must contain at least one digit")
        if not any(c.isalpha() for c in self.value):
            errors.append("Password must contain at least one letter")
        if errors:
            raise ValueError("; ".join(errors))

    def __str__(self) -> str:
        return str(self.value)