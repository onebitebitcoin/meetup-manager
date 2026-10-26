"""링크 미리보기: 대상 페이지를 받아 og 메타를 읽는다. 내부망 접근(SSRF)을 막기 위해 직접 연결한다."""
import http.client
import ipaddress
import socket
import ssl
import time
from html.parser import HTMLParser
from urllib.parse import quote, urljoin, urlsplit

ALLOWED_PORTS = {'http': 80, 'https': 443}
MAX_REDIRECTS = 3
MAX_BYTES = 512 * 1024
TIMEOUT = 3
USER_AGENT = 'Mozilla/5.0 (compatible; HanipLinkPreview/1.0)'
URL_SAFE = "/%:@!$&'()*+,;=-._~?"


class InvalidUrl(ValueError):
    """URL 형식 자체가 틀린 경우."""


class PinnedHTTPConnection(http.client.HTTPConnection):
    """호스트를 다시 조회하지 않고 검사를 마친 IP로 연결한다(DNS rebinding 방지)."""

    def __init__(self, host, ip, **kwargs):
        super().__init__(host, **kwargs)
        self.ip = ip

    def _open_socket(self):
        return socket.create_connection((self.ip, self.port), self.timeout)

    def connect(self):
        self.sock = self._open_socket()


class PinnedHTTPSConnection(PinnedHTTPConnection):
    def connect(self):
        # 인증서와 SNI는 원래 호스트 이름 기준으로 검증한다
        sock = self._open_socket()
        self.sock = ssl.create_default_context().wrap_socket(sock, server_hostname=self.host)


def is_public_ip(value):
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return False
    if ip.version == 6 and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    return not (
        ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
        or ip.is_multicast or ip.is_unspecified or not ip.is_global
    )


def resolve_host(host):
    infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    return list(dict.fromkeys(info[4][0] for info in infos))


def send_request(url, ip, accept='text/html', max_bytes=MAX_BYTES):
    """검사를 마친 ip로 GET 요청을 보내고 (상태 코드, 소문자 헤더, 본문)을 돌려준다. 리다이렉트는 따라가지 않는다.
    accept(예: 'text/html', 'image/')가 content-type에 없으면 본문을 읽지 않는다."""
    parts = urlsplit(url)
    connection_class = PinnedHTTPSConnection if parts.scheme == 'https' else PinnedHTTPConnection
    conn = connection_class(parts.hostname, ip, port=parts.port or ALLOWED_PORTS[parts.scheme], timeout=TIMEOUT)
    deadline = time.monotonic() + TIMEOUT
    try:
        # 한글 파일명처럼 ASCII가 아닌 경로는 퍼센트 인코딩한다(이미 인코딩된 %XX는 그대로 둔다)
        path = quote(parts.path or '/', safe=URL_SAFE)
        if parts.query:
            path = f'{path}?{quote(parts.query, safe=URL_SAFE)}'
        conn.request('GET', path, headers={
            'Host': parts.netloc.rpartition('@')[2], 'User-Agent': USER_AGENT,
            'Accept': '*/*' if accept.endswith('/') else accept, 'Accept-Encoding': 'identity',
        })
        response = conn.getresponse()
        headers = {key.lower(): value for key, value in response.getheaders()}
        if response.status in (301, 302, 303, 307, 308) or accept not in headers.get('content-type', '').lower():
            return response.status, headers, b''
        body = b''
        while len(body) < max_bytes and time.monotonic() < deadline:
            chunk = response.read(min(8192, max_bytes - len(body)))
            if not chunk:
                break
            body += chunk
        return response.status, headers, body
    finally:
        conn.close()


def check_url(url):
    """검사를 통과하면 (parts, 연결할 ip)를, 거부되면 None을 돌려준다."""
    parts = urlsplit(url)
    if parts.scheme not in ALLOWED_PORTS or not parts.hostname:
        return None
    try:
        port = parts.port
    except ValueError:
        return None
    if port is not None and port != ALLOWED_PORTS[parts.scheme]:
        return None
    try:
        ips = resolve_host(parts.hostname)
    except (OSError, UnicodeError):
        return None
    if not ips or not all(is_public_ip(ip) for ip in ips):
        return None
    return parts, ips[0]


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.title = ''
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title = True
        elif tag == 'meta':
            attrs = dict(attrs)
            key = (attrs.get('property') or attrs.get('name') or '').lower()
            content = attrs.get('content')
            if key and content and key not in self.meta:
                self.meta[key] = content.strip()

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def decode_body(body, content_type):
    charset = 'utf-8'
    for token in content_type.split(';')[1:]:
        key, _, value = token.partition('=')
        if key.strip().lower() == 'charset' and value.strip():
            charset = value.strip().strip('"\'')
    try:
        return body.decode(charset, errors='replace')
    except LookupError:
        return body.decode('utf-8', errors='replace')


def absolute_image(base_url, value):
    if not value:
        return None
    image = urljoin(base_url, value)
    return image if urlsplit(image).scheme in ('http', 'https') else None


def parse_preview(url, html):
    parser = MetaParser()
    parser.feed(html)
    meta = parser.meta
    title = meta.get('og:title') or parser.title.strip()
    if not title:
        return None
    return {
        'url': url,
        'title': title[:200],
        'description': (meta.get('og:description') or meta.get('description') or '')[:300],
        'image': absolute_image(url, meta.get('og:image')),
        'site_name': meta.get('og:site_name', '')[:100],
    }


def fetch(url, accept, max_bytes=MAX_BYTES):
    """리다이렉트를 따라가며 (content-type, 본문)을 돌려준다. 실패·거부·다른 형식은 None, URL 형식이 틀리면 InvalidUrl."""
    parts = urlsplit(url)
    if parts.scheme not in ALLOWED_PORTS or not parts.hostname:
        raise InvalidUrl(url)
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        checked = check_url(current)
        if checked is None:
            return None
        try:
            status, headers, body = send_request(current, checked[1], accept, max_bytes)
        except (OSError, http.client.HTTPException, UnicodeError):
            return None
        if status in (301, 302, 303, 307, 308):
            location = headers.get('location')
            if not location:
                return None
            current = urljoin(current, location)
            continue
        content_type = headers.get('content-type', '')
        if status != 200 or accept not in content_type.lower():
            return None
        return content_type, body
    return None


def fetch_preview(url):
    """미리보기 dict를 돌려준다. 실패·거부·비HTML은 None, URL 형식이 틀리면 InvalidUrl."""
    result = fetch(url, 'text/html')
    if result is None:
        return None
    content_type, body = result
    return parse_preview(url, decode_body(body, content_type))
