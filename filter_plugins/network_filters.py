import ipaddress

def first_address(network):
    return ipaddress.ip_network(network).network_address + 1

class FilterModule(object):
    def filters(self):
        return {
            'first_address': first_address
        }
