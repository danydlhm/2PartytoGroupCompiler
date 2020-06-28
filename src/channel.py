import asyncio

users = {}
index_free = set()

async def handle_connection(reader, writer):
    if len(index_free) > 0:
        i = index_free.pop()
        users[i] = (reader, writer)
    else:
        users[len(users)] = (reader, writer)
    count_blank_messages = 0
    while True:
        try:
            data = await reader.readline()
            count_blank_messages = count_blank_messages+1 if len(data) == 0 else 0
            if count_blank_messages > 5:
                raise Exception('Close connection')
            addr = writer.get_extra_info('peername')

            print(f"Received {data!r} from {addr!r}")
            connection_closed = []
            for key, user in users.items():
                try:
                    user[1].write(data)
                    await user[1].drain()
                except:
                    connection_closed.append(key)
                    pass
            for i in connection_closed:
                users.pop(i)
                index_free.add(i)
        except Exception as e:
            print(e)
            print("closed connection")
            break

async def main():
    server = await asyncio.start_server(
        handle_connection, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


def start_server():
    asyncio.run(main())


if __name__ == '__main__':
    start_server()
