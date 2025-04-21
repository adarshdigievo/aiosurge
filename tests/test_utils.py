import pytest
from unittest.mock import patch, AsyncMock
import io

from aiosurge.utils import load_tasks_data_from_csv


class MockAsyncReader:
    def __init__(self, data):
        """
        Initialize with data rows (list of lists).
        First row is treated as headers.
        """
        self.data = data
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.data):
            row = self.data[self.index]
            self.index += 1
            return row
        raise StopAsyncIteration


class MockAsyncContextManager:
    def __init__(self, mock_file):
        self.mock_file = mock_file

    async def __aenter__(self):
        return self.mock_file

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
class TestUtils:
    @patch("aiofiles.open")
    async def test_load_tasks_data_from_csv(self, mock_open):
        # Mock CSV data
        csv_data = [
            ["id", "name", "description", "priority"],
            ["task1", "Task 1", "Description 1", "high"],
            ["task2", "Task 2", "Description 2", "medium"],
            ["task3", "Task 3", "Description 3", "low"],
        ]

        # Set up mock reader
        mock_reader = MockAsyncReader(csv_data)

        # Set up mock file and context manager
        mock_file = AsyncMock()
        mock_context_manager = MockAsyncContextManager(mock_file)
        mock_open.return_value = mock_context_manager

        # Patch AsyncReader to return our mock
        with patch("aiosurge.utils.AsyncReader", return_value=mock_reader):
            # Call the function
            result = await load_tasks_data_from_csv("dummy_path.csv")

            # Verify the results
            assert len(result) == 3

            # Check first row
            assert result[0]["id"] == "task1"
            assert result[0]["name"] == "Task 1"
            assert result[0]["description"] == "Description 1"
            assert result[0]["priority"] == "high"

            # Check second row
            assert result[1]["id"] == "task2"
            assert result[1]["name"] == "Task 2"
            assert result[1]["description"] == "Description 2"
            assert result[1]["priority"] == "medium"

            # Check third row
            assert result[2]["id"] == "task3"
            assert result[2]["name"] == "Task 3"
            assert result[2]["description"] == "Description 3"
            assert result[2]["priority"] == "low"

            # Verify open was called with the right path
            mock_open.assert_called_once_with("dummy_path.csv")

    @patch("aiofiles.open")
    async def test_load_tasks_data_from_csv_empty(self, mock_open):
        # Mock CSV data with only headers
        csv_data = [
            ["id", "name", "description", "priority"],
        ]

        # Set up mock reader
        mock_reader = MockAsyncReader(csv_data)

        # Set up mock file and context manager
        mock_file = AsyncMock()
        mock_context_manager = MockAsyncContextManager(mock_file)
        mock_open.return_value = mock_context_manager

        # Patch AsyncReader to return our mock
        with patch("aiosurge.utils.AsyncReader", return_value=mock_reader):
            # Call the function
            result = await load_tasks_data_from_csv("dummy_path.csv")

            # Verify the results
            assert len(result) == 0
            assert isinstance(result, list)

    @patch("aiofiles.open")
    async def test_load_tasks_data_from_csv_no_headers(self, mock_open):
        # Mock CSV data with empty list
        csv_data = []

        # Set up mock reader
        mock_reader = MockAsyncReader(csv_data)

        # Set up mock file and context manager
        mock_file = AsyncMock()
        mock_context_manager = MockAsyncContextManager(mock_file)
        mock_open.return_value = mock_context_manager

        # Patch AsyncReader to return our mock
        with patch("aiosurge.utils.AsyncReader", return_value=mock_reader):
            # Call the function and expect an assertion error
            with pytest.raises(AssertionError):
                await load_tasks_data_from_csv("dummy_path.csv")
