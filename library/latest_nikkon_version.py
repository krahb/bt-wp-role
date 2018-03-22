#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Bob ter Hark, <bob@btunix.nl>
#

import requests
import re

from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
author: "Bob ter Hark (@krahb)
module: latest_nzbget_version
short_description: Get the version of the latest stable WordPress theme Nikkon
description:
version_added: "2.2"
options:
  url:
    description:
    - url to page with latest release
    - defaults to https://wordpress.org/themes/nikkon/
'''

EXAMPLES = '''
- latest_nikkon_version:

- latest_nikkon_version:
    url: ""
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(),
        ),
        supports_check_mode=True,
    )

    url = module.params['url']
    if not url:
        url = "https://wordpress.org/themes/nikkon/"

    changed = False

    page_with_latest = requests.get(url)
    if page_with_latest.status_code != 200:
        module.fail_json(msg="Error: http request returned <> 200", rc=1,
                         err=page_with_latest.status_code)

    latest = re.search('(?<=\"version\":\")(.*?)(?=\",\"preview_url\")',
                       str(page_with_latest.content))

    module.exit_json(msg=latest.group(0), changed=changed)


if __name__ == '__main__':
    main()
