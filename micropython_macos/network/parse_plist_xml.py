from uio import StringIO
import xmltok


def read_tag(tokenizer, tok):

    if tok[0] == xmltok.ATTR:
        return

    tag_name = tok[1][1]
    if tag_name == 'array':
        return read_array(tokenizer)
    elif tag_name == 'dict':
        return read_dict(tokenizer)
    elif tag_name in ['true', 'false']:
        return read_boolean(tokenizer, tag_name)
    elif tag_name in ['integer', 'string', 'data']:
        return read_scalar(tokenizer, tag_name)
    elif tag_name == 'plist':
        return read_plist(tokenizer)
    else:
        raise NotImplementedError(tok)


def read_key(tokenizer):
    output = None
    for tok in tokenizer:
        if tok[0] == xmltok.END_TAG:
            tag_name = tok[1][1]
            if tag_name == 'key':
                return output
        if tok[0] == 'TEXT':
            output = tok[1]
            continue


def read_boolean(tokenizer, tag_name):
    next_tok = next(tokenizer)
    if next_tok[0] != xmltok.END_TAG or next_tok[1][1] != tag_name:
        raise ValueError

    return True if tag_name == 'true' else False


def read_scalar(tokenizer, tag_name):
    output = None
    for tok in tokenizer:
        if tok[0] == xmltok.END_TAG:
            if tok[1][1] == tag_name:
                if tag_name == 'integer':
                    return int(output)
                return output
        if tok[0] == xmltok.TEXT:
            output = tok[1]

    raise ValueError('Go to end of tokenizer but did not get end tag')


def read_plist(tokenizer):
    output = None
    for tok in tokenizer:
        if tok[0] == xmltok.END_TAG:
            tag_name = tok[1][1]
            if tag_name == 'plist':
                return output
        if not output:
            output = read_tag(tokenizer, tok)
        else:
            raise ValueError()

    raise ValueError('Go to end of tokenizer but did not get end tag')


def read_dict(tokenizer):
    output = {}
    key = None
    for tok in tokenizer:
        if tok[0] == xmltok.END_TAG:
            tag_name = tok[1][1]
            if tag_name == 'dict':
                return output

            raise ValueError('Bad end tag')

        if tok[0] == xmltok.START_TAG:
            tag_name = tok[1][1]
            if tag_name == 'key':
                if key:
                    raise ValueError('key tag nested in key')
                key = read_key(tokenizer)
                continue

            if key is None:
                raise ValueError()

            output[key] = read_tag(tokenizer, tok)
            key = None

    raise ValueError('Go to end of tokenizer but did not get end tag')


def read_array(tokenizer):
    output = []

    for tok in tokenizer:
        if tok[0] == xmltok.END_TAG:
            tag_name = tok[1][1]
            if tag_name == 'array':
                return output
            raise ValueError('Bad end tag')

        if tok[0] == xmltok.START_TAG:
            output.append(read_tag(tokenizer, tok))

    raise ValueError('Go to end of tokenizer but did not get end tag')


def parse(xml_str):
    LINES_TO_STRIP = [
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">'
    ]
    for line in LINES_TO_STRIP:
        xml_str = xml_str.replace(line, '')
    tokenizer = xmltok.tokenize(StringIO(xml_str))
    for tok in tokenizer:
        if tok[0] == xmltok.START_TAG:
            return read_tag(tokenizer, tok)

    raise ValueError('Did not get a start tag')
