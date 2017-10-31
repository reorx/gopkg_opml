# coding: utf-8

import re
import sys


github_link_regex = re.compile(r'\"(github\.com/[\w-]+/[\w-]+)')


def parse_gopkg_file(filename):
    github_links = set()
    with open(filename, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            # empty line
            if not line:
                continue
            # comment line
            if line[0] == '#':
                continue
            r = github_link_regex.search(line)
            if not r:
                continue
            link = r.groups()[0]
            github_links.add(link)
    return github_links


class GithubOPML(object):
    base_template = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
  <head>
    <title>{title}</title>
  </head>
  <body>
{outline_groups}
  </body>
</opml>"""

    outline_group_template = """<outline text="{title}" title="{title}">
{outlines}
</outline>"""

    outline_template = (
        '<outline type="rss" '
        'text="{text}" '
        'title="{title}" '
        'xmlUrl="{feed_url}" '
        'htmlUrl="{html_url}"/>'
    )

    release_feed_suffix = '/releases.atom'
    master_feed_suffix = '/commits/master.atom'

    def __init__(self, title, links):
        self.title = title
        self.links = links

    def outline_group(self, title, outlines):
        """
        :param outlines: type list
        """
        return self.outline_group_template.format(
            title=title,
            outlines=self.left_pad(outlines, indent_size=1),
        )

    def outline(self, link, feed_suffix):
        """
        for release:
        https://github.com/jinzhu/gorm/releases.atom

        for master:
        https://github.com/getsentry/raven-go/commits/master.atom
        """
        text = link.split('/')[-1]
        return self.outline_template.format(
            text=text,
            title=text,
            feed_url='https://{}{}'.format(link, feed_suffix),
            html_url=link,
        )

    def left_pad(self, s, indent_unit='  ', indent_size=1):
        if isinstance(s, list):
            s = '\n'.join(s)
        indent = indent_unit * indent_size
        return '\n'.join('{}{}'.format(indent, i) for i in s.split('\n'))

    def make_opml(self):
        outline_groups = []
        release_group_items = []
        master_group_items = []

        for link in self.links:
            release_group_items.append(
                self.outline(link, self.release_feed_suffix)
            )
            master_group_items.append(
                self.outline(link, self.master_feed_suffix)
            )

        outline_groups.append(
            self.outline_group('Releases', release_group_items)
        )
        outline_groups.append(
            self.outline_group('Master Commits', master_group_items)
        )

        return self.base_template.format(
            title=self.title,
            outline_groups=self.left_pad(outline_groups, indent_size=2)
        )


def main():
    gopkg_file = sys.argv[1]
    github_links = parse_gopkg_file(gopkg_file)
    #print github_links
    o = GithubOPML('Gopkg Updates', github_links)
    #print o.make_opml()
    opml_file = '.'.join(gopkg_file.split('.')[:-1] + ['opml'])
    print 'write to {}'.format(opml_file)
    with open(opml_file, 'w') as f:
        f.write(o.make_opml())


if __name__ == '__main__':
    main()
