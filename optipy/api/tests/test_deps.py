import pytest
from pytest_mock import mocker

from fastapi import HTTPException, status, security

from optipy.auth import VerifyToken
from optipy.apps.users import models
from optipy.api.deps import (
    get_db,
    get_auth_token_sub,
    get_current_user,
    BadRequestFromRaisedException,
)


@pytest.fixture
def token_auth_scheme():
    return security.HTTPBearer()


@pytest.fixture
def token_verifier():
    return VerifyToken()


@pytest.fixture
def mock_db(mocker):
    return mocker.MagicMock()


def test_get_db(mock_db):
    # Assuming SessionLocal returns a MagicMock
    with pytest.raises(AttributeError):
        # Test that the session is closed at the end
        with next(get_db()) as db:
            assert isinstance(db, mocker.MagicMock)
            assert db == mock_db

        assert mock_db.close.called


def test_get_auth_token_sub_valid_token(mocker):
    mock_token = mocker.MagicMock()
    mock_token.credentials = "valid_token"

    mock_verify = mocker.MagicMock()
    mock_verify.return_value = {"sub": "12345"}

    mocker.patch.object(VerifyToken, 'verify', mock_verify)

    result = get_auth_token_sub(token=mock_token)

    assert result == "12345"
    mock_verify.assert_called_with("valid_token")


def test_get_auth_token_sub_invalid_token(mocker):
    mock_token = mocker.MagicMock()
    mock_token.credentials = "invalid_token"

    mock_verify = mocker.MagicMock(side_effect=Exception())
    mocker.patch.object(VerifyToken, "verify", mock_verify)

    with pytest.raises(HTTPException) as exc_info:
        get_auth_token_sub(token=mock_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Unauthorized. Token verification failed."


def test_get_auth_token_sub_missing_sub(mocker):
    mock_token = mocker.MagicMock()
    mock_token.credentials = "valid_token"

    mock_verify = mocker.MagicMock()
    mock_verify.return_value = {}

    mocker.patch.object(VerifyToken, 'verify', mock_verify)

    with pytest.raises(HTTPException) as exc_info:
        get_auth_token_sub(token=mock_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Unauthorized"


def test_get_current_user_existing_user(mocker, mock_db):
    mock_user = mocker.MagicMock()
    mock_db.query.return_value.filter_by.return_value.first.return_value = mock_user

    result = get_current_user(db=mock_db, sub="12345")
    assert result == mock_user
    mock_db.query.return_value.filter_by.assert_called_with(
        sub="12345",
        is_active=True,
    )


def test_get_current_user_new_user(mock_db):
    mock_db.query.return_value.filter_by.return_value.first.return_value = None

    result = get_current_user(db=mock_db, sub="12345")

    assert result.sub == "12345"
    assert mock_db.add.called_with(result)
    assert mock_db.commit.called
    assert mock_db.refresh.called_with(result)


def test_get_current_user_exception(mock_db):
    mock_db.query.side_effect = Exception

    with pytest.raises(BadRequestFromRaisedException) as exc_info:
        get_current_user(db=mock_db, sub="12345")
        assert isinstance(exc_info.value, BadRequestFromRaisedException)
