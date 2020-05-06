import pypandoc
import glob
import os
import re


def convertMarkdownDocsToRst():
    pypandoc.ensure_pandoc_installed()

    # TODO make various edits to improve conversion, like removing the Table of Contents
    print("Converting all .md files to .rst...")
    input_dir = '../../doc'
    output_dir = 'generated_docs'
    subdirs = ['', 'how_tos', 'explanations']
    for subdir in subdirs:
        # print(f'>>>> {subdir}')
        input_sub_dir = f'{input_dir}/{subdir}'
        if not os.path.isdir(input_sub_dir):
            print(f'Directory {input_sub_dir} does not exist. Skipping)')
        output_sub_dir = f'{output_dir}/{subdir}'
        convert_all_markdown_files_in_dir(subdir, input_sub_dir, output_sub_dir)


def convert_all_markdown_files_in_dir(subdir, input_sub_dir, output_sub_dir):
    base_names_to_skip = ['README', 'TemplatePage']
    md_files = glob.glob(f'{input_sub_dir}/*.md')
    if not md_files:
        return
    if not os.path.isdir(output_sub_dir):
        os.makedirs(output_sub_dir)
    for file in md_files:
        file_base_file = os.path.split(file)[1]
        file_base_name = os.path.splitext(file_base_file)[0]

        if file_base_name in base_names_to_skip:
            continue
        # print(file_base_name, input_sub_dir, output_sub_dir)
        convert_markdown_to_restructured_text(subdir, file_base_name, input_sub_dir, output_sub_dir)


def convert_markdown_to_restructured_text(subdir, file_base_name, input_dir, output_dir):
    with open(f'{input_dir}/{file_base_name}.md') as markdown_file:
        content = markdown_file.read()

        content = fix_up_markdown_content(subdir, file_base_name, content)

        # Temporary code for reviewing changes made, on all input files:
        with open(file_base_name + '_hacked.md', 'w') as w:
            w.write(content)

    output = pypandoc.convert_text(''.join(content), 'rst', format='md',
                                   outputfile=f'{output_dir}/{file_base_name}.rst')


def fix_up_markdown_content(subdir, file_base_name, content):
    # Note: We intentionally do not remove the 'GENERATED FILE' comment,
    # as if anyone edits the derived .rst file, it nicely
    # points to the master file.

    content = fixup_boilerplate_text(content)
    content = fixup_generated_snippets(content)
    content = fixup_code_languages_for_pygments(content)
    content = fixup_markdown_hyperlinks(content, subdir, file_base_name)

    return content


def fixup_boilerplate_text(content):
    # Remove 'top' anchor (and the following blank line)
    content = content.replace('<a id="top"></a>\n\n', '')

    # Remove table of contents
    content = re.sub(r'<!-- toc -->.*<!-- endtoc -->', '', content, count=1, flags=re.DOTALL)

    # Remove 'Back to User Guide'
    back_to_user_guide = (
        '---\n'
        '\n'
        '[Back to User Guide](/doc/README.md#top)\n'
    )
    content = content.replace(back_to_user_guide, '')
    return content


def fixup_generated_snippets(content):
    """
    Adjust the expanded code snippets that were generated
    by mdsnippets, to improve rendering by Sphinx
    """

    # Remove 'snippet source' links from all code snippets
    content = re.sub(
        r"<sup><a href='([^']+)' title='File snippet `[^`]+` was extracted from'>snippet source</a> ",
        r"(See [snippet source](\1))", content)

    # Remove 'anchor' links from all code snippets
    content = re.sub(
        r"\| <a href='#snippet-[^']+' title='Navigate to start of snippet `[^']+`'>anchor</a></sup>",
        '', content)

    return content


def fixup_code_languages_for_pygments(content):
    # Fix "WARNING: Pygments lexer name 'h' is not known"
    # Todo: find out how to fix this in conf.py - this is a horrible hack!
    content = content.replace(
        '\n```h\n',
        '\n```cpp\n')

    # Fix "WARNING: Pygments lexer name 'txt' is not known"
    # Text files don't need any markup
    content = content.replace(
        '\n```txt\n',
        '\n```\n')
    return content


def fixup_markdown_hyperlinks(content, subdir, file_base_name):
    hyperlink_regex = re.compile(
        r"""\] # the closing ] that surrounds the link text
            \( # the escaped ( at the start of the destination
            (  # start capturing the destination
            [^() ]+ # the destination
            )  # finish capturing the desintation
            \) # the escaped ) at the end of the destination""", re.VERBOSE)

    def convert_github_markdown_url_to_sphinx(matched_obj):
        full_match = matched_obj.group(0)
        full_url = matched_obj.group(1)

        # Check if it is a kind of URL will be embedded in Sphinx docs:
        will_include_in_sphix_docs = True
        if not full_url.startswith('/doc'):
            will_include_in_sphix_docs = False
        if '.md' not in full_url:
            will_include_in_sphix_docs = False

        if not will_include_in_sphix_docs:
            if full_url.startswith('/'):
                # It's an internal link, to a file or directory in our github repo
                # TODO Instead of master, use the changeset that this was generated from
                if full_url.endswith('/'):
                    new_full_url = 'https://github.com/approvals/ApprovalTests.cpp/tree/master' + full_url[0:-1]
                else:
                    new_full_url = 'https://github.com/approvals/ApprovalTests.cpp/blob/master' + full_url
                return f']({new_full_url})'
            else:
                # It's a link to somewhere else, e.g. http, mailto, or anchor ('#') in current document,
                # so return it unchanged
                return full_match

        assert 'TemplatePage.source.md' not in full_url

        # Split the url and the anchor
        if '#' in full_url:
            original_url, original_anchor = full_url.split('#')
        else:
            original_url = full_url
            original_anchor = ''

        current_path = '/doc'
        if subdir != '':
            current_path = f'{current_path}/{subdir}'
        new_url = os.path.relpath(original_url, current_path)
        new_url = new_url.replace('.md', '.html')

        new_anchor = original_anchor
        if new_anchor == 'top':
            new_anchor = ''

        # mdsnippets puts a hyphen in for each unusual character in an anchor
        # Sphinx puts a hyphen in for each run of one or more unusual characters in an anchor
        if '--' in new_anchor:
            new_anchor = re.sub('--+', '-', new_anchor)

        if new_anchor != '':
            new_full_url = f'{new_url}#{new_anchor}'
        else:
            new_full_url = new_url
        return f']({new_full_url})'

    content = hyperlink_regex.sub(convert_github_markdown_url_to_sphinx, content)

    # TODO  Print out any remaining lines that contain ](/
    # TODO  Print out a list of all adjusted URLs so that I can test them
    lines = content.splitlines()
    for line in lines:
        if '](/' in line:
            print('>>>', subdir, file_base_name, line)

    return content
