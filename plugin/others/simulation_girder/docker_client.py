import docker

client = docker.from_env()
try :
    cc = client.containers.run(
        image='covid.creatis.insa-lyon.fr/fcervenansky/kevin:0.1',
        command='run_batch_manager_light.sh /data /data/results',
        volumes={
            '/home/blot/Documents/girderServer/venv/storage': {
                'bind': '/data', 
                'mode': 'rw'
            },
        },
        detach=False
)
except docker.errors.ContainerError as e:
    print(e)