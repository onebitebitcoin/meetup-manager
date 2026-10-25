from unittest import mock

import pytest

from lite import linkpreview

URL = 'https://example.com/post'
HTML = (
    '<html><head><title>기본 제목</title>'
    '<meta name="description" content="기본 설명">'
    '<meta property="og:title" content="OG 제목">'
    '<meta property="og:description" content="OG 설명">'
    '<meta property="og:image" content="/img/a.png">'
    '<meta property="og:site_name" content="예제">'
    '</head><body></body></html>'
)


def html_response(body=HTML, content_type='text/html; charset=utf-8'):
    return 200, {'content-type': content_type}, body.encode('utf-8')


def redirect(location):
    return 302, {'location': location}, b''


@pytest.fixture
def net():
    """DNS 조회와 HTTP 요청을 대체한다. dns는 호스트별 IP 목록, responses는 요청 순서대로 응답."""
    state = {'dns': {}, 'responses': [], 'requests': []}

    def resolve(host):
        return state['dns'].get(host, ['93.184.216.34'])

    def request(url, ip):
        state['requests'].append((url, ip))
        return state['responses'].pop(0)

    with mock.patch.object(linkpreview, 'resolve_host', side_effect=resolve), \
            mock.patch.object(linkpreview, 'send_request', side_effect=request) as req:
        state['request_mock'] = req
        yield state


def get(api_client, auth, member, url=URL):
    return api_client.get('/api/lite/link-preview/', {'url': url}, **auth(member))


def test_og_메타를_파싱한다(api_client, auth, member, net):
    net['responses'] = [html_response()]
    res = get(api_client, auth, member)
    assert res.status_code == 200
    assert res.json()['preview'] == {
        'url': URL, 'title': 'OG 제목', 'description': 'OG 설명',
        'image': 'https://example.com/img/a.png', 'site_name': '예제',
    }


def test_og가_없으면_title과_description으로_대체한다(api_client, auth, member, net):
    body = '<html><head><title>기본 제목</title><meta name="description" content="기본 설명"></head></html>'
    net['responses'] = [html_response(body)]
    preview = get(api_client, auth, member).json()['preview']
    assert preview['title'] == '기본 제목'
    assert preview['description'] == '기본 설명'
    assert preview['image'] is None


def test_og_image가_http가_아니면_null(api_client, auth, member, net):
    body = '<meta property="og:title" content="t"><meta property="og:image" content="javascript:alert(1)">'
    net['responses'] = [html_response(body)]
    assert get(api_client, auth, member).json()['preview']['image'] is None


@pytest.mark.parametrize('ip', ['127.0.0.1', '10.0.0.5', '169.254.169.254', '::1', '192.168.1.1', '0.0.0.0'])
def test_사설_IP로_해석되면_null(api_client, auth, member, net, ip):
    net['dns']['example.com'] = [ip]
    res = get(api_client, auth, member)
    assert res.status_code == 200
    assert res.json() == {'preview': None}
    assert net['requests'] == []


def test_일부라도_사설_IP면_null(api_client, auth, member, net):
    net['dns']['example.com'] = ['93.184.216.34', '10.0.0.5']
    assert get(api_client, auth, member).json() == {'preview': None}


def test_허용되지_않는_포트는_null(api_client, auth, member, net):
    assert get(api_client, auth, member, 'http://example.com:8080/').json() == {'preview': None}
    assert net['requests'] == []


@pytest.mark.parametrize('url', ['ftp://example.com/', 'javascript:alert(1)', 'example.com', '', 'http:///x'])
def test_잘못된_URL은_400(api_client, auth, member, net, url):
    res = get(api_client, auth, member, url)
    assert res.status_code == 400
    assert res.json() == {'error': '링크 주소가 올바르지 않아요'}


def test_리다이렉트를_따라간다(api_client, auth, member, net):
    net['responses'] = [redirect('/final'), html_response()]
    preview = get(api_client, auth, member).json()['preview']
    assert preview['title'] == 'OG 제목'
    assert net['requests'][1][0] == 'https://example.com/final'


def test_리다이렉트로_사설_IP에_가면_null(api_client, auth, member, net):
    net['dns']['internal.test'] = ['10.0.0.5']
    net['responses'] = [redirect('http://internal.test/')]
    assert get(api_client, auth, member).json() == {'preview': None}
    assert len(net['requests']) == 1


def test_리다이렉트_4회_이상이면_null(api_client, auth, member, net):
    net['responses'] = [redirect('/a'), redirect('/b'), redirect('/c'), redirect('/d'), html_response()]
    assert get(api_client, auth, member).json() == {'preview': None}


def test_리다이렉트_3회까지는_허용(api_client, auth, member, net):
    net['responses'] = [redirect('/a'), redirect('/b'), redirect('/c'), html_response()]
    assert get(api_client, auth, member).json()['preview'] is not None


def test_HTML이_아니면_null(api_client, auth, member, net):
    net['responses'] = [html_response('{}', 'application/json')]
    assert get(api_client, auth, member).json() == {'preview': None}


def test_요청_실패는_null(api_client, auth, member, net):
    net['request_mock'].side_effect = OSError('timeout')
    assert get(api_client, auth, member).json() == {'preview': None}


def test_캐시_적중_시_다시_가져오지_않는다(api_client, auth, member, net):
    net['responses'] = [html_response()]
    first = get(api_client, auth, member).json()
    second = get(api_client, auth, member).json()
    assert first == second
    assert net['request_mock'].call_count == 1


def test_null_결과도_캐시한다(api_client, auth, member, net):
    net['responses'] = [html_response('{}', 'application/json')]
    get(api_client, auth, member)
    get(api_client, auth, member)
    assert net['request_mock'].call_count == 1


def test_토큰이_없으면_401(api_client, net):
    res = api_client.get('/api/lite/link-preview/', {'url': URL})
    assert res.status_code == 401
