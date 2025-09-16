class UnauthorizedError(Exception):
    """Raised when authentication fails"""

    pass


class BasicAuthService:
    """Basic authentication service"""

    def __init__(self, valid_username: str, valid_password: str):
        self._valid_username = valid_username
        self._valid_password = valid_password

    async def validate_credentials(self, username: str, password: str) -> bool:
        """Validate username and password against configured credentials"""
        if not username:
            raise UnauthorizedError('Username is required')

        if not password:
            raise UnauthorizedError('Password is required')

        if username != self._valid_username:
            raise UnauthorizedError('Invalid username')

        if password != self._valid_password:
            raise UnauthorizedError('Invalid password')

        return True
