from crawler.request_manager import check_services_status, init_services
from crawler.request_parser import RequestParser

from leak_collector.scripts._3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd import _3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd

init_services()
check_services_status()

if __name__ == "__main__":
    parse_sample = _3ev4metjirohtdpshsqlkrqcmxq6zu3d7obrdhglpy5jpbr7whmlfgqd()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
