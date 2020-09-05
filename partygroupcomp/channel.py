import asyncio
import traceback
from partygroupcomp import log
from partygroupcomp.participant import Participant
from partygroupcomp.commitment import CramerShoup
from partygroupcomp.ake import DHAKE

from codecs import decode, encode
from os import getpid
from platform import node
from hashlib import sha1
from time import time
from datetime import datetime
import dill
from cryptography.hazmat.primitives.serialization import ParameterFormat, Encoding, load_pem_parameters, PublicFormat, \
    load_pem_public_key
from cryptography.hazmat.backends import default_backend

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
            count_blank_messages = count_blank_messages + 1 if len(data) == 0 else 0
            if count_blank_messages > 5:
                raise Exception('Close connection')
            addr = writer.get_extra_info('peername')

            log.debug(f"Received {data!r} from {addr!r}")
            connection_closed = []
            users_aux = users.copy()
            for key, user in users_aux.items():
                try:
                    user[1].write(data)
                    await user[1].drain()
                except:
                    connection_closed.append(key)
                    pass
            for i in connection_closed:
                users_aux = users.copy()
                if i in users_aux:
                    users.pop(i)
                if i not in index_free:
                    index_free.add(i)
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            log.error("closed connection")
            break


async def main():
    server = await asyncio.start_server(
        handle_connection, '127.0.0.1', 8888)

    addr = server.sockets[0].getsockname()

    async with server:
        await server.serve_forever()


def start_server():
    asyncio.run(main())


def init_participant_parallel(n_participants, args):
    asyncio.run(execute_participant(n_participants, args))


def __encode_message(m):
    if type(m) is bytes:
        aux_m = (str(encode(m, "hex").decode('utf-8')) + '\n').encode()
    else:
        aux_m = (str(m) + '\n').encode()
    return aux_m


async def execute_participant(n_participants, args):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
    participant_principal = False
    h = sha1()
    pid = getpid()
    h.update(pid.to_bytes((pid.bit_length() + 7) // 8, byteorder='big'))
    h.update(node().encode('utf-8'))
    uid = int.from_bytes(h.digest(), byteorder='big')
    writer.write(__encode_message(uid))
    await writer.drain()
    uids = []
    c = None
    ake = None
    while len(uids) != n_participants:
        data = await reader.readline()
        data_str = data.decode()
        if ';' in data_str:
            uids = [int(uid) for uid in data_str.replace('\n', '').split(';')]
            a = await reader.readline()
            a = decode(a.decode().replace('\n', ''), 'hex')
            c = dill.loads(a)
            a = await reader.readline()
            a = decode(a.decode().replace('\n', ''), 'hex')
            pk_c = dill.loads(a)
            a = await reader.readline()
            a = decode(a.decode().replace('\n', ''), 'hex')
            ake = dill.loads(a)
            a = await reader.readline()
            a = decode(a.decode().replace('\n', ''), 'hex')
            parameters = dill.loads(a)
            parameters_1 = load_pem_parameters(parameters, backend=default_backend())
            ake.parameters = parameters_1
        else:
            uids.append(int(data_str.replace('\n', '')))
            if len(uids) == n_participants:
                c = CramerShoup()
                pk_c = c.generate_parameters()
                ake = DHAKE()
                writer.write(__encode_message(';'.join([str(i) for i in uids])))
                writer.write(__encode_message(dill.dumps(c)))
                await writer.drain()
                writer.write(__encode_message(dill.dumps(pk_c)))
                await writer.drain()
                writer.write(__encode_message(dill.dumps(ake)))
                writer.write(__encode_message(
                    dill.dumps(ake.parameters.parameter_bytes(encoding=Encoding.PEM, format=ParameterFormat.PKCS3))))
                await writer.drain()
                a = await reader.readline()
                a = await reader.readline()
                a = await reader.readline()
                a = await reader.readline()
                a = await reader.readline()
                participant_principal = True
        log.debug(f'Received: {data_str!r}')
    if participant_principal:
        time_ini = time()
    participant = Participant(uid=uid, commitment=c, ake=ake)
    pk_ake = participant.pk_ake.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
    writer.write(__encode_message(dill.dumps({uid: pk_ake})))
    await writer.drain()
    pk_ake_dic = {}
    ix_uid = uids.index(uid)
    uid_next = uids[(ix_uid + 1) % len(uids)]
    uid_before = uids[(ix_uid - 1) % len(uids)]
    while True:
        a = await reader.readline()
        a = decode(a.decode().replace('\n', ''), 'hex')
        pk_ake_other = dill.loads(a)
        pk_ake_other = {key: load_pem_public_key(value, backend=default_backend()) for key, value in
                        pk_ake_other.items()}
        pk_ake_dic.update(pk_ake_other)
        if len(pk_ake_dic) == n_participants:
            break
    log.info(f"round_0 participant {uid}")
    participant.round_0(uids=uids, pk_1=pk_ake_dic[uid_next], pk_2=pk_ake_dic[uid_before])
    log.info("Starting Round 1")
    m_1_dict = {}
    m_1_i = participant.round_1(pk_i=pk_c)
    writer.write(__encode_message(dill.dumps(m_1_i)))
    await writer.drain()
    while True:
        a = await reader.readline()
        a = decode(a.decode().replace('\n', ''), 'hex')
        m_1_i_other = dill.loads(a)
        m_1_dict[m_1_i_other[0]] = m_1_i_other
        if len(m_1_dict) == n_participants:
            break
    m_1 = [m_1_dict[p] for p in uids]
    log.info("Starting Round 2")
    m_2_i = participant.round_2_1()
    m_2_dict = {}
    writer.write(__encode_message(dill.dumps(m_2_i)))
    await writer.drain()
    while True:
        a = await reader.readline()
        a = decode(a.decode().replace('\n', ''), 'hex')
        m_2_i_other = dill.loads(a)
        m_2_dict[m_2_i_other[0]] = m_2_i_other
        if len(m_2_dict) == n_participants:
            break
    m_2 = [m_2_dict[p] for p in uids]
    log.info("Ending Round 2...")
    ack, K, sk, sid = participant.round_2_2(m_1=m_1, m_2=m_2)
    log.info("Round 2 ends")
    writer.write(__encode_message(dill.dumps(K)))
    await writer.drain()
    K_others = []
    while True:
        try:
            a = await asyncio.wait_for(reader.readline(), 10)
        except asyncio.TimeoutError:
            log.debug('TimeOut')
            break
        a = decode(a.decode().replace('\n', ''), 'hex')
        K_other = dill.loads(a)
        K_others.append(K_other)
        if len(K_others) == n_participants:
            break
    ack_2 = all([K == k for k in K_others])
    log.info("Algorithm works: " + str(ack and ack_2))
    if participant_principal and ack and ack_2:
        try:
            with open(f'.\\extras\\tiempo.csv', mode='a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                f.write(f"{args.multiprocess},{timestamp},"
                        f"{n_participants},{time() - time_ini},{str(K).replace(',', ';')},{sk},{sid}\n")
        except:
            log.error('Algo ha ido mal al escribir el fichero de tiempo')


if __name__ == '__main__':
    start_server()
