from crawler.request_manager import check_services_status, parse_leak_data
from leak_collector.scripts._monitor_mozilla import _monitor_mozilla

check_services_status()

if __name__ == "__main__":
    parse_sample = _monitor_mozilla()
    parsed_data, raw_parse_mapping = parse_leak_data(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample)
    print(parsed_data)
