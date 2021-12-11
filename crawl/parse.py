import functools

from bs4 import BeautifulSoup, element

bs_parser = 'html5lib'


def try_deco(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AttributeError as e:
            return None

    return wrapper


@try_deco
def get_options(q: element) -> list[str]:
    return [li.find('label').text for li in q.find('ul').find_all('li')]


@try_deco
def get_dropdown_options(q: element) -> list[str]:
    return [opt.text for opt in q.find('select').find_all('option')]


@try_deco
def get_labels_tmpl(q: element) -> list[str]:
    return [
        e.find('label').text
        for e in q.find_all(class_='topic__type-items')
    ]


class FormBuilder:
    def __init__(self, title: str):
        self.next_oid = 0
        self.title = title
        self.questions = []

    def get_oid(self):
        r = self.next_oid
        self.next_oid += 1
        return r

    def make_options(self, texts: list[str]) -> list[dict[str]]:
        return [{
            'id': self.get_oid(),
            'text': s
        } for s in texts]

    def add_question(self, ty: str, title: str, **kw):
        r = {
            'type': ty,
            'id': len(self.questions),
            'title': title,
        }
        self.questions.append(r | kw)

    def build(self) -> dict[str]:
        return {
            'title': self.title,
            'body': {
                'questions': self.questions
            }
        }


def parse_vj(html: str) -> dict[str]:
    soup = BeautifulSoup(html, bs_parser)
    soup = soup.find('div', class_='survey')
    title = soup.find('h1').text.strip()
    if title.endswith('[复制]'):
        title = title[:-4]
    ctx = FormBuilder(title)
    desc = soup.find('div', class_='surveydescription').text.strip()
    if desc:
        ctx.add_question('comment', desc)
    for e in soup.find_all(class_='div_question'):
        title = e.find(class_='div_title_question').text.strip()
        ext = {}
        if title.endswith('【多选题】'):
            ty = 'checkbox'
            ext['options'] = ctx.make_options(get_options(e))
        elif e.find('textarea') is not None:
            ty = 'input'
        elif opts := get_dropdown_options(e):
            ty = 'dropdown'
            ext['options'] = ctx.make_options(opts)
        elif opts := get_options(e):
            ty = 'radio'
            ext['options'] = ctx.make_options(opts)
        else:
            ty = 'comment'

        ctx.add_question(ty, title, **ext)

    return ctx.build()


def parse_xz(html: str) -> dict[str]:
    soup = BeautifulSoup(html, bs_parser)
    title = soup.find('h1', class_='htitle').text.strip()
    ctx = FormBuilder(title)
    for e in soup.find('div', class_='topic__type-body').find_all('fieldset'):
        title = e.find('legend').text.strip()
        labels = get_labels_tmpl(e)
        ext = {}
        expand = False
        if e.find(class_='select__type'):
            ty = 'dropdown'
            # options are not rendered
            ext['options'] = ctx.make_options(labels)
        elif e.find(class_='text__type'):
            ty = 'input'
            expand = True
        elif e.find(class_='textarea__type'):
            ty = 'text'
            expand = True
        elif e.find(class_='radio__type'):
            ty = 'radio'
            ext['options'] = ctx.make_options(labels)
        elif e.find(class_='checkbox__type'):
            ty = 'checkbox'
            ext['options'] = ctx.make_options(labels)
            # TODO: parse limits
        else:
            ty = 'comment'

        if expand and labels:
            ctx.add_question(ty, title + ' ' + labels[0])
            for s in labels[1:]:
                ctx.add_question(ty, s)
        else:
            ctx.add_question(ty, title, **ext)

    return ctx.build()
