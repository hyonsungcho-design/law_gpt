#!/usr/bin/env python3
"""Search law.go.kr and save selected records and official attachments."""
import argparse, datetime, json, os, re, sys, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

BASE = 'https://www.law.go.kr'
TARGETS = {'eflaw': ('law', '법령일련번호', '법령명한글'), 'admrul': ('admrul', '행정규칙일련번호', '행정규칙명'), 'licbyl': ('licbyl', '별표일련번호', '별표명'), 'admbyl': ('admrulbyl', '별표일련번호', '별표명')}
class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)
def check_url(url):
    u = urllib.parse.urlsplit(url)
    if u.scheme != 'https' or u.hostname not in ('www.law.go.kr', 'law.go.kr') or u.username or u.password or u.port not in (None, 443):
        raise ValueError('허용되지 않은 다운로드 주소')
def get(url):
    check_url(url)
    with urllib.request.build_opener(SafeRedirect()).open(urllib.request.Request(url, headers={'User-Agent':'law-skill/1.0'}), timeout=40) as r:
        data = r.read(30_000_001)
        if len(data) > 30_000_000: raise ValueError('응답 크기 제한 초과')
        return data, r.headers.get_content_type()
def api(path, params):
    oc = os.environ.get('LAW_API_OC', '').strip()
    if not oc: raise ValueError('LAW_API_OC 환경변수에 발급받은 API 인증값을 설정하세요.')
    url = BASE + '/DRF/' + path + '?' + urllib.parse.urlencode(dict(params, OC=oc, type='XML'))
    data, _ = get(url)
    try: root = ET.fromstring(data)
    except ET.ParseError: raise ValueError('API가 유효한 XML을 반환하지 않았습니다. 인증 및 서비스 상태를 확인하세요.')
    if root.tag.lower() in ('error', 'result', 'errorresponse', 'response') or root.find('.//error') is not None:
        raise ValueError('API 오류 응답: ' + ' '.join(root.itertext())[:400].replace(oc, '[인증값]'))
    return root, data
def safe(s):
    s = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', str(s)).strip(' .')[:90]
    return s if s and s.upper() not in ('CON','PRN','AUX','NUL') else 'item'
def field(node, key):
    return (node.findtext(key) or '').strip()
def search(args):
    params = dict(target=args.target, query=args.query, search=args.search, display=args.limit, page=args.page)
    if args.target == 'eflaw': params['nw'] = '3'
    root, _ = api('lawSearch.do', params)
    if root.find('totalCnt') is None: raise ValueError('예상하지 못한 API 검색 응답입니다: ' + root.tag)
    tag, ident, title = TARGETS[args.target]
    rows = []
    for node in root.findall('.//' + tag):
        d = {child.tag: no_oc((child.text or '').strip()).replace(os.environ['LAW_API_OC'].strip(), '[인증값]') for child in node if len(child) == 0}
        if field(node, ident): rows.append(d)
    print(json.dumps({'target':args.target, 'query':args.query, 'total':field(root,'totalCnt'), 'page':args.page, 'results':rows}, ensure_ascii=False, indent=2))
def absolute_link(raw):
    url = urllib.parse.urljoin(BASE, raw.strip())
    p = urllib.parse.urlsplit(url)
    if p.scheme == 'http' and p.hostname in ('www.law.go.kr','law.go.kr'): url = urllib.parse.urlunsplit(('https',p.netloc,p.path,p.query,p.fragment))
    check_url(url)
    return url
