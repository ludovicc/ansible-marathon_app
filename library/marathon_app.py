#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2015, Ludovic Claude <ludovic.claude@laposte.net>
#

DOCUMENTATION = """
module: marathon_app
version_added: "1.9"
short_description: start and stop applications with Marathon
description:
  - Start and stop applications with Marathon.

options:
  uri:
    required: true
    description:
      - Base URI for the Marathon instance

  operation:
    required: true
    aliases: [ command ]
    choices: [ create, edit, fetch, versions, restart, destroy, kill ]
    description:
      - The operation to perform.

  username:
    required: false
    description:
      - The username to log-in with.

  password:
    required: false
    description:
      - The password to log-in with.

  id:
    required: true
    description:
      - Unique identifier for the app consisting of a series of names separated by slashes.

  command:
    aliases: [ cmd ]
    required: false
    description:
      - The command that is executed.

  arguments:
    aliases: [ args ]
    required: false
    description:
      - An array of strings that represents an alternative mode of specifying the command to run.

  cpus:
    required: false
    description:
     - The number of CPU`s this application needs per instance. This number does not have to be integer, but can be a fraction.

  memory:
    aliases: [ mem ]
    required: false
    description:
     - The amount of memory in MB that is needed for the application per instance.

  ports:
    required: false
    description:
     - An array of required port resources on the host.

  requirePorts:
    required: false
    description:
     - If true, the ports you have specified are used as host ports.

  instances:
    required: false
    description:
     - The number of instances of this application to start.

  executor:
    required: false
    description:
     - The executor to use to launch this application.

  container:
    required: false
    description:
     - Additional data passed to the containerizer on application launch. This is a free-form data structure that can contain arbitrary data.

  env:
    required: false
    description:
     - Key value pairs that get added to the environment variables of the process to start.

  constraints:
    required: false
    description:
     - Valid constraint operators are one of ["UNIQUE", "CLUSTER", "GROUP_BY"].

  acceptedResourceRoles:
    required: false
    description:
     - A list of resource roles.

  labels:
    required: false
    description:
     - Attaching metadata to apps can be useful to expose additional information to other services, so we added the ability to place labels on apps.

  uris:
    required: false
    description:
     - URIs defined here are resolved, before the application gets started. If the application has external dependencies, they should be defined here.

  dependencies:
    required: false
    description:
     - A list of services upon which this application depends.

  healthChecks:
    required: false
    description:
     - An array of checks to be performed on running tasks to determine if they are operating as expected.

  backoffSeconds:
    required: false
    description:
     - Configures exponential backoff behavior when launching potentially sick apps. The backoff period is multiplied by the factor for each consecutive failure until it reaches maxLaunchDelaySeconds.

  backoffFactor:
    required: false
    description:
     - Configures exponential backoff behavior when launching potentially sick apps. The backoff period is multiplied by the factor for each consecutive failure until it reaches maxLaunchDelaySeconds.

  maxLaunchDelaySeconds:
    required: false
    description:
     - Configures exponential backoff behavior when launching potentially sick apps. The backoff period is multiplied by the factor for each consecutive failure until it reaches maxLaunchDelaySeconds.

  upgradeStrategy_minimumHealthCapacity:
    required: false
    description:
     - a number between 0and 1 that is multiplied with the instance count. This is the minimum number of healthy nodes that do not sacrifice overall application purpose.

  upgradeStrategy_maximumOverCapacity:
    required: false
    description:
     - a number between 0 and 1 which is multiplied with the instance count. This is the maximum number of additional instances launched at any point of time during the upgrade process.

  restart:
    required: false
    description:
     - If the app is affected by a running deployment, then the update operation will fail. The current deployment can be overridden by setting the `force` query parameter. Default: false.

author: "Ludovic Claude (@ludovicc)"
"""

EXAMPLES = """
TODO
# Create a new issue and add a comment to it:
- name: Create an issue
  jira: uri={{server}} username={{user}} password={{pass}}
        project=ANS operation=create
        summary="Example Issue" description="Created using Ansible" issuetype=Task
  register: issue

- name: Comment on issue
  jira: uri={{server}} username={{user}} password={{pass}}
        issue={{issue.meta.key}} operation=comment 
        comment="A comment added by Ansible"

# Assign an existing issue using edit
- name: Assign an issue using free-form fields
  jira: uri={{server}} username={{user}} password={{pass}}
        issue={{issue.meta.key}} operation=edit
        assignee=ssmith

# Create an issue with an existing assignee
- name: Create an assigned issue
  jira: uri={{server}} username={{user}} password={{pass}}
        project=ANS operation=create
        summary="Assigned issue" description="Created and assigned using Ansible" 
        issuetype=Task assignee=ssmith

# Edit an issue using free-form fields
- name: Set the labels on an issue using free-form fields
  jira: uri={{server}} username={{user}} password={{pass}}
        issue={{issue.meta.key}} operation=edit 
  args: { fields: {labels: ["autocreated", "ansible"]}}

- name: Set the labels on an issue, YAML version
  jira: uri={{server}} username={{user}} password={{pass}}
        issue={{issue.meta.key}} operation=edit 
  args: 
    fields: 
      labels:
        - "autocreated"
        - "ansible"
        - "yaml"

# Retrieve metadata for an issue and use it to create an account
- name: Get an issue
  jira: uri={{server}} username={{user}} password={{pass}}
        project=ANS operation=fetch issue="ANS-63"
  register: issue

- name: Create a unix account for the reporter
  sudo: true
  user: name="{{issue.meta.fields.creator.name}}" comment="{{issue.meta.fields.creator.displayName}}"

# Transition an issue by target status
- name: Close the issue
  jira: uri={{server}} username={{user}} password={{pass}}
        issue={{issue.meta.key}} operation=transition status="Done"
"""

