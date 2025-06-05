from crawler.request_manager import check_services_status, init_services
from crawler.request_parser import RequestParser

from leak_collector.scripts._3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd import _3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd
from leak_collector.scripts._nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad import \
    _nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad
from leak_collector.scripts._weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd import \
    _weg7sdx54bevnvulapqu6bpzwztryeflq3s23tegbmnhkbpqz637f2yd

init_services()
check_services_status()

if __name__ == "__main__":
    parse_sample = _nerqnacjmdy3obvevyol7qhazkwkv57dwqvye5v46k5bcujtfa6sduad()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
