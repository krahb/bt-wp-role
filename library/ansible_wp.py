#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '0.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ansible_wp
'''

# import module snippets
import json
from subprocess import call
from distutils.spawn import *
from ansible.module_utils.basic import *

def query_available(path, wp, module, theme):
    rc, wpout, wperr = module.run_command("{} --path={} theme search {} --format=json --fields=slug,version".format(wp, path, theme))
    if rc != 0:
        module.fail_json(msg=wperr, rc=rc)
    try:
        theme_list = json.loads(wpout)
    except:
        theme_list = []
    theme_version = ''
    for t in theme_list:
        if t['slug'] == theme:
            theme_version = t['version']
    return theme_version

def core(path, wp, module):

    theme = module.params['theme']
    state = module.params['state']
    plugin = module.params['plugin']
    users = module.params['users']
    download = module.params['download']
    changed = False

    if theme:
        # wp --path=/var/www/thiwp/ theme is-installed <theme>
        theme_not_installed, wpout, wperr = module.run_command("{} --path={} theme is-installed {}".format(wp, path, theme))
        if wperr:
            module.fail_json(msg=wperr, rc=rc)
        if theme_not_installed == 0:
            # theme is installed
            rc, wpout, wperr = module.run_command("{} --path={} theme get {} --format=json --fields=version".format(wp, path, theme))
            if wperr:
                module.fail_json(msg=wperr, rc=rc)
            theme_version = json.loads(wpout)['version']
            if state == 'present':
                module.exit_json(msg="Theme {}.{} installed".format(theme, theme_version), changed=False)
            if state == 'absent':
                if not module.check_mode:
                    rc, wpout, wperr = module.run_command("{} --path={} theme delete {}".format(wp, path, theme))
                    if wperr:
                        module.fail_json(msg=wperr, rc=rc)
                    module.exit_json(msg="Theme {}.{} removed".format(theme, theme_version), changed=True)
            if state == 'latest':
                available_version = query_available(path, wp, module, theme)
                if available_version == theme_version:
                    module.exit_json(msg="Theme {}.{} installed".format(theme, theme_version), changed=False)
            else:
                if not module.check_mode:
                    rc, wpout, wperr = module.run_command("{} --path={} theme update {}".format(wp, path, theme))
                    if rc != 0:
                        module.fail_json(msg=wperr, rc=rc)
                module.exit_json(msg="Theme {} updated to {}".format(theme, available_version), changed=True)
        else:
            # theme is not installed
            if state == 'absent':
                module.exit_json(msg="Theme {} absent".format(theme), changed=False)
            available_version = query_available(path, wp, module, theme)
            if not module.check_mode:
                rc, wpout, wperr = module.run_command("{} --path={} theme install {} --activate".format(wp, path, theme))
                if rc != 0:
                    module.fail_json(msg=wperr, rc=rc)
            module.exit_json(msg="Theme {}.{} installed".format(theme, available_version), changed=True)

#    if plugin:
#        # wp --path=/var/www/thiwp/ plugin is-installed <plugin>
#        plugin_installed, wpout, wperr = module.run_command("{} --path={} plugin is-installed {}".format(wp, path, theme))
#        if wperr:
#          module.fail_json(msg=wperr, rc=rc)
#        rc, wpout, wperr = module.run_command("{} --path={} plugin search {} --format=csv --field=version".format(wp, path, theme))
#          if rc == 1:
#            if wperr:
#                # stderr, so something went wrong,
#                module.fail_json(msg=wperr, rc=rc)
#            else:
#                # plugin is not installed
#                # plugin search wordpress-seo --format=json --field=slug
#                rc, wpout, wperr = module.run_command("{} --path={} plugin search {} --format=json --field=slug".format(wp, path, plugin))
#                if rc != 0:
#                    module.fail_json(msg=wperr, rc=rc)
#                if plugin in wpout:
#                    # plugin is available
#                    if not module.check_mode:
#                        rc, wpout, wperr = module.run_command("{} --path={} plugin install {}".format(wp, path, plugin))
#                        if rc != 0:
#                            module.fail_json(msg=wperr, rc=rc)
#                    module.exit_json(msg="Plugin {} installed".format(plugin), changed=True)
#                    changed = True
#                    if pluginoutput:
#                        pluginoutput = pluginoutput + ", Plugin {} installed".format(plugin)
#                    else:
#                        pluginoutput = "Plugin {} installed".format(plugin)
#                else:
#                    module.fail_json(msg="Plugin {} is not unavailable".format(plugin), rc=rc)
#                    if pluginoutput:
#                        pluginoutput = pluginoutput + ", Plugin {} is not available".format(plugin)
#                    else:
#                        pluginoutput = "Plugin {} is not available".format(plugin)
#          else:
#            module.exit_json(msg="Plugin {} installed".format(plugin), changed=False)
#              if pluginoutput:
#                  pluginoutput = pluginoutput + ", Plugin {} installed".format(plugin)
#              else:
#                  pluginoutput = "Plugin {} installed".format(plugin)
#
#          module.exit_json(msg=pluginoutput, changed=changed)
#
#    else:
#        rc, wpversion, wperr = module.run_command("{} core version --path={}".format(wp, path))
#        if not rc:
#            module.exit_json(msg=wpversion, changed=changed)
#        else:
#            module.fail_json(msg=wperr)

def main():
    module = AnsibleModule(
        argument_spec={
            'path': {'required': True, 'type': 'str'},
            'state': {
                'required': False,
                'default': 'present',
                'choices': ['present', 'absent', 'latest'],
                'type': 'str'
            },
            'download': {
                'required': False,
                'default': 'no',
                'choices': ['no', 'yes'],
                'type': 'str'
            },
            'plugin': {'required': False, 'type': 'str'},
            'theme': {'required': False, 'type': 'str'},
            'users': {'required': False, 'type': 'list'},
            'cache': {'required': False, 'type': 'str'},
            'core': {'required': False, 'type': 'str'},
        },
        mutually_exclusive=[
        ],
        supports_check_mode=True
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
