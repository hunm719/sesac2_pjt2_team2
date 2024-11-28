from sqlmodel import SQLModel, Field

class Admin(SQLModel, table=True):

    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(..., max_length=20)
    user_password: str = Field(...)
    # role: str

class AdminSignUp(SQLModel):
    user_id: str
    user_password: str
