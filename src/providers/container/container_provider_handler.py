from src.providers.container.docker_container_provider import DockerContainerProvider

class ContainerProviderHandler():
    _container_provider = None
    def __init__(self):
        self._container_provider = DockerContainerProvider()

    def get_provider(self):
        return self._container_provider