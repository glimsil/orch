import docker
import time
import os
import copy
from src.modules.manager.services_manager import ServicesManager

class Core:

	client = docker.from_env()
	service_manager = ServicesManager()
	#
	# name - string
	# version - string
	# min_replicas - number
	# max_replicas - number
	# autoscale - bool
	# autoscale_strategy - string
	# containers - list
	#
	SERVICE_INFO_TEMPLATE = {
		'name': None,
		'image': None,
		'version': None,
		'min_replicas': 2,
		'max_replicas': 10,
		'autoscale': True,
		'autoscale_strategy': {
			'type' : 'cpu',
			'up' : 50,
			'down' : 10
		}
	} 

	# TODO:
	# Scaling up and down
	# Autoscaling and strategies config.
	# Health check

	def deploy_service(self, service_name, image_name, image_version, lb_port, **kwargs):
		is_new = False
		try:
			self.client.containers.get('traefik_lb_{service_name}'.replace('{service_name}', service_name))
		except docker.errors.NotFound:
			is_new = True
		except docker.errors.APIError as err:
			print("Failed to get lb container: {0}".format(err))
		if(is_new):
			lb_int_port = str(lb_port)+'1'
			self.create_lb(service_name, lb_port, lb_int_port)
			print('Service will listen on port ' + str(lb_port) + '. LB interface on port: ' + lb_int_port)
		if(not self.service_manager.service_info_exists(service_name)):
			service_info = self.init_service_info(service_name, image_name, image_version, lb_port)
		else:
			service_info = self.service_manager.get_service_info(service_name)
		self.deploy_scale_service(service_info)
		
	def init_service_info(self, service_name, image_name, image_version, lb_port):
		service_info = copy.deepcopy(self.SERVICE_INFO_TEMPLATE)
		service_info['name'] = service_name
		service_info['image'] = image_name
		service_info['version'] = image_version
		service_info['port'] = lb_port
		return self.service_manager.save_service_info(service_name, service_info)

	def create_lb(self, service_name, service_port, lb_dashboard_port):
		lb_image = 'traefik:1.7'
		line = 'docker run -d -p {lb_dashboard_port}:8080 -p {service_port}:80 -v $PWD/src/config/traefik.toml:/etc/traefik/traefik.toml -v /var/run/docker.sock:/var/run/docker.sock --name traefik_lb_{service_name} {lb_image}'.replace('{lb_dashboard_port}', str(lb_dashboard_port)).replace('{service_port}', str(service_port)).replace('{service_name}', service_name).replace('{lb_image}', lb_image)
		os.system(line)

	def deploy_scale_service(self, service_info):
		containers = self.list_services_by_name(service_info['name'])
		containers_to_scale = service_info['min_replicas']
		# checking if current number of container is greater than min and lesser than max
		if(len(containers) > containers_to_scale):
			containers_to_scale = len(containers)
			if(containers_to_scale > service_info['max_replicas']):
				containers_to_scale = service_info['max_replicas']
		labels = {
			'orch.service.name' : service_info['name'], 
			'traefik.backend': service_info['name'], 
			'traefik.port' : '80', 
			'traefik.frontend.rule':'Host:localhost'
			}
		ports = {
			str(service_info['port']) + '/tcp': None
			}

		# creating new containers
		for i in range(containers_to_scale):
			self.deploy_service_instance(service_info)
		
		# removing old ones
		for old_container in containers:
			old_container.remove(force=True)

	def deploy_service_instance(self, service_info):
		image = service_info['image']
		if(service_info['version'] != None):
			image += ':' + str(service_info['version'])
		labels = {
			'orch.service.name' : service_info['name'], 
			'traefik.backend': service_info['name'], 
			'traefik.port' : '80', 
			'traefik.frontend.rule':'Host:localhost'
			}
		ports = {
			str(service_info['port']) + '/tcp': None
			}
		name = service_info['name'] + '_' + str(round(time.time() * 1000))
		self.client.containers.run(image, detach=True, name = name, labels = labels, ports = ports) 

	def scale_service(self, service_name, scale_to):
		if(self.service_manager.service_info_exists(service_name)):
			service_info = self.service_manager.get_service_info(service_name)
		else:
			print('There is no service info for this service name.')
			return
		if(scale_to > service_info['max_replicas']):
			scale_to = service_info['max_replicas']
		elif(scale_to < service_info['min_replicas']):
			scale_to = service_info['min_replicas']
		containers = self.list_services_by_name(service_name)
		if(len(containers) == scale_to):
			print('Same number of replicas as requested. No changes on service.')
		elif(len(containers) < scale_to):
			print('Scaling up to ' + str(scale_to))
			for i in range(scale_to - len(containers)):
				self.scale_service_up(service_name, service_info)
		else:
			print('Scaling down to ' + str(scale_to))
			for i in range(len(containers) - scale_to):
				self.scale_service_down(service_name, service_info)
	
	def scale_service_up(self, service_name, service_info=None):
		if(service_info == None):
			if(self.service_manager.service_info_exists(service_name)):
				service_info = self.service_manager.get_service_info(service_name)
			else:
				print('There is no service info for this service name.')
				return
		
		containers = self.list_services_by_name(service_name)
		if(service_info['max_replicas'] > len(containers)):
			print('Scaling up ' + service_name)
			self.deploy_service_instance(service_info)
		else:
			print('Service \'' + service_name + '\' exceeded the max replicas limit.')

	def scale_service_down(self, service_name, service_info=None):
		if(service_info == None):
			if(self.service_manager.service_info_exists(service_name)):
				service_info = self.service_manager.get_service_info(service_name)
			else:
				print('There is no service info for this service name.')
				return
		
		containers = self.list_services_by_name(service_name)
		if(service_info['min_replicas'] < len(containers)):
			print('Scaling down ' + service_name)
			containers[-1].remove(force=True)
		else:
			print('Service \'' + service_name + '\' exceeded the min replicas limit.')

	def remove_service(self, service_name):
		try:
			lb_container = self.client.containers.get('traefik_lb_{service_name}'.replace('{service_name}', service_name))
			lb_container.remove(force=True)
		except docker.errors.NotFound as err:
			print("Load Balancer Container not found: {0}".format(err))
		except docker.errors.APIError as err:
			print("Failed to get lb container: {0}".format(err))
		containers = self.list_services_by_name(service_name)
		for container in containers:
			container.remove(force=True)
		self.service_manager.delete_service_info(service_name)

	def count_services_by_name(self, service_name):
		containers = self.list_services_by_name(service_name)
		return len(containers)

	def list_services_by_name(self, service_name):
		return self.client.containers.list(filters={'label' : 'orch.service.name='+service_name})
