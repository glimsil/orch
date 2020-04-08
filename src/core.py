import docker
import time
import os

class Core:
	client = docker.from_env()

	#
	# name - string
	# version - string
	# min_replicas - number
	# max_replicas - number
	# autoscale - bool
	# autoscale_strategy - string
	# containers - list
	#
	SERVICES_CONTROL = {} 

	# TODO:
	# Managing services and configs in disk
	# Scaling up and down
	# Autoscaling and strategies config.
	# Health check

	def deploy(self, service, image_name, image_version, lb_port, **kwargs):
		image = image_name
		if(image_version != None):
			image += ':' + str(image_version)
		name = service + '_' + str(round(time.time() * 1000))

		is_new = False
		try:
			self.client.containers.get('traefik_lb_{service_name}'.replace('{service_name}', service))
		except docker.errors.NotFound:
			is_new = True
		except docker.errors.APIError as err:
			print("Failed to get lb container: {0}".format(err))
		if(is_new):
			lb_int_port = str(lb_port)+'1'
			self.create_lb(service, lb_port, lb_int_port)
			print('Service will listen on port ' + str(lb_port) + '. LB interface on port: ' + lb_int_port)
		self.client.containers.run(image, detach=True, name = name, labels = {'traefik.backend': service, 'traefik.port' : '80', 'traefik.frontend.rule':'Host:localhost'}, ports= {str(lb_port) + '/tcp': None}) 

	def create_lb(self, service_name, service_port, lb_dashboard_port):
		lb_image = 'traefik:1.7'
		line = 'docker run -d -p {lb_dashboard_port}:8080 -p {service_port}:80 -v $PWD/src/config/traefik.toml:/etc/traefik/traefik.toml -v /var/run/docker.sock:/var/run/docker.sock --name traefik_lb_{service_name} {lb_image}'.replace('{lb_dashboard_port}', str(lb_dashboard_port)).replace('{service_port}', str(service_port)).replace('{service_name}', service_name).replace('{lb_image}', lb_image)
		os.system(line)
