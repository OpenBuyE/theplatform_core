import time
from services.session_service import SessionService


def main(poll_interval_seconds: int = 5):
    """
    Worker sencillo que:
    - Cada poll_interval_seconds:
        - Busca sesiones 'open'
        - Si alguna está llena, la cierra y ejecuta el motor de adjudicación.
    """
    service = SessionService()

    while True:
        try:
            service.process_open_sessions()
        except Exception as e:
            # En producción, aquí conviene usar un logger avanzado
            print(f"[WORKER ERROR] {e}")
        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    main()
