import logging

logger = logging.getLogger(__name__)


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
        logger.info('Authentication attempt for user: %s', username)

        if not username:
            logger.warning('Authentication failed: username missing')
            raise UnauthorizedError('Username is required')

        if not password:
            logger.warning(
                'Authentication failed: password missing for user: %s', username
            )
            raise UnauthorizedError('Password is required')

        if username != self._valid_username:
            logger.warning('Authentication failed: invalid username: %s', username)
            raise UnauthorizedError('Invalid username')

        if password != self._valid_password:
            logger.warning(
                'Authentication failed: invalid password for user: %s', username
            )
            raise UnauthorizedError('Invalid password')

        logger.info('Authentication successful for user: %s', username)
        return True
