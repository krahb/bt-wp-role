#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ansible_wp
version_added: "post 2.3"
author: Doug Stewart
short_description: Install and manage WordPress sites
description:
   - WordPress installations can be installed, removed, and managed using the WP-CLI command line tool
'''

# import module snippets
from subprocess import call
from distutils.spawn import *
from ansible.module_utils.basic import *

def core(path, wp, module):

# module.check_mode

    themes = module.params['themes']
    plugins = module.params['plugins']
    users = module.params['users']
    download = module.params['download']
    changed = False

    if themes:
      for theme in themes:
        # wp --path=/var/www/thiwp/ theme is-installed <theme>
        rc, wpout, wperr = module.run_command("{} --path={} theme is-installed {}".format(wp, path, theme))
        if rc == 1:
            if wperr:
                # stderr, so something went wrong,
                module.fail_json(msg=wperr, rc=rc)
            else:
                # theme is not installed
                # theme search nikko --format=json --field=slug
                rc, wpout, wperr = module.run_command("{} --path={} theme search {} --format=json --field=slug".format(wp, path, theme))
                if rc != 0:
                    module.fail_json(msg=wperr, rc=rc)
                if theme in wpout:
                    # theme is available
                    if not module.check_mode:
                        rc, wpout, wperr = module.run_command("{} --path={} theme install {}".format(wp, path, theme))
                        if rc != 0:
                            module.fail_json(msg=wperr, rc=rc)
                    module.exit_json(msg="Theme {} installed".format(theme), changed=True)
                else:
                    module.fail_json(msg="Theme {} is not unavailable".format(theme), rc=rc)
        else:
            module.exit_json(msg="Theme {} installed".format(theme), changed=False)

    if plugins:
        pluginoutput=''
        ppp=plugins
        pp=''
        for plugin in plugins:
          pp=pp+' '+plugin
          # wp --path=/var/www/thiwp/ plugin is-installed <plugin>
          rc, wpout, wperr = module.run_command("{} --path={} plugin is-installed {}".format(wp, path, plugin))
          if rc == 1:
            if wperr:
                # stderr, so something went wrong,
                module.fail_json(msg=wperr, rc=rc)
            else:
                # plugin is not installed
                # plugin search wordpress-seo --format=json --field=slug
                rc, wpout, wperr = module.run_command("{} --path={} plugin search {} --format=json --field=slug".format(wp, path, plugin))
                if rc != 0:
                    module.fail_json(msg=wperr, rc=rc)
                if plugin in wpout:
                    # plugin is available
                    if not module.check_mode:
                        rc, wpout, wperr = module.run_command("{} --path={} plugin install {}".format(wp, path, plugin))
                        if rc != 0:
                            module.fail_json(msg=wperr, rc=rc)
#                    module.exit_json(msg="Plugin {} installed".format(plugin), changed=True)
                    changed = True
                    if pluginoutput:
                        pluginoutput = pluginoutput + ", Plugin {} installed".format(plugin)
                    else:
                        pluginoutput = "Plugin {} installed".format(plugin)
                else:
#                    module.fail_json(msg="Plugin {} is not unavailable".format(plugin), rc=rc)
                    if pluginoutput:
                        pluginoutput = pluginoutput + ", Plugin {} is not available".format(plugin)
                    else:
                        pluginoutput = "Plugin {} is not available".format(plugin)
          else:
#            module.exit_json(msg="Plugin {} installed".format(plugin), changed=False)
              if pluginoutput:
                  pluginoutput = pluginoutput + ", Plugin {} installed".format(plugin)
              else:
                  pluginoutput = "Plugin {} installed".format(plugin)

          module.exit_json(msg=pluginoutput, changed=changed)

    else:
        rc, wpversion, wperr = module.run_command("{} core version --path={}".format(wp, path))
        if not rc:
            module.exit_json(msg=wpversion, changed=changed)
        else:
            module.fail_json(msg=wperr)

def main():
    module = AnsibleModule(
        argument_spec = {
            "path": {'required': True, 'type': 'str'},
            'download': {
                'required': False,
                'default': 'no',
                'choices': ['no','yes'],
                'type': 'str'
            },
            'plugins': {'required': False, 'type': 'list'},
            'themes': {'required': False, 'type': 'list'},
            'users': {'required': False, 'type': 'list'},
            'cache': {
                'required': False,
                'type': 'str'
            },
        },
        mutually_exclusive = [
        ],
        supports_check_mode = True
    )

    wpcli = find_executable('wp')

    if not wpcli:
        module.fail_json(msg="`wp` not found! You must have a working WP-CLI install in order to execute this module.")

    path = module.params['path']

    try:
        core(path, wpcli, module)
    except Exception as e:
        module.fail_json(msg=str(e))

if __name__ == '__main__':
    main()