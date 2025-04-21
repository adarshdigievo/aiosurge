# [Unofficial] Surge Python SDK (Async)

The Surge Python SDK provides convenient access to the Surge API from applications written in the Python language.

- This is an unofficial async clone of the [Official Python SDK](https://github.com/surge-ai/surge-python)
- For a list of major changes made, see [Full Async Changelog](./asyncio_conversion.md)

## Development

- To install dev dependencies, first [install uv](https://docs.astral.sh/uv/getting-started/installation/)
- Install the optional dev dependencies using `uv sync --extra dev`
- Test the package across supported python versions using the `tox` command.

- You may also use the `pytest` command directly to run tests from the command line:

```bash
# Run all tests
pytest

# Run tests in a specific file
pytest tests/test_projects.py

# Run a specific test
pytest tests/test_projects.py::test_init_complete
```

### Installation

For an editable install of the package for local testing, you can use the below command:

```bash
pip install -e .
```

### Requirements

* Python 3.9+

## Usage

The below examples assume that the code is **executed in an async environment** (in the body of coroutine functions)

### Authentication

The library needs to be configured with your account's API key which is available in your Surge Profile. Set
`surge.api_key` to its value:

```python
import aiosurge

aiosurge.api_key = "YOUR API KEY"
```

Or set the API key as an environment variable:

```bash
export SURGE_API_KEY=<YOUR API KEY>
```

### Downloading project results

Once the API key has been set, you can list all of the Projects under your Surge account or retrieve a specific Project
by its ID.

```python
# List your Projects
projects = await aiosurge.Project.list()

# Print the name of the first Project
print(projects[0].name)

# Retrieve a specific Project
project = await aiosurge.Project.retrieve("076d207b-c207-41ca-b73a-5822fe2248ab")

# Download the results for that project
results = await project.download_json()

# Alternatively, download the results to a file
await project.save_report("export_csv", "results.csv")
```

### Creating projects

If you have a blueprint, you can use it as a template to get a new batch of data annotated.
You can add new labeling tasks from a CSV or with a list of dictionaries.

```python
# List blueprint projects
blueprint_projects = await aiosurge.Project.list_blueprints()
blueprint = blueprint_projects[0]

# Create a project from a blueprint
project = await aiosurge.Project.create("My Labeling Project (July 2023 Batch)", template_id=blueprint.id)

# Add data from a CSV file
await project.create_tasks_from_csv('my_data.csv')

# Or add data directly
tasks = await project.create_tasks([{
    "company": "Surge",
    "city": "San Francisco",
    "state": "CA"
}])
```

### Creating tasks

You can create new Tasks for a project, list all of the Tasks in a given project, or retrieve a specific Task given its
ID.

```python
# Create Tasks for the new Project
tasks_data = [{"id": 1, "company": "Surge AI"}, {"id": 2, "company": "Twitch TV"}]
tasks = await project.create_tasks(tasks_data)

# List all Tasks in the Project
all_tasks = await project.list_tasks()

# Retrieve a specific Task
task = await aiosurge.Task.retrieve(task_id="eaa44610-c8f6-4480-b746-28b6c8defd4d")

# Print the fields of that Task
print(task.fields)
```

You can also create Tasks in bulk by uploading a local CSV file. The header of the CSV file must specify the fields that
are used in your Tasks.

| id |  company  |
|:---|:---------:|
| 1  | Surge AI  |
| 2  | Twitch TV |

```python
# Create Tasks in bulk via CSV file
file_path = "./companies_to_classify.csv"
tasks = await project.create_tasks_from_csv(file_path)
```
