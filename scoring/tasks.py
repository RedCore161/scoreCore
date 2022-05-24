import docker


def task_stop_docker_container(container):
    client = docker.from_env()
    cont = client.containers.get(container)
    if cont:
        cont.stop()