def no_oc(s):
    p=urllib.parse.urlsplit(s)
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True) if k.lower() != 'oc']
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(q),'') )
def form(args):
    if not re.fullmatch(r'\d+', args.id): raise ValueError('id는 검색 결과의 숫자 일련번호여야 합니다.')
    root, _ = api('lawSearch.do', {'target':args.target,'query':args.query,'search':args.search,'display':100,'page':args.page})
    tag, ident, _ = TARGETS[args.target]
    matches=[n for n in root.findall('.//'+tag) if field(n,ident)==args.id]
    if len(matches)!=1: raise ValueError('해당 검색 페이지에서 일련번호를 찾지 못했습니다.')
    node=matches[0]; folder=Path(args.output)/'별표서식'/(safe(args.name)+'_'+args.id)
    folder.mkdir(parents=True,exist_ok=False)
    oc=os.environ['LAW_API_OC'].strip()
    meta={n.tag: no_oc((n.text or '').strip()).replace(oc,'[인증값]') for n in node if len(n)==0}
    result={'조회일':datetime.date.today().isoformat(),'검색어':args.query,'검색범위':args.search,'검색결과':meta,'첨부':[]}
    for n in node:
        if '파일링크' not in n.tag or not n.text or not n.text.strip(): continue
        entry={'종류':n.tag,'출처':no_oc(n.text.strip())}
        try:
            url=absolute_link(n.text); data,ct=get(url)
            if ct in ('text/html','application/json','application/xml','text/xml') or data.lstrip().lower().startswith((b'<!doctype html',b'<html')): raise ValueError('파일 대신 오류 또는 웹페이지가 반환됨')
            ext=Path(urllib.parse.urlsplit(url).path).suffix.lower()
            if ext not in ('.hwp','.hwpx','.pdf','.doc','.docx','.xls','.xlsx','.zip'): ext='.pdf' if data.startswith(b'%PDF') else '.hwp' if data.startswith(bytes.fromhex('d0cf11e0')) else '.bin'
            filename='서식_'+str(len(result['첨부'])+1).zfill(3)+ext
            (folder/filename).write_bytes(data); entry.update({'파일':filename,'상태':'저장'})
        except Exception as e: entry.update({'상태':'실패','사유':str(e).replace(oc,'[인증값]')})
        result['첨부'].append(entry)
    (folder/'출처.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
def collect(args):
    if not re.fullmatch(r'\d+', args.id): raise ValueError('id는 검색 결과의 숫자 일련번호여야 합니다.')
    params = {'target':args.target, 'MST' if args.target == 'eflaw' else 'ID':args.id}
    if args.target == 'eflaw':
        if not re.fullmatch(r'\d{8}', args.effective or ''): raise ValueError('법령은 검색 결과 시행일자 8자리(--effective)가 필요합니다.')
        params['efYd']=args.effective
    root, raw = api('lawService.do', params)
    expected = ('법령',) if args.target == 'eflaw' else ('AdmRulService','행정규칙')
    if root.tag not in expected: raise ValueError('예상하지 못한 본문 응답: ' + root.tag)
    folder = Path(args.output) / ('법령' if args.target == 'eflaw' else '행정규칙') / (safe(args.name) + '_' + args.id)
    folder.mkdir(parents=True, exist_ok=False)
    # API response may contain the caller's OC in detail links. Remove it before writing.
    oc=os.environ['LAW_API_OC'].strip()
    for node in root.iter():
        if node.text and oc in node.text: node.text = node.text.replace(oc, '[인증값]')
    ET.ElementTree(root).write(folder/'원문.xml', encoding='utf-8', xml_declaration=True)
    manifest = {'제목':args.name,'종류':args.target,'일련번호':args.id,'시행일':args.effective,'조회일':datetime.date.today().isoformat(),'본문':'원문.xml','출처':BASE+'/DRF/lawService.do?'+urllib.parse.urlencode(params), '첨부':[]}
    links=[]
    for node in root.iter():
        if ('파일링크' in node.tag or node.tag == '첨부파일링크') and node.text and node.text.strip(): links.append((node.tag,node.text.strip()))
    for i,(tag,link) in enumerate(dict.fromkeys(links),1):
        entry={'종류':tag,'출처':no_oc(link)}
        try:
            url=absolute_link(link); data, content_type=get(url)
            if content_type in ('text/html','application/json','application/xml','text/xml') or data.lstrip().lower().startswith((b'<!doctype html',b'<html')): raise ValueError('파일 대신 오류 또는 웹페이지가 반환됨')
            ext=Path(urllib.parse.urlsplit(url).path).suffix.lower()
            if ext not in ('.hwp','.hwpx','.pdf','.doc','.docx','.xls','.xlsx','.zip'):
                ext = '.pdf' if data.startswith(b'%PDF') else '.hwp' if data.startswith(bytes.fromhex('d0cf11e0')) else '.bin'
            filename=f'첨부_{i:03d}{ext}'
            (folder/filename).write_bytes(data); entry.update({'파일':filename,'상태':'저장'})
        except Exception as e: entry.update({'상태':'실패','사유':str(e).replace(oc,'[인증값]')})
        manifest['첨부'].append(entry)
    (folder/'출처.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
def main():
    p=argparse.ArgumentParser(description='국가법령정보센터 검색 및 자료 저장')
    sub=p.add_subparsers(dest='cmd',required=True)
    s=sub.add_parser('search'); s.add_argument('--target',choices=TARGETS,required=True); s.add_argument('--query',required=True); s.add_argument('--search',type=int,choices=[1,2,3],default=1); s.add_argument('--limit',type=int,choices=range(1,101),default=20); s.add_argument('--page',type=int,default=1); s.set_defaults(func=search)
    c=sub.add_parser('collect'); c.add_argument('--target',choices=['eflaw','admrul'],required=True); c.add_argument('--id',required=True); c.add_argument('--name',required=True); c.add_argument('--effective'); c.add_argument('--output',required=True); c.set_defaults(func=collect)
    f=sub.add_parser('form'); f.add_argument('--target',choices=['licbyl','admbyl'],required=True); f.add_argument('--query',required=True); f.add_argument('--search',type=int,choices=[1,2,3],default=1); f.add_argument('--page',type=int,default=1); f.add_argument('--id',required=True); f.add_argument('--name',required=True); f.add_argument('--output',required=True); f.set_defaults(func=form)
    a=p.parse_args()
    try: a.func(a)
    except Exception as e: print('오류: '+str(e).replace(os.environ.get('LAW_API_OC') or '\0','[인증값]'),file=sys.stderr); sys.exit(1)
if __name__ == '__main__': main()
