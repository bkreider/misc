import logging
import socket

LOGGER=logging.getLogger(__name__)

def tcp_port_available(port, interface="0.0.0.0"):
    """Check availability of port by binding to a TCP socket

    Returns:
        - None: Unknown status - permission denied or other failure
        - False: Unable to  bind to port
        - True: Able to bind to port
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((interface, port))
    except Exception as e:
        if e.errno == 13:
            # Ports < 1024 need root access
            LOGGER.debug("Permission denied.")
            return None
        if e.errno == 48:
            # This doesn't mean listening socket, it could be an active
            # client socket in use
            LOGGER.debug("Port %d unavailable" % (port,))
            return False
        else:
            LOGGER.debug("Error scanning port {}: {}".format(port, e))
            return None

    return True

def first_open_port(start, end):
    ports = tcp_port_scan(start, end)

    LOGGER.debug("Available ports: {}".format(ports["open"]))
    open_ports = list(ports["open"])
    open_ports.sort()
    if len(open_ports) > 0:
        return open_ports[0]
    else:
        return None

def tcp_port_scan(start, end):
    open        = set()
    unknown     = set()
    unavailable = set()

    LOGGER.debug("Starting port sweep")
    for port in xrange(start, end+1):
        status = tcp_port_available(port)

        if status is False:
            unavailable.add(port)
        if status is None:
            unknown.add(port)
        if status:
            open.add(port)

    return {"open":        open,
            "unknown":     unknown,
            "unavailable": unavailable}

def main(start, end):
    ports = tcp_port_scan(start, end)

    # Note Unavailble doesn't mean "listening"
    LOGGER.info("Unavailable ports: {unavailable}".format(**ports))

    # Too noisy to printout 60k ports
    #LOGGER.info("Open ports: {open}".format(**ports))
    #LOGGER.info("Unknown ports: {unknown}".format(**ports))

if __name__ == "__main__":
    from muster import logger
    logger.setup_logging()
    main(1, 64000)