import json
import base64

def request(url, user=None, passwd=None, data=None, method=None):
    if data:
        data = json.dumps(data)

    if not user:
      auth = base64.encodestring('%s:%s' % (user, passwd)).replace('\n', '')
      response, info = fetch_url(module, url, data=data, method=method, 
                               headers={'Content-Type':'application/json',
                                        'Authorization':"Basic %s" % auth})
    else:
      response, info = fetch_url(module, url, data=data, method=method, 
                               headers={'Content-Type':'application/json'})

    if info['status'] not in (200, 204):
        module.fail_json(msg=info['msg'])

    body = response.read()

    if body:
        return json.loads(body)
    else:
        return {}

def post(url, user, passwd, data):
    return request(url, user, passwd, data=data, method='POST')

def put(url, user, passwd, data):
    return request(url, user, passwd, data=data, method='PUT')

def get(url, user, passwd):
    return request(url, user, passwd)

def delete(url, user, passwd):
    return request(url, user, passwd, data=None, method='DELETE')

def create(restbase, user, passwd, params):
    createfields = {
        'id': params['id'],
        'summary': params['summary'],
        'description': params['description'],
        'issuetype': { 'name': params['issuetype'] }}

    # Merge in any additional or overridden fields
    if params['fields']:
        createfields.update(params['fields'])

    data = {'fields': createfields}

    url = restbase + '/apps'

    ret = post(url, user, passwd, data) 

    return ret


def edit(restbase, user, passwd, params):
    data = {
        'id': params['id']
        }

    url = restbase + '/apps/' + params['id']    

    ret = put(url, user, passwd, data) 

    return ret

def restart(restbase, user, passwd, params):
    data = {
        'force': params['force']
        }

    url = restbase + '/apps/' + params['id'] + '/restart'   

    ret = post(url, user, passwd, data) 

    return ret

def fetch(restbase, user, passwd, params):
    url = restbase + '/apps/' + params['id']
    ret = get(url, user, passwd) 
    return ret

def destroy(restbase, user, passwd, params):
    url = restbase + '/apps/' + params['id']
    ret = delete(url, user, passwd) 
    return ret

def kill(restbase, user, passwd, params):
    url = restbase + '/apps/' + params['id'] + '/tasks'  
    ret = delete(url, user, passwd) 
    return ret

# Some parameters are required depending on the operation:
OP_REQUIRED = dict(create=['id'],
                   edit=['id'],
                   fetch=['id'],
                   versions=['id'],
                   restart=['id'],
                   destroy=['id'],
                   kill=['id'])

def main():

    global module
    module = AnsibleModule(
        argument_spec=dict(
            uri=dict(required=True),
            operation=dict(choices=['create', 'edit', 'fetch', 'versions', 'restart', 'destroy', 'kill'],
                           aliases=['command'], required=True),
            username=dict(required=False,default=None),
            password=dict(required=False,default=None),
            id=dict(type='str'),
            cmd=dict(aliases=['command'], type='str'),
            args=dict(aliases=['arguments']),
            cpus=dict(),
            mem=dict(aliases=['memory']),
            ports=dict(),
            requirePorts=dict(),
            instances=dict(),
            executor=dict(),
            container=dict(),
            env=dict(default={}),
            constraints=dict(),
            acceptedResourceRoles=dict(),
            labels=dict(),
            uris=dict(),
            dependencies=dict(),
            healthChecks=dict(),
            backoffSeconds=dict(),
            backoffFactor=dict(),
            maxLaunchDelaySeconds=dict(),
            upgradeStrategy_minimumHealthCapacity=dict(),
            upgradeStrategy_maximumOverCapacity=dict(),
            restart=dict(default=False, type='bool'))
        ),
        supports_check_mode=False
    )

    op = module.params['operation']

    # Check we have the necessary per-operation parameters
    missing = []
    for parm in OP_REQUIRED[op]:
        if not module.params[parm]:
            missing.append(parm)
    if missing:
        module.fail_json(msg="Operation %s require the following missing parameters: %s" % (op, ",".join(missing)))

    # Handle rest of parameters
    uri = module.params['uri']
    user = module.params['username']
    passwd = module.params['password']

    if not uri.endswith('/'):
        uri = uri+'/'
    restbase = uri + 'v2'

    # Dispatch
    try:
        
        # Lookup the corresponding method for this operation. This is
        # safe as the AnsibleModule should remove any unknown operations.
        thismod = sys.modules[__name__]
        method = getattr(thismod, op)

        ret = method(restbase, user, passwd, module.params)

    except Exception, e:
        return module.fail_json(msg=e.message)


    module.exit_json(changed=True, meta=ret)


from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
main()
