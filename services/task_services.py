from ..database.models.task import *
from .generic_services import GenericServices


task_services = GenericServices[Task, TaskCreate, TaskUpdate, TaskPublic](Task)
