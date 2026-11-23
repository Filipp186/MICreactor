"""Check the index or every commit selected for a public push."""

import os
import re
import subprocess
import sys


PUBLIC_FILES = {
    '.gitignore', '.gitattributes', '.githooks/pre-commit', '.githooks/pre-push', '.githooks/check-public.py',
    'LICENSE', 'README.md', 'THIRD_PARTY_NOTICES.md', 'QT_LGPL_COMPLIANCE.md',
    'docs/PUBLICATION.md', 'docs/USER_GUIDE_RU.md', 'docs/VOICE_PROFILES_RU.md',
}
VERSION = r'[0-9]+\.[0-9]+\.[0-9]+'
RELEASE_NOTES = re.compile(rf'docs/RELEASE_NOTES_{VERSION}_RU\.md')
RELEASE_TAG = re.compile(rf'refs/tags/v{VERSION}')
PUBLIC_EMAIL = re.compile(r'^[^@\s]+@users\.noreply\.github\.com$')
EMAIL = re.compile(r'[\w.+%-]+@[\w.-]+\.[a-z]{2,}', re.IGNORECASE)
PRIVATE_PATH = re.compile(r'(?i)\b[a-z]:[\\/]+(?:users|documents|проекты|obsidian)[\\/]+')
PRIVATE_IP = re.compile(r'(?<![\d.])(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])')
SECRET = re.compile(
    r'(?<![\w-])(?:github_pat_[A-Za-z0-9_]{50,}|gh[pousr]_[A-Za-z0-9]{30,}|'
    r'hf_[A-Za-z0-9]{25,}|sk-(?:proj-)?[A-Za-z0-9_-]{30,}|(?:AKIA|ASIA)[A-Z0-9]{16}|'
    r'xox[baprs]-[A-Za-z0-9-]{20,}|ya29\.[A-Za-z0-9_-]{24,}|y0_[A-Za-z0-9_-]{25,})(?![\w-])|'
    r'-----BEGIN (?:ENCRYPTED |RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----\s+[A-Za-z0-9+/=]{20,}|'
    r'https?://[^/@\s]+:[^/@\s]+@|(?<!\d)\d{8,12}:[A-Za-z0-9_-]{35}(?![A-Za-z0-9_-])'
)
MAX_SIZE = 512 * 1024
checked = set()


def git(*args):
    return subprocess.check_output(['git', '--no-replace-objects', *args])


def fail(reason):
    raise SystemExit(f'Public Git guard blocked this operation: {reason}')


def check_text(text, label, check_addresses=True):
    if SECRET.search(text):
        fail(f'credential pattern in {label}')
    if PRIVATE_PATH.search(text) or PRIVATE_IP.search(text):
        fail(f'local path or private network address in {label}')
    if check_addresses and any(not PUBLIC_EMAIL.fullmatch(email) for email in EMAIL.findall(text)):
        fail(f'email address in {label}')


def check_files(entries):
    for entry in entries.split(b'\0'):
        if not entry:
            continue
        meta, path_bytes = entry.split(b'\t', 1)
        mode, kind, oid = meta.decode('ascii').split()
        path = path_bytes.decode('utf-8')
        if path not in PUBLIC_FILES and not RELEASE_NOTES.fullmatch(path):
            fail(f'path outside the public allowlist ({path!r})')
        if mode not in {'100644', '100755'} or kind != 'blob':
            fail(f'non-regular file at {path!r}')
        if oid in checked:
            continue
        if int(git('cat-file', '-s', oid)) > MAX_SIZE:
            fail(f'file exceeds the public text size limit ({path!r})')
        data = git('cat-file', 'blob', oid)
        if b'\0' in data:
            fail(f'binary content at {path!r}')
        check_text(data.decode('utf-8-sig'), path)
        checked.add(oid)


def check_commit(oid):
    raw = git('cat-file', 'commit', oid).decode('utf-8')
    headers, _, message = raw.partition('\n\n')
    for header in headers.splitlines():
        if header.startswith(('author ', 'committer ')):
            match = re.search(r'<([^<>]+)>', header)
            if not match or not PUBLIC_EMAIL.fullmatch(match[1]):
                fail('commit metadata must use a GitHub noreply email')
            check_text(header, 'commit metadata', check_addresses=False)
    check_text(message, 'commit message')
    check_files(git('ls-tree', '-r', '-z', oid))


def main():
    if sys.argv[1] == 'index':
        for ident in ('GIT_AUTHOR_IDENT', 'GIT_COMMITTER_IDENT'):
            match = re.search(rb'<([^<>]+)>', git('var', ident))
            if not match or not PUBLIC_EMAIL.fullmatch(match[1].decode('utf-8')):
                fail('configure a GitHub noreply email for this repository')
        check_files(git('ls-tree', '-r', '-z', git('write-tree').strip().decode('ascii')))
        return

    commits = set()
    for line in sys.stdin:
        _, oid, remote_ref, _ = line.split()
        if set(oid) == {'0'}:
            continue
        if remote_ref != 'refs/heads/main' and not RELEASE_TAG.fullmatch(remote_ref):
            fail('only main and version tags may be pushed')
        if git('cat-file', '-t', oid).strip() != b'commit':
            fail('public refs must point directly to a commit')
        for commit in git('rev-list', oid).decode('ascii').splitlines():
            if commit not in commits:
                check_commit(commit)
                commits.add(commit)


if __name__ == '__main__':
    try:
        main()
    except (UnicodeError, ValueError, subprocess.CalledProcessError):
        fail('could not verify UTF-8 content or Git objects')
