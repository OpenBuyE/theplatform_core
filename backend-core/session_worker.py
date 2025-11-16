import time
from services.session_service import SessionService
from services.session_pool_service import SessionPoolService


def main(poll_interval_seconds: int = 5):
    """
    Worker sencillo que:
    - Cada poll_interval_seconds:
        1) Activa sesiones programadas desde sessions_pool (type = 'scheduled').
        2) Procesa sesiones 'open':
            - Marca como 'expired' las que han caducado sin aforo.
            - Cierra + adjudica las que alcanzan aforo dentro de plazo.
        3) Procesa cadenas de sesiones para las que están en 'adjudicated':
            - X23.1 -> X23.2 -> X23.3 desde sessions_pool.
    """
    session_service = SessionService()
    pool_service = SessionPoolService()

    while True:
        try:
            # 1) Activar sesiones programadas (parque de sesiones)
            pool_service.process_scheduled_sessions()

            # 2) Procesar sesiones abiertas (caducidad, cierre, adjudicación)
            session_service.process_open_sessions()

            # 3) Encadenar sesiones para las sesiones adjudicadas
            session_service.process_chains_for_adjudicated_sessions()

        except Exception as e:
            print(f"[WORKER ERROR] {e}")

        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    main()
