from zeroconf import ServiceBrowser, ServiceListener, Zeroconf, ServiceInfo
class mdns:
    """
    # mDNS Service Listener and Publisher.
    # Usage:-
    # ==================

    # to announce a service
        import mdns
        mdns = mdns.mdns()
        service_name = 'this service is from the master casheer computer'
        service_info = {'n': 'dummy_service_info'}
        mdns.publish(service_name, service_info)
        input('>>> ') # wait
        mdns.unpublish(service_name) # unpublish that service

    # to listen to others' published services
        import mdns
        mdns = mdns.mdns()
        def onadd(name, info):
            #handle event: on service add
            print('Service added:')
            print('    name:', name)
            print('    info:', info)

        def onupdate(name, info):
            #handle event: on service update
            print('Service updated:')
            print('    name:', name)
            print('    info:', info)

        def onremove(name):
            #handle event: on service remove
            print('removed:', name)

        mdns.listen(onadd=onadd, onupdate=onupdate, onremove=onremove)
        # mdns.listener['onadd'] = another_def # to change listener event handler def
        input('>>> ') # wait
        mdns.unlisten() # to stop listening
    """
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.published_services = {}
        self.listening = False
    
    def publish(self, name : str, info : dict, port=9999) -> None:
        #  announcing a service
        if name in self.published_services:
            raise Exception('Service name already exists in the published services.')
        service_info = ServiceInfo(
            type_="_http._tcp.local.",
            name=f"{name}._http._tcp.local.",
            addresses=b'\n\x00\x01\x02', # b'\n\x00\x01\x02' is socket.inet_aton("10.0.1.2")
            port=port,
            weight=0,
            priority=0,
            properties=info,
        )
        self.published_services[name] = service_info
        self.zeroconf.register_service(service_info)
    
    def unpublish(self, name : str) -> None:
        if not name in self.published_services:
            raise Exception('Service name not found in the published services.')
        self.zeroconf.unregister_service(self.published_services[name])
        del self.published_services[name]
        
    def listen(self, onadd=None, onupdate=None, onremove=None):
        # listen for services
        # onadd , onupdate, onremove := def where events are catched & is called with: def(service_name, service_info)
        if (onadd, onupdate, onremove) == (None, None, None): return
        if self.listening: raise Exception('already listening.')
        self.listening = True
        self.listener = {
            'zeroconf': Zeroconf(),
            'serviceBrowser': None,
            'onadd': onadd,
            'onupdate': onupdate,
            'onremove': onremove,
        }
        class listener(ServiceListener):
            def add_service(_self, zc: Zeroconf, type_: str, name: str) -> None:
                if self.listener['onadd']: self.listener['onadd'](name[:-18], mdns.clean_dict(zc.get_service_info(type_, name).properties))
                #NOTE: [:-18] is to remove '._http._tcp.local.' from service name
                #print(f"Service [{name}] added")
                #print(f"service info: [{info}]")
                
            def update_service(_self, zc: Zeroconf, type_: str, name: str) -> None:
                if self.listener['onupdate']: self.listener['onupdate'](name[:-18], mdns.clean_dict(zc.get_service_info(type_, name).properties))
                #print(f"Service [{name}] updated")
                
            def remove_service(_self, zc: Zeroconf, type_: str, name: str) -> None:
                if self.listener['onremove']: self.listener['onremove'](name[:-18])
                #print(f"Service [{name}] removed")
        self.listener['serviceBrowser'] = ServiceBrowser(self.listener['zeroconf'], "_http._tcp.local.", listener())

    def unlisten(self):
        if not self.listening: raise Exception('already not listening.')
        self.listening = False
        self.listener.zeroconf.close()

    def close(self):
        # unregister published services
        for service_name in list(self.published_services.keys()):
            self.zeroconf.unregister_service(self.published_services[service_name])
            del self.published_services[service_name]
        self.zeroconf.close()
        # stop service listener
        if self.listening: self.unlisten()
        
    __del__ = close

    @staticmethod
    def clean_dict(_dict):
        # converts this: {b'n': b'dummy_service_info'}
        # into this: {'n': 'dummy_service_info'}
        new_dict = {}
        for key in _dict:
            new_dict[key.decode()] = _dict[key].decode()
        return new_dict


if __name__ == '__main__':
    # Testing this module
    print('setting listener')
    import mdns # python module can import itself 
    mdns = mdns.mdns()
    def onadd(name, info):
        print('Service added:')
        print('    name:', name)
        print('    info:', info)
    def o(n): print('Service removed:',n)
    mdns.listen(onadd=onadd)
    mdns.listener['onremove'] = o
    print('publishing the service')
    service_name = 'this service is from the master casheer computer'
    mdns.publish(service_name, {'n': 'dummy_service_info'})
    input('press Enter to exit :>>> ')
    print('unpublishing the service')
    mdns.unpublish(service_name)
    import time
    time.sleep(1)
    exit(0) # all successfull

# Reference:-
#chosen library: https://pypi.org/project/zeroconf/
#implementation for windows: https://stackoverflow.com/questions/10244117/how-can-i-find-the-ip-address-of-a-host-using-mdns
#alternative: https://github.com/DynamicDevices/pybonjour-python3
    


    
