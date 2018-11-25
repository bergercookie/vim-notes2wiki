#!/usr/bin/env python3

"""
Scirpt for converting a vim-notes directory to the corresponding vimwiki
structure
"""

import datetime
import os
import re
import sys

import click


@click.command()
@click.option('--notes-dir', required=True, help='Path to vim-notes directory')
@click.option('--vw-dir', required=True, help='Path to vimwiki directory')
@click.option('--interactive', is_flag=True,
              help='Prompt in case overwrite is needed')
def main(notes_dir: str, vw_dir: str, interactive):
    """Main."""

    # sanitize data
    for d in notes_dir, vw_dir:
        if not os.path.isdir(d):
            print("\"{}\" is not a directory. Exiting...".format(d))
            sys.exit(1)

    # call  convert_file for all files
    print("Converting notes...")
    files_list = [f for f in os.listdir(notes_dir) if f.endswith(".md")]
    for i, fname in enumerate(files_list):
        print("{}. Converting: {}".format(i, fname))
        fname_wo_ext = fname.rsplit('.', maxsplit=1)[0]
        fname_wiki = os.path.join(vw_dir, "{}.wiki".format(fname_wo_ext))
        fname_full = os.path.join(notes_dir, fname)

        if os.path.exists(fname_wiki):
            if interactive:
                ans = input("\"{}\" already exists. Overwrite? [Y/n]"
                            .format(fname_wiki))
                if ans not in ['Y', 'y', '']:
                    print("Skipping file...")
                    continue
            else:
                print("[!] \"{}\" already exists, overwriting...".format(fname_wiki))

        convert_file(fname_full, fname_wiki)

    # Modify index.wiki
    print("Adding link to notes in index.wiki...")
    index_file = os.path.join(vw_dir, "index.wiki")
    if not os.path.isfile(index_file):
        print("Cannot detect {} file. Exiting...".format(index_file))
        sys.exit(2)

    # Summarise imported notes file in another `.wiki` page
    notes_wiki_fname = "vim_notes_imported"
    notes_wiki_fpath = os.path.join(vw_dir,
                                    ".".join([notes_wiki_fname, 'wiki']))
    with open(notes_wiki_fpath, 'w') as notes_f:
        notes_f.write("= Imported notes (former vim-notes) =\n\n")
        notes_f.write("Notes imported on {}\n"
                      .format(datetime.datetime.now()
                              .strftime("%Y/%m/%d - %I:%M%p")))

        for fname in files_list:
            fname_wo_ext = fname.rsplit('.', maxsplit=1)[0]
            notes_f.write("\t* [[{}]]\n".format(fname_wo_ext))

    with open(index_file, 'a') as index_f:
        index_f.write("* [[{}|Imported notes from vim-notes directory]]\n\n"
                      .format(notes_wiki_fname))


def convert_file(src: str, dst: str):
    """Convert a file from vim-notes format to vimwiki."""

    # Read
    ###########################################################################
    with open(src, 'r') as fin:
        lines = fin.readlines()

    # Process
    ###########################################################################
    # write note title
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
        # TODO - test this
        m = re.match('^(#+) (.*)$', line)
        if m:
            lvl = len(m.group(1))
            s = m.group(2)
            lines[i] = "{0} {1} {0}\n".format('=' * lvl, s)

    return lines


def sed_tags(lines: list) -> str:
    """Convert vim-notes '@' tags to vimwiki :*: tags."""

    for i, line in enumerate(lines):
        m = re.match('^@([a-zA-Z-]+)$', line)
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
        '▹': '*',
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
