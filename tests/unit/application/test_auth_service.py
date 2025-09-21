"""Tests for BasicAuthService"""

import pytest

from app.application.auth_service import BasicAuthService, UnauthorizedError


# Fixtures
@pytest.fixture
def test_valid_username():
    """Valid username for testing (specific to auth service tests)"""
    return 'test-user'


@pytest.fixture
def test_valid_password():
    """Valid password for testing (specific to auth service tests)"""
    return 'test-secret-password-123'


@pytest.fixture
def auth_service(test_valid_username, test_valid_password):
    """Create BasicAuthService instance"""
    return BasicAuthService(test_valid_username, test_valid_password)


# Tests for successful validation
async def test_validate_credentials_success(
    auth_service, test_valid_username, test_valid_password
):
    """Test successful credentials validation"""

    result = await auth_service.validate_credentials(
        test_valid_username, test_valid_password
    )

    assert result is True


# Tests for invalid credentials
async def test_validate_credentials_with_invalid_username(
    auth_service, test_valid_password
):
    """Test validation with invalid username"""

    invalid_username = 'wrong-user'

    with pytest.raises(UnauthorizedError) as exc_info:
        await auth_service.validate_credentials(invalid_username, test_valid_password)

    assert str(exc_info.value) == 'Invalid username'


async def test_validate_credentials_with_invalid_password(
    auth_service, test_valid_username
):
    """Test validation with invalid password"""

    invalid_password = 'wrong-password'

    with pytest.raises(UnauthorizedError) as exc_info:
        await auth_service.validate_credentials(test_valid_username, invalid_password)

    assert str(exc_info.value) == 'Invalid password'


@pytest.mark.parametrize(
    'username,password,expected_error',
    [
        ('', 'valid-password', 'Username is required'),
        (None, 'valid-password', 'Username is required'),
        ('test-user', '', 'Password is required'),  # use valid username
        ('test-user', None, 'Password is required'),  # use valid username
        ('   ', 'valid-password', 'Invalid username'),  # whitespace username
        (
            'test-user',
            '   ',
            'Invalid password',
        ),  # use valid username, whitespace password
    ],
)
async def test_validate_credentials_with_invalid_inputs(
    auth_service, username, password, expected_error
):
    """Test validation with various invalid inputs"""

    with pytest.raises(UnauthorizedError) as exc_info:
        await auth_service.validate_credentials(username, password)

    assert str(exc_info.value) == expected_error


@pytest.mark.parametrize(
    'special_username,special_password',
    [
        ('user-!@#$%^&*()_+-=[]{}|;:,.<>?', 'pass-!@#$%^&*()_+-=[]{}|;:,.<>?'),
        ('тест-юзер', 'тест-пароль'),  # unicode characters
    ],
)
async def test_validate_credentials_with_special_characters(
    special_username, special_password
):
    """Test credentials validation with special and unicode characters"""

    service = BasicAuthService(special_username, special_password)

    result = await service.validate_credentials(special_username, special_password)

    assert result is True
