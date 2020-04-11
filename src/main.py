import click
from src.core import Core


@click.group()
@click.version_option("0.0.1")
def cli():
    """
    First version of orch cli.
    """


@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.option('--image-name', help='Image Name', required=True)
@click.option('--image-version', default='latest', help='Image Version')
@click.option('--port', default='4000', help='Image Version')
def deploy(service_name, image_name, image_version, port):
    """Simply deploy a docker container."""

    Core().deploy_service(service_name, image_name, image_version, port)


@cli.command()
@click.option('--service-name', help='Service name', required=True)
def replicas_count(service_name):
    """Retrieve the number of replicas of the service."""
    print(Core().count_services_by_name(service_name))

@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.argument('scale_to')
def scale(service_name, scale_to):
    """Scale service to a specific number of replicas."""
    Core().scale_service(service_name, int(scale_to))

@cli.command()
@click.option('--service-name', help='Service name', required=True)
def scale_up(service_name):
    """Adds one replica to the service cluster."""
    Core().scale_service_up(service_name)

@cli.command()
@click.option('--service-name', help='Service name', required=True)
def scale_down(service_name):
    """Remove one replica from the service cluster."""
    Core().scale_service_down(service_name)

@cli.command()
@click.option('--service-name', help='Service name', required=True)
def remove(service_name):
    """Remove service."""
    Core().remove_service(service_name)
