from sqlmodel import SQLModel, Field

class AdminSignUp(SQLModel):
    admin_id: str
    admin_password: str
    email: str

class AdminSignIn(SQLModel):
    admin_id: str
    admin_password: str