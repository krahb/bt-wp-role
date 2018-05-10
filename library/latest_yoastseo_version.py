#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2017, Bob ter Hark, <bob@btunix.nl>
#

import requests

from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
author: "Bob ter Hark (@krahb)
module: latest_yoastseo_version
short_description: Get the latest version of stable Yoast SEO plugin
description:
version_added: "2.2"
options:
  url:
    description:
    - url to page with latest release
    - defaults to https://wordpress.org/plugins/wordpress-seo/
'''

EXAMPLES = '''
- latest_yoastseo_version:

- latest_yoastseo_version:
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
        url = "https://wordpress.org/plugins/wordpress-seo/"

    changed = False

    page_with_latest = requests.get(url)
    if page_with_latest.status_code != 200:
        module.fail_json(msg="Error: http request returned <> 200", rc=1,
                         err=page_with_latest.status_code)

    latest = re.search('(?<=\"softwareVersion\": \")(.*?)(?=\",)',
                       str(page_with_latest.content))

    module.exit_json(msg=latest.group(0), changed=changed)


if __name__ == '__main__':
    main()
