import re

from .hpaste import stringToData, WrongKeyError


cheader = re.compile(b'070707[0-7]{6}[0-7]{6}'
                     b'(?P<mode>[0-7]{6})'
                     b'(?P<uid>[0-7]{6})'
                     b'(?P<gid>[0-7]{6})'
                     b'(?P<nlink>[0-7]{6})'
                     b'(?P<rdev>[0-7]{6})'
                     b'(?P<mtime>[0-7]{11})'
                     b'(?P<namesize>[0-7]{6})'
                     b'(?P<filesize>[0-7]{11})')

ncheader = re.compile(b'(?P<lic>Hou[LN]C)\x1a'
                      b'[0-7]{5}'
                      b'(?P<cpionamelen>[0-9a-fA-F]{5})'
                      b'(?P<time>[0-9a-fA-F]{9})'
                      b'(?P<cpionamehash>[0-9a-fA-F]{9})')

pyimports = re.compile(br'(?:from(?:\s|\\\s)+'
                       br'(?P<from>\w+(?:(?:\\\n\s*)?\.(?:\\\n\s*)?\w+)*)'
                       br'(?:\s|\\\s)+)?'
                       br'import(?:\s|\\\s)+'
                       br'(?P<imp>\w+(?:(?:\\\n\s*)?\.(?:\\\n\s*)?\w+)*(?:(?:\s|\\\s)*,(?:\s|\\\s)*\w+(?:(?:\\\n\s*)?\.(?:\\\n\s*)?\w+)*)*)', re.MULTILINE)  # TODO: this doesnt capture unicode imports as we work with binary


nodeinit = re.compile(b'(\\w+(?:/\\w+)?)\\.init\0(?:type\s+=\s+(\w+))?')


def _lic_type_from_code(code):
    # type: (bytes) -> str
    lic = 'unknown'
    if cheader.match(code):
        lic = 'Commercial'
    else:
        match = ncheader.match(code)
        if match:
            lic = 'Non Commercial' if match.group('lic') == 'HouNC' else 'Limited Commercial'
    return lic


def _scan_for_python_imports(code):
    # type: (bytes) -> set[str]
    imports = set()
    for match in pyimports.finditer(code):
        pref = None
        if match.group('from'):
            pref = match.group('from').decode('UTF-8')
            pref = re.sub(r'(?:\s|\n|\\\s)+', '', pref, re.MULTILINE)

        imps = re.sub(r'(?:\s|\n|\\\s)+', '', match.group('imp').decode('UTF-8'), re.MULTILINE).split(',')
        if pref:
            imps = ['.'.join((pref, imp)) for imp in imps]
        imports.update(imps)
    return imports


def _scan_for_nodes(code):
    # type: (bytes) -> list[(str, str)]
    """
    this is a very approximate crude method
    """
    nodes = []

    lic = _lic_type_from_code(code)
    if lic == 'unknown':
        raise RuntimeError('unknown license type')
    elif lic == 'Commercial':
        header = cheader
    else:
        header = ncheader
    for match in header.finditer(code):
        nmatch = nodeinit.match(code, pos=match.end())
        if nmatch:
            nodes.append((nmatch.group(1).decode('UTF-8'), nmatch.group(2).decode('UTF-8') if nmatch.group(2) else '<N/A>'))
    return nodes


def generate_report_data(s, key=None):
    data, deserializer = stringToData(s, key)
    if data['version'] < 2:
        raise NotImplementedError('legacy snippet formats are not supported')

    if deserializer is None:
        return {'error': 'cannot deserialize data, probably encryption key was not provided'}

    try:
        code = deserializer(data['code'].encode('UTF-8'))  # type: bytes
    except WrongKeyError:
        return {'error': 'cannot deserialize data, wrong encryption key provided'}

    info = {}

    info['license'] = _lic_type_from_code(code)
    info['imports'] = _scan_for_python_imports(code)
    info['nodes'] = _scan_for_nodes(code)

    return info


def _test_scan_for_python_imports():
    text = br'''something
    from ass.pop\
    import\
        mouth , \
        wowus.\
        titus
andmorethings'''
    test = _scan_for_python_imports(text)
    assert test == {'ass.pop.mouth', 'ass.pop.wowus.titus'}, test


def _test_scan_for_nodes():
    text = b'''HouLC\x1a1033600bbf0626e4915092bb9909geo1/merge11.parm\0{
version 0.8
}
HouLC\x1a1033600bbb0626e4915076ac4ae7geo1/merge11.userdata\0\0\0\0\1\0
___Version___\0\0\0\x03\0\x0818.5.408HouLC\x1a1033600bbc0626e491507277fc71geo1/group9.init\0type = groupcreate
matchesdef = 0
HouLC\x1a1033600bbd0626e4915015968140geo1/group9.def\0sopflags sopflags = '''
    test = _scan_for_nodes(text)
    assert test == {'geo1/group9'}, test


if __name__ == '__main__':
    _test_scan_for_python_imports()
    _test_scan_for_nodes()
    print('all tests are fine')
