# author: Ruofei Du
# This script builds the website by parsing the markdown text files and json files in data/
# This script also includes common files such as header and footer, and embed them into the final HTML
from xml.etree import ElementTree as ET
from scripts.types import *
import re, json
import markdown

re_markdown = re.compile("<!--\s*include\s*:\s*data\/(.+)\.txt\s*?-->")
re_html = re.compile("<!--\s*include\s*:\s*(.+)\.html\s*?-->")

html, md, data, people = {}, {}, {}, {}


def remove_comments(html):
    return re.sub("(<!--.*?-->)", "", html, flags=re.DOTALL)


def remove_blank_lines(html):
    return re.sub("\n\s*\n", "\n", html, flags=re.DOTALL)


def read_str(file_name):
    with open(file_name, 'r') as f:
        s = ''.join(f.readlines())
    return s


def read_html(file_name):
    s = read_str(file_name + '.html')
    while re_markdown.search(s):
        key = re_markdown.search(s).groups()[0]
        print("%s\t<=\t%s.txt" % (file_name, key))
        s = re.sub("<!--\s*include\s*:\s*data\/" + key + "\.txt\s*-->", md[key], s, flags=re.DOTALL)
    while re_html.search(s):
        key = re_html.search(s).groups()[0]
        print("%s\t<=\t%s.html" % (file_name, key))
        s = re.sub("<!--\s*include\s*:\s*" + key + "\.html\s*-->", html[key], s, flags=re.DOTALL)
    return s


def read_content(file_name):
    s = read_html(file_name + '.content')
    while re_markdown.search(s):
        key = re_markdown.search(s).groups()[0]
        print("%s\t<=\t%s.txt" % (file_name, key))
        s = re.sub("<!--\s*include\s*:\s*data\/" + key + "\.txt\s*-->", md[key], s, flags=re.DOTALL)
    while re_html.search(s):
        key = re_html.search(s).groups()[0]
        print("%s\t<=\t%s.html" % (file_name, key))
        s = re.sub("<!--\s*include\s*:\s*" + key + "\.html\s*-->", html[key], s, flags=re.DOTALL)

    s = remove_comments(s)
    s = remove_blank_lines(s)
    return s


def build(file_name):
    print("---")
    s = read_content(file_name)
    # Build to separate folders
    # out_file = "%s.html" % file_name if file_name == 'index' else "%s/index.html" % file_name
    # Build to the root
    out_file = "%s.html" % file_name
    with open(out_file, 'w') as f:
        f.write('<!-- Automatically generated by build.py from MarkDown files -->\n')
        f.write('<!-- Augmentarium | UMIACS | University of Maryland, College Park -->\n')
        f.write(s)


def read_markdown(file_name):
    s = read_str('data/' + file_name + '.txt')
    s = markdown.markdown(s)
    return s


def read_data(file_name):
    return json.load(open('data/' + file_name + '.json'))


def write_bib(b):
    filename = 'bib/' + b['bib'] + '.bib'
    if 'http' in filename:
        return
    print(filename)
    TAB = "&nbsp&nbsp&nbsp&nbsp"

    with open(filename, 'w') as f:
        f.write('@%s{%s,<br/>\n' % (b['type'], b['bibname']))
        f.write(TAB + 'title = "%s",<br/>\n' % b['title'])
        author_list = b['author']
        if 'authorb' in b:
            author_list = b['authorb']
        if 'bibauthor' in b:
            author_list = b['bibauthor']
        f.write(TAB + 'author = {%s},<br/>\n' % author_list)
        f.write(TAB + '%s = {%s},<br/>\n' % ('journal' if b['type'] == 'article' else 'booktitle', b['booktitle']))
        f.write(TAB + 'year = {%s},<br/>\n' % b['year'])
        if b['month']:
            f.write(TAB + 'month = {%s},<br/>\n' % b['month'])
        if b['day']:
            f.write(TAB + 'day = {%s},<br/>\n' % b['day'])
        if b['type'] == 'article':
            f.write(TAB + 'volume = {%s},<br/>\n' % b['volume'])
            f.write(TAB + 'number = {%s},<br/>\n' % b['number'])
        if b['editor']:
            f.write(TAB + 'editor = {%s},<br/>\n' % b['editor'])
        if b['location']:
            f.write(TAB + 'location = {%s},<br/>\n' % b['location'])
        elif b['address']:
            f.write(TAB + 'location = {%s},<br/>\n' % b['address'])
        if b['publisher']:
            f.write(TAB + 'publisher = {%s},<br/>\n' % b['publisher'])
        if b['series']:
            f.write(TAB + 'series = {%s},<br/>\n' % b['series'])
        if b['keywords']:
            f.write(TAB + 'keywords = {%s},<br/>\n' % b['keywords'])
        f.write(TAB + 'pages = {%s}<br/>\n' % b['pages'])
        f.write('}<br/>\n')

    filename = 'bib/' + b['bib'] + '.apa'
    print(filename)

    with open(filename, 'w') as f:
        f.write('%s.' % b['apauthor'])
        f.write(' (%s).<br/> ' % (b['year']))
        f.write('%s.' % b['title'])
        f.write(' <br/><i>%s</i>' % b['booktitle'])
        if b['type'] == 'article':
            f.write(', %s(%s)' % (b['volume'], b['number']))
        f.write(', %s' % b['pages'].replace('--', '-').replace(' ', ''))


