import pytest
import jwt
from fastapi import HTTPException, status

from optipy.api.exceptions import BadRequestFromRaisedException
from optipy.config import settings

from ..auth0 import VerifyToken


@pytest.fixture
def verify_token():
    return VerifyToken()


class TestVerifyToken:

    def test_verify_valid_token(self, mocker, verify_token):
        key = "test_key"
        mock_jwks_client = mocker.MagicMock()
        mock_jwks_client.get_signing_key_from_jwt.return_value = mocker.MagicMock(
            key=key
        )
        verify_token.jwks_client = mock_jwks_client

        token = "valid_token"
        decoded_token = {"sub": "12345", "name": "John Doe"}

        mock_decode = mocker.MagicMock()
        mock_decode.return_value = decoded_token
        mocker.patch("jwt.decode", mock_decode)

        result = verify_token.verify(token)

        assert result == decoded_token
        mock_decode.assert_called_with(
            token,
            key,
            algorithms=settings.AUTH0_ALGORITHMS,
            audience=settings.AUTH0_API_AUDIENCE,
            issuer=settings.AUTH0_ISSUER
        )

    def test_verify_invalid_jwk_client(self, mocker, verify_token):
        mock_jwks_client = mocker.MagicMock()
        mock_jwks_client.get_signing_key_from_jwt.side_effect = jwt.exceptions.PyJWKClientError
        verify_token.jwks_client = mock_jwks_client

        token = "invalid_token"

        with pytest.raises(HTTPException) as exc_info:
            verify_token.verify(token)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "Error while trying to initialize JWK client."

    def test_verify_invalid_token(self, mocker, verify_token):
        mock_jwks_client = mocker.MagicMock()
        mock_jwks_client.get_signing_key_from_jwt.return_value = mocker.MagicMock()
        verify_token.jwks_client = mock_jwks_client

        token = "invalid_token"

        with pytest.raises(HTTPException) as exc_info:
            verify_token.verify(token)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert exc_info.value.detail == "Error decoding JWT token"

    def test_verify_generic_exception(self, mocker, verify_token):
        mock_jwks_client = mocker.MagicMock()
        mock_jwks_client.get_signing_key_from_jwt.return_value = mocker.MagicMock(
            key="dummy_key"
        )
        verify_token.jwks_client = mock_jwks_client

        token = "valid_token"
        exception_message = "Something went wrong"
        exception = Exception(exception_message)

        mock_decode = mocker.MagicMock(side_effect=exception)
        mocker.patch("jwt.decode", mock_decode)

        with pytest.raises(BadRequestFromRaisedException) as exc_info:
            verify_token.verify(token)
            assert str(exc_info.value) == exception_message
