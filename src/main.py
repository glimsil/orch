import click
import requests
import json
from src.client import OrchClient
from src.manager.main import OrchManager

@click.group()
@click.version_option("0.0.1")
def cli():
    """
    First version of orch cli.
    """

@cli.command()
@click.option('--service-info-file', help='Path to service info json file', required=False)
@click.option('--service-info-raw', help='Raw service info', required=False)
@click.option('--host-file', help='Host file path. If not informed, the default will be used.', required=False)
def deploy(service_info_file, service_info_raw, host_file):
    """Simply deploy a docker container."""
    OrchClient(host_file).deploy_service(service_info_file, service_info_raw)
    
@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.option('--host-file', help='Host file path. If not informed, the default will be used.', required=False)
def get_service(service_name, host_file):
    """Retrieve the number of replicas of the service."""
    OrchClient(host_file).get_service(service_name)

@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.option('--host-file', help='Host file path. If not informed, the default will be used.', required=False)
@click.argument('scale_to')
def scale(service_name, host_file, scale_to):
    """Scale service to a specific number of replicas."""
    OrchClient(host_file).scale(service_name, scale_to)

@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.option('--host-file', help='Host file path. If not informed, the default will be used.', required=False)
def scale_up(service_name, host_file):
    """Adds one replica to the service cluster."""
    OrchClient(host_file).scale_up(service_name)

@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.option('--host-file', help='Host file path. If not informed, the default will be used.', required=False)
def scale_down(service_name, host_file):
    """Remove one replica from the service cluster."""
    OrchClient(host_file).scale_down(service_name)

@cli.command()
@click.option('--service-name', help='Service name', required=True)
@click.option('--host-file', help='Host file path. If not informed, the default will be used.', required=False)
def remove(service_name, host_file):
    """Remove service."""
    OrchClient(host_file).remove_service(service_name)

@cli.command()
def manager_init():
    """init manager."""
    OrchManager().init()
