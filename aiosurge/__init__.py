import os

from aiosurge.projects import Project
from aiosurge.tasks import Task
from aiosurge.teams import Team
from aiosurge.reports import Report

api_key = os.environ.get("SURGE_API_KEY", None)
base_url = os.environ.get("SURGE_BASE_URL", "https://app.surgehq.ai/api")
