#!/usr/bin/python3
""" script to get examples from my presentation
    example of python - it's faster than doing it manually
"""

import os
import re
from urllib.request import urlopen
from collections import defaultdict

GITHUB_URL = 'https://raw.githubusercontent.com'
TEX_URL = '/dithua/presentations/master/python/src/presentation.tex'
FILENAME = 'presentation.tex'
FOLDER = 'presentation-code'
PREFIX = 'slide'
SEPARATOR = '-'
LANG = '.py'


def remove_indent(code_block):
    """ makes sure first line is not indented
        and removes that much space from the rest
        of the lines as well
    :returns: str - the block unindented

    """
    lines = code_block.strip('\n').split('\n')
    indent = len(lines[0]) - len(lines[0].lstrip())
    return '\n'.join([line[indent:] for line in lines])


def tex_regex(block_name, regex_name=None):
    """ creates a regular expression that captures
        latex environments. Captures two parts,
        the first one is the whole environment with the tags
        and can be renamed using regex_name.
        The second one is named content and doesn't include the tags.

    :block_name: the name of the block
    :regex_name: the name to give the group that matches
                 the whole block
    :returns:    a compiled regular expression
    """

    names = (regex_name if regex_name else block_name,
             block_name,
             block_name)
    regexp = re.compile(r'(?P<%s>\\begin{%s}(?P<content>.*?)\\end{%s})'
                        % names,
                        re.DOTALL)
    return regexp

if __name__ == '__main__':

    print('You are running slide evaluation v 0.0.1')
    if not os.path.exists(FOLDER):
        print('Creating folder "{}" to add code samples'.format(FOLDER))
        os.makedirs(FOLDER)
    # open the presentation and get all the text
    # with open(FILENAME, 'r') as tex_file:
    #     text = tex_file.read()
    text = str(urlopen(GITHUB_URL + TEX_URL).read(), encoding='utf-8')

    # we want to count frames - it's easier to find the examples then
    frame_regex = tex_regex('frame')
    # lstlisting is a way to insert code with syntax highlighting in tex
    # so we know that all code is in tags \begin{lstlisting} - \end{lstlisting}
    code_regex = tex_regex('lstlisting')
    # get code examples

    code_examples = defaultdict(list)
    for frame_count, frame_match in enumerate(frame_regex.finditer(text)):
        frame_text = frame_match.group('content')
        for code_count, code_match in \
                enumerate(code_regex.finditer(frame_text)):
            code = remove_indent(code_match.group('content'))
            tokens = [PREFIX, str(frame_count), str(code_count)]
            codefile = SEPARATOR.join(tokens) + LANG
            with open(os.path.join(FOLDER, codefile), 'w') as out:
                out.write(code)
                # TODO remove this
                code_examples[frame_count].append(code)

    print('Written %s files to folder "%s"' % (len(code_examples), FOLDER))
    print('Input the number of the slide you wish to run the code of.')
    print('Type exit to leave the programme at any time.')
    while(True):
        try:
            user_inp = input('\nslide number: ')
            slide_num = int(user_inp)
        except ValueError:
            if user_inp == 'exit':
                print("bye!")
                break
            else:
                print('\nI was expecting a number!')
                continue
        examples = code_examples[slide_num]
        if examples:
            for index, example in enumerate(examples):
                try:
                    print('\nRunning example %s of slide %s'
                          % (index + 1, slide_num))
                    print('--------------------------------\n')
                    # TODO this is insecure - check it at some point
                    exec(example)
                    print('\n--------------------------------\n')
                except Exception as e:
                    print('Oops.. we got an error Houston\n')
                    print(e)
                    print()
                    print(example)
        else:
            print('\nSorry, There is no example on slide %s!' % slide_num)
