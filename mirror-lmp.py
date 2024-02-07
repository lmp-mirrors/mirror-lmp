#!/usr/bin/env python3

import os
import logging
import subprocess
import time

import yaml

logging.basicConfig(
    level=os.environ.get('LOGLEVEL', 'INFO'),
    format='%(asctime)s %(levelname)s: %(message)s')
log = logging.getLogger('mirror-lmp')

MIRROR_DIR = os.environ.get('MIRROR_DIR', '/mirrors')


def _should_fetch(repo_path, config):
    interval = config.get('interval-minutes')
    if not interval:
        return True
    now = time.time()
    last_check = os.path.join(repo_path, 'mirror-last-check')
    try:
        elapsed = now - os.stat(last_check).st_mtime
        remaining = (interval * 60) - elapsed
        if remaining > 0:
            log.debug('Fetch(%s) elapsed(%d) remaining(%d) seconds',
                      repo_path, elapsed, remaining)
            return False
    except FileNotFoundError:
        pass
    with open(last_check, 'w') as f:
        f.write('%s' % now)
    return True


def _mirror_repo(repo, config):
    dst = os.path.join(MIRROR_DIR, repo)
    if not dst.endswith('.git'):
        dst += '.git'
    if not os.path.exists(dst):
        log.info('Repo does not exist, cloning: %s', repo)
        subprocess.check_call(
            ['git', 'clone', '--bare', '--mirror', config['url'], dst])
    else:
        if _should_fetch(dst, config):
            log.info('Running git-fetch on: %s', repo)
            subprocess.check_call(['git', 'fetch'], cwd=dst)

            if config.get('github_mirror'):
                url = 'ssh://git@github.com/lmp-mirrors/' + os.path.basename(repo)
                log.info('Mirroring to github: %s', url)
                subprocess.check_call(['git', 'push', '-f', url, 'refs/heads/*:refs/heads/*'], cwd=dst)
                subprocess.check_call(['git', 'push', '-f', url, 'refs/tags/*:refs/tags/*'], cwd=dst)
        else:
            log.info('Skipping fetch for: %s', repo)


def main():
    # For github mirroring
    os.environ['GIT_SSH_COMMAND'] = 'ssh -i ./github-mirror_id'
    log.info('Mirroring repos')

    cfg_file = os.path.join(
        os.path.dirname(__file__),
        "lmp-mirrors.yaml"
    )
    with open(cfg_file) as f:
        cfg = yaml.safe_load(f)

    for repo, config in cfg.items():
        _mirror_repo(repo, config)


if __name__ == '__main__':
    main()
