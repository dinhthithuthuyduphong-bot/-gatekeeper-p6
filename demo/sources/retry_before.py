from client import TransientError


def push(client, item):
    client.write(item)
