from crawler.request_manager import check_services_status, init_services
from crawler.request_parser import RequestParser
from leak_collector.scripts._gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad import \
    _gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad

init_services()
check_services_status()

if __name__ == "__main__":
    parse_sample = _gunrabxbig445sjqa535uaymzerj6fp4nwc6ngc2xughf2pedjdhk4ad()
    parser = RequestParser(proxy={"server": "socks5://127.0.0.1:9150"}, model=parse_sample).parse()
    print(parse_sample.card_data)
    print(parse_sample.entity_data)
