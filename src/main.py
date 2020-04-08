import click
from src.core import Core


@click.group()
@click.version_option("1.0")
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

    Core().deploy(service_name, image_name, image_version, port)
