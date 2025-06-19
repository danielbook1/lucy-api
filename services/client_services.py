from ..database.models.client import *
from .generic_services import GenericServices


client_services = GenericServices[Client, ClientCreate, ClientUpdate, ClientPublic](
    Client
)
