from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class User:
    email: str
    password_hash: str
    name: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = False
    is_email_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: datetime | None = None

    def activate(self) -> None:
        self.is_active = True
        self.is_email_verified = True
        self.updated_at = datetime.utcnow()

    def update_last_login(self) -> None:
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_password(self, new_hash: str) -> None:
        self.password_hash = new_hash
        self.updated_at = datetime.utcnow()