import sys
import socket
import logging
import os.path
import xmlrpclib


from supervisor.xmlrpc import SupervisorTransport


LOGGER=logging.getLogger(__name__)
SUPERVISOR_SOCK="etc/supervisor.sock"


def connect_domain_socket(env_path):
    """Connects to a domain socket using the env_path"""
    path = os.path.join(env_path, SUPERVISOR_SOCK)
    transport = SupervisorTransport(None, None,
                                  serverurl="unix://%s" % (path,))

    # xmlrpc needs a URI that starts with http(s) even if it is a dummy
    dummy_uri = "http://127.0.0.1"
    proxy = xmlrpclib.ServerProxy(dummy_uri, transport)
    return proxy


class DomainSocketSupervisor(object):

    def __init__(self, env_path=sys.exec_prefix):
        """Defaults to current environment as the path to find supervisord"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self._env_path = env_path
        self._conn = connect_domain_socket(env_path)
        try:
            self._construct_methods_from_server()
        except socket.error as e:
            if e.errno == 2:
                self._logger.critical("Cannot find domain socket. Supervisord "
                                      "isn't running or is misconfigured")
            raise

    def list_methods(self):
        return self.system.listMethods()

    def _get_methods(self):
        return self._conn.system.listMethods()

    def _construct_methods_from_server(self):
        """
        Lookup all XML-RPC methods using the system.listMethods()
        call and build up pseudo attributes and methods to allow
        tab-completion and normal python function calls
        """
        # Add actual methods to class
        for method in self._get_methods():
            #self._logger.debug("Adding method {} to class attributes".format(
            #                    method))

            # Methods have namespaces, and Python needs actual objects
            # delmited by ".".  Create dummy objects and assign methods there
            # This only works 2 layers deep:  self.system.listMethods() e.g.
            obj, method_name = method.split(".")

            # create new Dummy or use existing one
            temp = self.__dict__.get(obj, Dummy(obj))

            # add new method to dummy obj
            temp.set_method(method_name, getattr(self._conn, method))
            self.__dict__[obj] = temp


class Dummy(object):
    def __init__(self, name):
        self._name = name

    def set_method(self, name, method):
        self.__dict__[name] = method

    def __getattr__(self, name):
        "Clean attribute error to hide Dummy name"
        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self._name, name))


def main():
    from muster.logger import setup_logging
    setup_logging()

    p = DomainSocketSupervisor()
    p.system.listMethods()

if __name__ == "__main__":
    main()
