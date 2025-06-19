from ..database.models.project import *
from .generic_services import GenericServices


project_services = GenericServices[
    Project, ProjectCreate, ProjectUpdate, ProjectPublic
](Project)
