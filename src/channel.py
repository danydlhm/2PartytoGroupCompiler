import asyncio

async def tcp_echo_client(message):
    reader, writer = None, None

    print(f'Send: {message!r}')
    writer.write(message.encode())

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(tcp_echo_client('Hello World!'))


class Channel:
    participants = []

    def __init__(self) -> None:
        pass

    def broadcast(self, msg) -> None:
        for i in self.participants:
            pass  # send the message to all participants

    def subscribe(self, participant) -> None:
        self.participants.append(participant)


class ChannelParticipant:

    def __init__(self, host, port) -> None:
        self.host = host
        self.port = port
        # ToDo: Open connection
        # ToDo: Send subscribe with my IP and port for listening


    def broadcast(self, msg) -> None:
        # ToDo: Open server connection
        # ToDo: Send message
        pass

    def read(self, msg) -> None:
        msgs = self.connection.read_all()
        # ToDo: On server connection read message

    # def get_all_messages(self, msg) -> None:
    #     # ToDo: On server connection read message
    #     pass
