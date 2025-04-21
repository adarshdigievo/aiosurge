from aiocsv import AsyncReader
import aiofiles


async def load_tasks_data_from_csv(file_path: str):
    tasks_data = []

    async with aiofiles.open(file_path) as csvfile:
        reader = AsyncReader(csvfile)

        try:
            headers = await reader.__anext__()
        except StopAsyncIteration:
            headers = None

        assert type(headers) is list and len(headers) > 0

        async for row in reader:
            data = {}
            for i in range(len(headers)):
                data[headers[i]] = row[i]
            tasks_data.append(data)

    return tasks_data
