from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyResetCodeRequest(BaseModel):
    email: EmailStr

    code: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )


class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(
        min_length=32,
        max_length=128,
    )

    new_password: str = Field(
        min_length=6,
        max_length=72,
    )

    confirm_password: str = Field(
        min_length=6,
        max_length=72,
    )


class PasswordResetResponse(BaseModel):
    message: str


class VerifyResetCodeResponse(BaseModel):
    message: str
    reset_token: str
