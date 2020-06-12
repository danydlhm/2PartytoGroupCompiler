from src.participant import Participant
from src.commitment import CramerShoup
from src.ake import DHAKE
from src import log
from datetime import datetime
from random import randint


def init_participants(index_exec=None):
    log.info("Init participants")
    c = CramerShoup()
    pk_c = c.generate_parameters()
    n_participants = randint(3, 10)
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
    ack, K = zip(*[p.round_2_2(m_1=m_1, m_2=m_2) for p in participants])
    log.info("Round 2 ends")
    log.info("Algorithm works: " + str(all(ack)))
    with open(f'..\\extras\\claves.csv', mode='a') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        for k in K:
            log.debug("Clave calculada K: " + str(k))
            aux_exec = str(index_exec)+"," if index_exec is not None else ""
            f.write(f"{aux_exec}{timestamp},{str(k).replace(',', ';')}\n")
    DHAKE.reset_object()


if __name__ == '__main__':
    for i in range(100):
        try:
            init_participants(i)
            print(f"{i}: Acierto")
        except Exception as e:
            print(f"{i}: Fallo")
