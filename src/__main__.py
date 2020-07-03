from src.participant import Participant
from src.commitment import CramerShoup
from src.ake import DHAKE
from src.channel import start_server
from src import log
from datetime import datetime
from random import randint
from codecs import decode,encode
from os import getpid
from platform import node
from multiprocessing import Process
import asyncio
from hashlib import sha1
import dill
from cryptography.hazmat.primitives.serialization import ParameterFormat, Encoding, load_pem_parameters, PublicFormat, load_pem_public_key
from cryptography.hazmat.backends import default_backend
from time import sleep


def init_participants(index_exec=None):
    log.info("Init participants")
    c = CramerShoup()
    pk_c = c.generate_parameters()
    n_participants = randint(15, 100)
    participants = [Participant(uid=i, commitment=c) for i in range(1, n_participants+1)]
    log.info("Get UIDS")
    uids = [p.uid for p in participants]
    for i in range(n_participants):
        log.info(f"round_0 participant {i}")
        aux_p = participants[i]
        pk_1 = participants[(i + 1) % n_participants].pk_ake
        pk_2 = participants[(i - 1) % n_participants].pk_ake
        aux_p.round_0(uids=uids, pk_1=pk_1, pk_2=pk_2)
    log.info("Starting Round 1")
    m_1 = [p.round_1(pk_i=pk_c) for p in participants]
    log.info("Starting Round 2")
    m_2 = [p.round_2_1() for p in participants]
    log.info("Ending Round 2...")
    ack, K, sk, sid = zip(*[p.round_2_2(m_1=m_1, m_2=m_2) for p in participants])
    log.info("Round 2 ends")
    log.info("Algorithm works: " + str(all(ack)))
    with open(f'..\\extras\\claves.csv', mode='a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        for i in range(len(K)):
            k = K[i]
            sk_i = sk[i]
            sid_i = sid[i]
            log.debug("Clave calculada K: " + str(k))
            log.debug("Clave calculada sk: " + str(sk_i))
            log.debug("Clave calculada sid: " + str(sid_i))
            aux_exec = str(index_exec)+"," if index_exec is not None else ""
            f.write(f"{aux_exec}{timestamp},{str(k).replace(',', ';')},{sk_i},{sid_i}\n")
    DHAKE.reset_object()


def __encode_message(m):
    if type(m) is bytes:
        print(encode(m, "hex"))
        aux_m = (str(encode(m, "hex").decode('utf-8')) + '\n').encode()
    else:
        aux_m = (str(m) + '\n').encode()
    return aux_m


async def execute_participant(n_participants):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)
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
            a = decode(a.decode().replace('\n',''), 'hex')
            c = dill.loads(a)
            a = await reader.readline()
            a = decode(a.decode().replace('\n',''), 'hex')
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
                writer.write(__encode_message(dill.dumps(ake.parameters.parameter_bytes(encoding=Encoding.PEM, format=ParameterFormat.PKCS3))))
                await writer.drain()
                a = await reader.readline()
                a = await reader.readline()
                a = await reader.readline()
                a = await reader.readline()
                a = await reader.readline()
        log.debug(f'Received: {data_str!r}')
    participant = Participant(uid=uid, commitment=c, ake=ake)
    pk_ake = participant.pk_ake.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo)
    writer.write(__encode_message(dill.dumps({uid: pk_ake})))
    await writer.drain()
    pk_ake_dic = {}
    ix_uid = uids.index(uid)
    uid_next = uids[(ix_uid+1) % len(uids)]
    uid_before = uids[(ix_uid-1) % len(uids)]
    while True:
        a = await reader.readline()
        a = decode(a.decode().replace('\n', ''), 'hex')
        pk_ake_other = dill.loads(a)
        pk_ake_other = {key: load_pem_public_key(value, backend=default_backend()) for key, value in pk_ake_other.items()}
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
    K_others = []
    writer.write(__encode_message(dill.dumps(K)))
    await writer.drain()
    while True:
        a = await reader.readline()
        a = decode(a.decode().replace('\n', ''), 'hex')
        K_other = dill.loads(a)
        K_others.append(K_other)
        if len(K_others) == n_participants:
            break
    ack_2 = all([K==k for k in K_others])
    log.info("Algorithm works: " + str(ack and ack_2))


def init_participant_parallel(n_participants):
    asyncio.run(execute_participant(n_participants))




if __name__ == '__main__':
    # for i in range(100):
    #     try:
    #         init_participants(i)
    #         log.debug(f"{i}: Acierto")
    #     except Exception as e:
    #         log.debug(f"{i}: Fallo")
    n_participants = randint(15, 100)
    p_server = Process(target=start_server)
    p_server.start()
    sleep(10)
    pids = []
    for i in range(n_participants):
        p_i = Process(target=init_participant_parallel, args=(n_participants,))
        pids.append(p_i)
        p_i.start()
    [pid.join() for pid in pids]
    p_server.terminate()
    p_server.close()
    [pid.close() for pid in pids]

