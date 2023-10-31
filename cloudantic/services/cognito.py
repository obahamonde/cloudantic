import os

from dotenv import load_dotenv  # type: ignore

load_dotenv()
from boto3 import client  # type: ignore
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from ..utils import async_io, handle  # type: ignore

cognito = client("cognito-idp", region_name="us-east-1")


class SignUpResponse(BaseModel):
    user_sub: str
    user_confirmed: bool


class ConfirmSignUpResponse(BaseModel):
    status: str


class SignInResponse(BaseModel):
    access_token: str
    id_token: str
    refresh_token: str


class SignOutResponse(BaseModel):
    status: str


class ChangePasswordResponse(BaseModel):
    status: str


class ForgotPasswordResponse(BaseModel):
    code_delivery_details: str


class ConfirmForgotPasswordResponse(BaseModel):
    status: str


class CognitoClient(BaseModel):
    user_pool_id: str = Field(
        description="The ID of the Cognito User Pool",
        default=os.environ.get("USER_POOL_ID"),
    )
    client_id: str = Field(
        description="The ID of the Cognito User Pool Client",
        default=os.environ.get("USERPOOL_CLIENT_ID"),
    )

    @handle
    @async_io
    def sign_up(self, username: str, password: str) -> SignUpResponse:
        response = cognito.sign_up(
            ClientId=self.client_id,
            Username=username,
            Password=password,
        )
        return SignUpResponse(
            user_sub=response["UserSub"], user_confirmed=response["UserConfirmed"]
        )

    @handle
    @async_io
    def confirm_sign_up(
        self, username: str, confirmation_code: str
    ) -> ConfirmSignUpResponse:
        cognito.confirm_sign_up(
            ClientId=self.client_id,
            Username=username,
            ConfirmationCode=confirmation_code,
        )
        return ConfirmSignUpResponse(status="Confirmed")

    @handle
    @async_io
    def sign_in(self, username: str, password: str) -> SignInResponse:
        response = cognito.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
        )
        return SignInResponse(
            access_token=response["AuthenticationResult"]["AccessToken"],
            id_token=response["AuthenticationResult"]["IdToken"],
            refresh_token=response["AuthenticationResult"]["RefreshToken"],
        )

    @handle
    @async_io
    def sign_out(self, access_token: str) -> SignOutResponse:
        cognito.global_sign_out(AccessToken=access_token)
        return SignOutResponse(status="Signed out")

    @handle
    @async_io
    def change_password(
        self, previous_password: str, proposed_password: str, access_token: str
    ) -> ChangePasswordResponse:
        cognito.change_password(
            PreviousPassword=previous_password,
            ProposedPassword=proposed_password,
            AccessToken=access_token,
        )
        return ChangePasswordResponse(status="Password changed")

    @handle
    @async_io
    def forgot_password(self, username: str) -> ForgotPasswordResponse:
        response = cognito.forgot_password(
            ClientId=self.client_id,
            Username=username,
        )
        return ForgotPasswordResponse(
            code_delivery_details=response["CodeDeliveryDetails"]["Destination"]
        )

    @handle
    @async_io
    def confirm_forgot_password(
        self, username: str, confirmation_code: str, new_password: str
    ) -> ConfirmForgotPasswordResponse:
        cognito.confirm_forgot_password(
            ClientId=self.client_id,
            Username=username,
            ConfirmationCode=confirmation_code,
            Password=new_password,
        )
        return ConfirmForgotPasswordResponse(status="Password reset")

    @handle
    @async_io
    def get_user(self, access_token: str) -> dict[str, str]:
        response = cognito.get_user(AccessToken=access_token)
        return response["UserAttributes"]
