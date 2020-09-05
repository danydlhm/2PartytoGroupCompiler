from partygroupcomp.participant import Participant
from partygroupcomp.commitment import CramerShoup
from partygroupcomp.ake import DHAKE
from partygroupcomp.channel import start_server, init_participant_parallel
from partygroupcomp import log
from datetime import datetime
from random import randint
from multiprocessing import Process
from time import sleep, time


def init_participants(index_exec=None, args=None, n_participants=randint(15, 100)):
    log.info("Init participants")
    c = CramerShoup()
    pk_c = c.generate_parameters()
    time_ini = time()
    participants = [Participant(uid=i, commitment=c) for i in range(1, n_participants + 1)]
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
    try:
        with open(f'.\\extras\\claves.csv', mode='a') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            for i in range(len(K)):
                k = K[i]
                sk_i = sk[i]
                sid_i = sid[i]
                log.debug("Clave calculada K: " + str(k))
                log.debug("Clave calculada sk: " + str(sk_i))
                log.debug("Clave calculada sid: " + str(sid_i))
                aux_exec = str(index_exec) + "," if index_exec is not None else ""
                f.write(f"{aux_exec}{timestamp},{str(k).replace(',', ';')},{sk_i},{sid_i}\n")
    except:
        log.error('Algo ha ido mal al escribir el fichero de claves')
    if all(ack):
        try:
            with open(f'.\\extras\\tiempo.csv', mode='a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                f.write(f"{args.multiprocess},{timestamp},{n_participants},{time() - time_ini},"
                        f"{str(K).replace(',', ';')},{sk[0]},{sid[0]}\n")
        except:
            log.error('Algo ha ido mal al escribir el fichero de tiempo')
    DHAKE.reset_object()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Execute 2PartyToGroup Algorithm')
    parser.add_argument('-i', '--iterations', type=int, default=1,
                        help='a positive integer for the repetitions')
    parser.add_argument('-m', '--multiprocess', type=bool, default=False,
                        help='activate the algorithm process in multiples process)')

    args = parser.parse_args()
    for i in range(args.iterations):
        log.info(f'Init iteration {i}')
        n_participants = randint(15, 100)
        try:
            if not args.multiprocess:
                init_participants(i, args, n_participants=n_participants)
            else:
                p_server = Process(target=start_server)
                p_server.start()
                sleep(10)
                pids = []
                for j in range(n_participants):
                    p_i = Process(target=init_participant_parallel, args=(n_participants, args))
                    pids.append(p_i)
                    p_i.start()
                [pid.join() for pid in pids]
                log.debug(f"Cerrando servidor")
                p_server.kill()
                p_server.join()
                p_server.close()
                [pid.close() for pid in pids]
            log.debug(f"{i}: Acierto")
        except Exception as e:
            log.debug(f"{i}: Fallo")
