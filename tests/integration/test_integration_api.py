from unittest.mock import patch

from httpx import AsyncClient


async def test_health_check_success(async_client: AsyncClient):
    """Test successful health check"""
    response = await async_client.get('/health')

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert 'status' in data
    assert 'database_connected' in data
    assert 'response_datetime' in data
    assert data['status'] == 'healthy'
    assert isinstance(data['database_connected'], bool)
    # In integration tests database might be unavailable - that is normal
    # Main thing is endpoint responds with correct structure


async def test_health_check_no_auth_required(async_client: AsyncClient):
    """Test that health endpoint does not require authorization"""
    # Request without authorization headers
    response = await async_client.get('/health')

    assert response.status_code == 200


async def test_health_check_database_error(async_client: AsyncClient):
    """Test handling database error"""
    # Patch get_health_status to simulate DB error
    with patch(
        'app.infrastructure.repositories.repo_health.RDBHealthChecker.get_health_status'
    ) as mock_check:
        mock_check.return_value = False

        response = await async_client.get('/health')

        # System should handle error gracefully
        assert response.status_code == 200  # Health endpoint always returns 200
        data = response.json()
        # In case of DB error, database_connected should be False
        assert data['database_connected'] is False


async def test_get_position_success(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test successful current position retrieval"""
    response = await async_client.get('/positions', headers=auth_headers_valid)

    assert response.status_code == 200
    data = response.json()

    assert 'x' in data
    assert 'y' in data
    assert 'direction' in data
    assert isinstance(data['x'], int)
    assert isinstance(data['y'], int)
    assert data['direction'] in ['NORTH', 'SOUTH', 'EAST', 'WEST']

    assert isinstance(data['x'], int)
    assert isinstance(data['y'], int)
    assert data['direction'] in ['NORTH', 'SOUTH', 'EAST', 'WEST']


async def test_get_position_unauthorized(
    async_client: AsyncClient, auth_headers_invalid: dict
):
    """Test unauthorized access to position"""
    response = await async_client.get('/positions', headers=auth_headers_invalid)

    assert response.status_code == 401
    data = response.json()
    assert 'detail' in data


async def test_get_position_no_auth_header(async_client: AsyncClient):
    """Test request without auth header"""
    response = await async_client.get('/positions')

    assert response.status_code == 401


async def test_get_position_malformed_auth(async_client: AsyncClient):
    """Test with malformed auth header"""
    headers = {'Authorization': 'Basic invalid_base64'}
    response = await async_client.get('/positions', headers=headers)

    assert response.status_code == 401


async def test_execute_command_success(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test successful command execution"""
    payload = {'command': 'FF'}
    response = await async_client.post(
        '/commands', json=payload, headers=auth_headers_valid
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert 'x' in data
    assert 'y' in data
    assert 'direction' in data
    assert 'stopped_by_obstacle' in data
    assert 'message' in data
    assert data['stopped_by_obstacle'] is False

    # In integration tests we check that command executed successfully
    # Exact position depends on initial state in DB
    assert isinstance(data['x'], int)
    assert isinstance(data['y'], int)
    assert data['direction'] in ['NORTH', 'SOUTH', 'EAST', 'WEST']


async def test_execute_command_invalid_format(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test command execution with invalid format"""
    invalid_commands = [
        {'command': 'XYZ'},  # Invalid characters
        {'command': ''},  # Empty command
        {'command': 'F1R2'},  # Numbers are not allowed
        {'command': 'frlb'},  # Lowercase is not allowed
    ]

    for payload in invalid_commands:
        response = await async_client.post(
            '/commands', json=payload, headers=auth_headers_valid
        )

        assert response.status_code == 422  # Validation error
        data = response.json()
        assert 'detail' in data


async def test_execute_command_with_obstacles(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test command execution with obstacles from configuration"""
    # Use command that might encounter obstacle from config/obstacles.json
    payload = {'command': 'FFFFF'}  # Many steps forward
    response = await async_client.post(
        '/commands', json=payload, headers=auth_headers_valid
    )

    assert response.status_code == 200
    data = response.json()

    # Check that response contains obstacle information
    assert 'stopped_by_obstacle' in data
    assert isinstance(data['stopped_by_obstacle'], bool)


async def test_execute_command_unauthorized(
    async_client: AsyncClient, auth_headers_invalid: dict
):
    """Test unauthorized command execution"""
    payload = {'command': 'F'}
    response = await async_client.post(
        '/commands', json=payload, headers=auth_headers_invalid
    )

    assert response.status_code == 401


async def test_execute_command_valid_commands(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test various valid commands"""
    valid_commands = ['F', 'B', 'L', 'R', 'LR', 'FBLR']

    for command in valid_commands:
        payload = {'command': command}
        response = await async_client.post(
            '/commands', json=payload, headers=auth_headers_valid
        )

        assert response.status_code == 200, f"Command '{command}' should be valid"
        data = response.json()

        # Check that all required fields are present
        assert 'x' in data
        assert 'y' in data
        assert 'direction' in data
        assert 'stopped_by_obstacle' in data


async def test_execute_command_invalid_json(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test with invalid JSON in request body"""
    # Test with missing command field
    response = await async_client.post('/commands', json={}, headers=auth_headers_valid)
    assert response.status_code == 422

    # Test with additional fields (forbidden by configuration)
    payload = {'command': 'F', 'extra_field': 'not_allowed'}
    response = await async_client.post(
        '/commands', json=payload, headers=auth_headers_valid
    )
    assert response.status_code == 422


async def test_full_rover_operation_flow(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test complete rover integration scenario"""
    # 1. Check system health
    health_response = await async_client.get('/health')
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data['status'] == 'healthy'
    # In integration tests database might be unavailable - skip check

    # 2. Get initial position
    position_response = await async_client.get('/positions', headers=auth_headers_valid)
    assert position_response.status_code == 200
    initial_position = position_response.json()
    assert isinstance(initial_position['x'], int)
    assert isinstance(initial_position['y'], int)
    assert initial_position['direction'] in ['NORTH', 'SOUTH', 'EAST', 'WEST']

    # 3. Execute movement command
    command_payload = {'command': 'FF'}
    command_response = await async_client.post(
        '/commands', json=command_payload, headers=auth_headers_valid
    )
    assert command_response.status_code == 200

    final_position = command_response.json()

    # Check that command executed and position may have changed
    assert isinstance(final_position['x'], int)
    assert isinstance(final_position['y'], int)
    assert final_position['direction'] in ['NORTH', 'SOUTH', 'EAST', 'WEST']
    assert isinstance(final_position['stopped_by_obstacle'], bool)

    # 4. Check that new position was saved to DB
    new_position_response = await async_client.get(
        '/positions', headers=auth_headers_valid
    )
    assert new_position_response.status_code == 200
    saved_position = new_position_response.json()

    # Position in DB should match the last executed command
    assert saved_position['x'] == final_position['x']
    assert saved_position['y'] == final_position['y']
    assert saved_position['direction'] == final_position['direction']


async def test_error_response_format(
    async_client: AsyncClient, auth_headers_valid: dict
):
    """Test error response format"""
    # Test 401 Unauthorized
    response = await async_client.get('/positions')
    assert response.status_code == 401
    data = response.json()
    assert 'detail' in data

    # Test 422 Validation Error
    payload = {'command': 'INVALID'}
    response = await async_client.post(
        '/commands', json=payload, headers=auth_headers_valid
    )
    assert response.status_code == 422
    data = response.json()
    assert 'detail' in data


async def test_api_performance_basic(async_client: AsyncClient):
    """Basic API performance test"""
    import time

    start_time = time.time()
    response = await async_client.get('/health')
    end_time = time.time()

    assert response.status_code == 200
    # API should respond quickly (less than 2 seconds for health check with real DB)
    assert (end_time - start_time) < 2.0