def write_data_to_markdown(file_name):
    LINE_MEDIA = '* *%s*, **[%s](%s)**, %s%s %s, %s.\n'
    LINE_STUDENTS = '<div class="2u 12u$(medium) center"><span class="image fit">' \
                    '<a href="%s" target="_blank"><img src="photos/%s" alt="%s" class="face"/></a></span>' \
                    '<h4 class="center"><a href="%s" target="_blank" class="name">%s</a></h4></div>\n'

    # (m['image'], m['title'], m['url'], m['title'], m['author'], m['booktitle'], m['keywords'], m['url'],
    # m['video'], m['code'], m['slides'], m['apa'], m['bib']  )
    LINE_PAPERS = '<div class="3u 12u$(medium)"><span class="image fit">' \
                  '<a href="%s" target="_blank"><img src="teaser/%s" class="pub-pic" alt="%s" /></a></span></div>' \
                  '<div class="9u 12u$(medium) pub-info"><h4><a href="%s" target="_blank">%s</a></h4>' \
                  '<p class="authors">%s</p>' \
                  '<p class="booktitle">%s</p>' \
                  '<p class="keywords">%s</p><br/><br/>' \
                  '<div class="downloads">Download: <a href="%s" target="_blank">[pdf]</a>%s %s%s%s%s%s | ' \
                  'Cite: <a href="%s" class="bibtex">[APA]</a> <a href="%s" class="bibtex">[BibTeX]</a></div>' \
                  '</p></div>'
    LINE_UNPUBLISHED = '<div class="3u 12u$(medium)"><span class="image fit">' \
                       '<img src="teaser/%s" class="pub-pic" alt="%s" /></span></div>' \
                       '<div class="9u 12u$(medium) pub-info"><h4>%s</h4>' \
                       '<p class="authors">%s</p>' \
                       '<p class="booktitle">%s</p>' \
                       '<p class="keywords">%s</p><br/><br/>' \
                       '<div class="downloads">Download: [pdf] %s%s%s | ' \
                       'Cite: <a href="%s" class="bibtex">[APA]</a> <a href="%s" class="bibtex">[BibTeX]</a></div>' \
                       '</p></div>'

    CATEGORY = '### %s\n'
    YEAR = '### %s\n'
    NEW_ROW = '<div class="row">\n'
    NEW_PUB = '<div class="row pub">\n'
    ROW_END = '</div>\n'

    HIDDEN_CATEGORIES = ['Faculty', 'Affiliated Faculty', 'Collaborators']

    with open("data/%s.txt" % file_name, 'w') as f:
        f.write('[comment]: <> (This markdown file is generated from %s.json by build.py)\n' % file_name)
        if file_name == 'media':
            for m in reversed(data['media']):
                f.write(LINE_MEDIA % (
                    m['publisher'], m['title'], m['url'], '(Video) ' if m['video'] else '', m['month'], m['day'],
                    m['year']))
        elif file_name == 'students':
            categories = []
            for m in data['students']:
                m['name'] = m['name'].strip()
                people[m['name']] = m
                if m['category'] not in categories:
                    categories.append(m['category'])
            for c in categories:
                if c in HIDDEN_CATEGORIES:
                    continue
                f.write(CATEGORY % c)
                count = 0
                f.write(NEW_ROW)
                for m in data['students']:
                    if m['category'] == c and m['visible']:
                        if count and count % 5 == 0:
                            f.write(ROW_END)
                            f.write(NEW_ROW)
                        f.write(LINE_STUDENTS % (m['url'], m['photo'], m['name'] + "'s photo", m['url'], m['name']))
                        count += 1
                f.write(ROW_END)
        elif file_name == 'papers':
            years = []
            for m in data['papers']:
                if m['year'] not in years:
                    years.append(m['year'])
                if not m['bib']:
                    m['bib'] = m['bibname']
                authors = m['author'].split(' and')
                m['apauthor'] = ''
                for i, author in enumerate(authors):
                    if i > 0:
                        m['apauthor'] += ', '
                        if i == len(authors) - 1:
                            m['apauthor'] += 'and '
                    m['apauthor'] += author.strip()
                write_bib(m)
                m['url'] = 'papers/' + m['url'] if not 'http' in m['url'] else m['url']
                bib = m['bib']
                m['bib'] = 'bib/' + bib + '.bib'
                m['apa'] = 'bib/' + bib + '.apa'
                if not m['video']:
                    if m['youtube']:
                        m['video'] = m['youtube']
                    else:
                        m['video'] = m['vimeo']
                m['video'] = ' <a href="%s" target="blank">[video]</a>' % m['video'] if m['video'] else ''
                m['code'] = ' <a href="%s" target="blank">[code]</a>' % m['code'] if m['code'] else ''
                m['slides'] = ' <a href="%s" target="blank">[slides]</a>' % m['slides'] if m['slides'] else ''
                if 'web' in m and m['web']:
                    m['web'] = ' <a href="%s" target="blank">[web]</a>' % m['web']
                else:
                    m['web'] = ''
                if 'data' in m and m['data']:
                    m['data'] = ' <a href="%s" target="blank">[data]</a>' % m['data']
                else:
                    m['data'] = ''
                if not m['published']:
                    m['booktitle'] = 'To Appear In ' + m['booktitle']
                    m['url'] = ''
                if m['doi']:
                    m['doi'] = ' <a href="https://doi.org/%s" target="_blank">[doi]</a>' % m['doi']
                m['author'] = ''
                for i, author in enumerate(authors):
                    if i > 0:
                        if len(authors) > 2:
                            m['author'] += ', '
                        else:
                            m['author'] += ' '
                        if i == len(authors) - 1:
                            m['author'] += 'and '
                    a = author.strip()
                    if a in people:
                        m['author'] += '<a href="%s">%s</a>' % (people[a]['url'], a)
                    else:
                        m['author'] += a
                if m['keywords']:
                    m['keywords'] = "keywords: %s" % m['keywords']
                m['keywords'] += '<br/><br/>'
                if m['published']:
                    pages = m['pages'].replace('--', ',')
                    pages = pages.replace('-', ',')
                    pages = pages.split(',')
                    # print(m['title'])
                    # print(pages)
                    if len(pages) == 2:
                        m['pstart'] = pages[0].strip()
                        m['pend'] = pages[1].strip()
                    if m['type'] == 'article':
                        if len(pages) == 2:
                            m['booktitle'] += ". Vol. %s, No. %s, pp. %s-%s" % (
                                m['volume'], m['number'], m['pstart'], m['pend'])
                        else:
                            m['booktitle'] += ". Vol. %s, No. %s." % (m['volume'], m['number'])
                    else:
                        if len(pages) == 2:
                            m['booktitle'] += ". pp. %s-%s" % (m['pstart'], m['pend'])
                m['booktitle'] += ', %s.' % m['year']
                if m['award']:
                    m['booktitle'] += '<br/><span class="award">%s</span>' % m['award']
                    if 'news' in m:
                        m['booktitle'] += ' <a href="%s"><span class="news">News</span></a>' % m['news']

            for y in sorted(years, reverse=True):
                # f.write(YEAR % y)
                count = 0
                for m in data['papers']:
                    if m['year'] == y and m['visible']:
                        f.write(NEW_PUB)
                        if m['published']:
                            f.write(LINE_PAPERS % (
                                m['url'], m['image'], m['title'], m['url'], m['title'], m['author'], m['booktitle'],
                                m['keywords'],
                                m['url'], m['doi'], m['video'], m['code'], m['slides'], m['web'], m['data'], m['apa'],
                                m['bib']))
                        else:
                            f.write(LINE_UNPUBLISHED % (
                                m['image'], m['title'], m['title'], m['author'], m['booktitle'],
                                m['keywords'], m['video'], m['code'], m['slides'], m['apa'], m['bib']))
                        f.write(ROW_END)
                        count += 1


html_files = ['header', 'footer', 'contact', 'menu', 'sidebar', 'banner']
data_files = ['media', 'students', 'papers']
md_files = ['bio', 'nav', 'menu', 'media', 'activities', 'students', 'ungrads', 'papers']
build_files = ['index', 'media', 'activities', 'group', 'publications']

# First, parse Json Data and write to Markdown files
for f in data_files:
    data[f] = read_data(f)
for m in data['media']:
    m['title'] = smart_title(m['title'])
for f in data_files:
    write_data_to_markdown(f)

# Next, read and parse HTML and MARKDOWN file for including
for f in md_files:
    md[f] = read_markdown(f)
for f in html_files:
    html[f] = read_html(f)

# Finally, generate combined files
for f in build_files:
    build(f)
