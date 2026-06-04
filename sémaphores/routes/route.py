import requests

semaphores = requests.get('http://192.168.1.100:8000/get_semaphore')

print(semaphores.status_code)

mes_semaphores = semaphores.json()

print(mes_semaphores)