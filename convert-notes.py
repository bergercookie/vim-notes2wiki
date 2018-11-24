#!/usr/bin/env python3

""" Scirpt fro converting a vim-notes to vimwiki structure"""
import click
import os
import sys
import re


@click.command()
@click.option('--notes-dir', required=True, help='Path to notes directory')
@click.option('--vw-dir', required=True, help='Path to notes directory')
def main(notes_dir: str, vw_dir: str):
    """Main."""

    # call  covnert_file for all files
    for fname in [f for f in os.listdir(notes_dir) if f.endswith(".md")]:
        print("Converting: {}".format(fname))
        fname_wo_ext = fname.rsplit('.', maxsplit=1)[0]
        fname_wiki = os.path.join(vw_dir, "{}.wiki".format(fname_wo_ext))
        fname_full = os.path.join(notes_dir, fname)
        convert_file(fname_full, fname_wiki)


def convert_file(src: str, dst: str):
    """Convert a file from vim-notes format to vimwiki."""

    # Read
    ###########################################################################
    with open(src, 'r') as fin:
        lines = fin.readlines()

    # Process
    ###########################################################################
    # write note title
    print("lines: ", lines)
    print(lines[0])
    lines[0] = "= {} =\n".format(lines[0].rstrip())

    lines = sed_headers(lines)
    lines = sed_tags(lines)
    lines = sed_bullets(lines)
    lines = sed_snippets(lines)

    # Write
    ###########################################################################
    with open(dst, 'w') as fout:
        fout.writelines(lines)


def sed_headers(lines: list) -> str:
    """Convert Markdown '#' headers to Pandoc = * = headers."""

    for i, line in enumerate(lines):
        m = re.match('(#+) (.*)$', line)
        if m:
            lvl = len(m.group(1))
            s = m.group(2)
            lines[i] = "{0} {1} {0}\n".format('=' * lvl, s)

    return lines


def sed_tags(lines: list) -> str:
    """Convert vim-notes '@' tags to vimwiki :*: tags."""

    for i, line in enumerate(lines):
        m = re.match('@(\w+)$', line)
        if m:
            s = m.group(1)
            lines[i] = ":{0}:\n".format(s)

    return lines

def sed_bullets(lines: list) -> str:
    """Convert vim-notes '•', '◦', '▸' tags to vimwiki :*: tags."""

    bullets_corr = {
        '•': '*',
        '◦': '*',
        '▸': '*',
    }

    # Line must start with these characters (excpet spaces)
    for b_in, b_out in bullets_corr.items():
        lines = [l.replace(b_in, b_out, 1) for l in lines]

    return lines


def sed_snippets(lines: list) -> str:
    """Convert vim-notes code snippets to vimwiki."""

    lines_out = lines

    # find lines that contain ```
    # group them by two, act only on the first ones
    snippet_idxs = [li for li, l in enumerate(lines_out) if "```" in l]
    idx_pairs = [(snippet_idxs[i], snippet_idxs[i+1])
                 for i in range(0, len(snippet_idxs) - 1, 2)]

    for sn_start, sn_end in idx_pairs:
        lines_out[sn_start] = "{{{" + lines_out[sn_start][3:]
        lines_out[sn_end] = "}}}" + "\n"

    return lines_out


if __name__ == '__main__':
    main()



