import json
import io
from unittest.mock import patch, AsyncMock, MagicMock
import pytest

from aiosurge.reports import Report


class MockResponse:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockStreamResponse:
    def __init__(self, content=b"test data"):
        self.content = content

    async def aiter_bytes(self):
        yield self.content

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockAsyncContextManager:
    def __init__(self, mock_obj):
        self.mock_obj = mock_obj

    async def __aenter__(self):
        return self.mock_obj

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def ready_report_response():
    return MockResponse(
        status="READY",
        url="https://example.com/report.json.gzip",
        expires_in_seconds=3600,
    )


@pytest.fixture
def creating_report_response():
    return MockResponse(status="CREATING", job_id="job123")


@pytest.mark.asyncio
class TestReport:
    @pytest.fixture
    def setup_save_mocks(self):

        with (
            patch("httpx.AsyncClient") as mock_client,
            patch("aiosurge.reports.tempfile.NamedTemporaryFile") as mock_tempfile,
            patch("aiosurge.reports.gzip.open") as mock_gzip_open,
            patch("aiofiles.open") as mock_aiofiles_open,
        ):

            # Mock HTTP stream
            mock_stream_response = MockStreamResponse(b"compressed data")
            client_instance = AsyncMock()
            client_instance.stream = MagicMock(return_value=mock_stream_response)
            mock_client.return_value = MockAsyncContextManager(client_instance)

            # Mock tempfile
            tmp_file = MagicMock()
            tmp_file.name = "/tmp/temp_file"
            mock_tempfile.return_value.__enter__.return_value = tmp_file

            # Mock gzip
            gzip_file = MagicMock()
            gzip_file.read.return_value = b"decompressed data"
            mock_gzip_open.return_value.__enter__.return_value = gzip_file

            # Mock final file write
            aio_file = AsyncMock()
            mock_aiofiles_open.return_value.__aenter__.return_value = aio_file

            yield {
                "client": client_instance,
                "tmp_file": tmp_file,
                "gzip_file": gzip_file,
                "aio_file": aio_file,
            }

    @patch("aiosurge.reports.Report.request", new_callable=AsyncMock)
    async def test_save_report_success(
        self, mock_request, setup_save_mocks, ready_report_response
    ):
        mock_request.return_value = ready_report_response

        await Report.save_report(
            project_id="project123", type="export_json", filepath="test_output.json"
        )

        setup_save_mocks["client"].stream.assert_called_once()
        setup_save_mocks["tmp_file"].write.assert_called_with(b"compressed data")
        setup_save_mocks["gzip_file"].read.assert_called_once()
        setup_save_mocks["aio_file"].write.assert_awaited_once_with(
            b"decompressed data"
        )

    @patch("aiosurge.reports.Report.request", new_callable=AsyncMock)
    @patch("aiosurge.reports.asyncio.sleep", new_callable=AsyncMock)
    async def test_creating_then_ready(
        self,
        mock_sleep,
        mock_request,
        setup_save_mocks,
        creating_report_response,
        ready_report_response,
    ):
        mock_request.side_effect = [creating_report_response, ready_report_response]

        await Report.save_report("project123", "export_json")

        assert mock_request.await_count == 2
        mock_sleep.assert_called_once_with(2)

    @patch("aiosurge.reports.Report.request", new_callable=AsyncMock)
    async def test_report_status_error(self, mock_request):
        mock_request.return_value = MockResponse(status="ERROR")

        with pytest.raises(ValueError):
            await Report.save_report("project123", "export_json")

    @patch("aiosurge.reports.Report.request", new_callable=AsyncMock)
    async def test_report_timeout(self, mock_request):
        mock_request.return_value = MockResponse(status="CREATING", job_id="job123")

        with pytest.raises(
            Exception, match="Report failed to generate within 2 seconds"
        ):
            await Report.save_report("project123", "export_json", poll_time=2)

    @pytest.mark.parametrize(
        "json_data",
        [
            ([{"id": "1", "val": 1}, {"id": "2", "val": 2}]),
            ([]),
        ],
    )
    @patch("aiosurge.reports.Report.save_report")
    async def test_download_json_variants(self, mock_save_report, json_data):
        encoded = json.dumps(json_data).encode()

        async def mock_save(project_id, type, filepath, poll_time, api_key):
            if isinstance(filepath, io.BytesIO):
                filepath.write(encoded)

        mock_save_report.side_effect = mock_save
        result = await Report.download_json("project123")

        assert result == json_data
        assert isinstance(result, list)

    @patch("aiosurge.reports.Report.save_report")
    async def test_download_json_custom_poll_time(self, mock_save_report):
        async def dummy_save(project_id, type, filepath, poll_time, api_key):
            filepath.write(b'[{"id": "1"}]')

        mock_save_report.side_effect = dummy_save
        result = await Report.download_json("project123", poll_time=99)

        assert result == [{"id": "1"}]
