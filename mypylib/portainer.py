import requests
import time

baseurl = 'http://192.168.1.30:9000'
uname = 'Will@WillJBrown.com'
pword = 'gXvgZ2LqXLCxbdhkrcdicvLc'
auth = None


def authtoken():
    authurl = baseurl + '/api/auth'
    authdata = {'Username': uname, 'Password': pword}
    authrequest = requests.post(authurl, json=authdata)
    authkvp = {'Authorization': 'Bearer ' + authrequest.json()['jwt']}
    return {'kvp': authkvp, 'time': time.time()}


def gettoken():
    global auth
    if auth is None or auth['time'] < time.time() - 8 * 3600:
        auth = authtoken()
    return auth['kvp']


def portainerstatus():
    statusurl = baseurl + '/api/status'
    statusrequest = requests.get(statusurl, headers=gettoken())
    return 'Version' in statusrequest.json()


def liststacks():
    if not portainerstatus():
        return False
    stacksdict = {}
    stackurl = baseurl + '/api/stacks'
    stacksrequest = requests.get(stackurl, headers=gettoken())
    for stack in stacksrequest.json():
        # pprint.pprint(stack)
        stacksdict.update(
            {stack['Name']: {
                'Name': stack['Name'],
                'Status': stack['Status'],
                'Id': stack['Id']
            }}
        )
    return stacksdict


def startstack(stackname):
    stackid = liststacks()[stackname]['Id']
    starturl = baseurl + '/api/stacks/' + str(stackid) + '/start'
    startrequest = requests.post(starturl, headers=gettoken())
    return startrequest.status_code == 200


def stopstack(stackname):
    stackid = liststacks()[stackname]['Id']
    stopurl = baseurl + '/api/stacks/' + str(stackid) + '/stop'
    stoprequest = requests.post(stopurl, headers=gettoken())
    return stoprequest.status_code == 200


def listendpoints():
    endpointdict = {}
    endpointurl = baseurl + '/api/endpoints'
    endpointrequest = requests.get(endpointurl, headers=gettoken())
    for point in endpointrequest.json():
        endpointdict.update(
            {point['Name']: {
                'Name': point['Name'],
                'Id': point['Id'],
                'Status': point['Status'],
                'PublicURL': point['PublicURL'],
                'Running': point['Snapshots'][0]['RunningContainerCount'],
                'Unhealthy': point['Snapshots'][0]['UnhealthyContainerCount']
            }}
        )
    return endpointdict


def listcontainersonendpoint(endpoint):
    endid = endpoint['Id']
    containerdict = {}
    containerurl = baseurl + '/api/endpoints/' + str(endid) + '/docker/containers/json'
    containerrequest = requests.get(containerurl, headers=gettoken(), params={'all': True})
    for container in containerrequest.json():
        # pprint.pprint(container)
        containerdict.update(
            {container['Names'][0][1:]: {
                'Names': container['Names'][0][1:],
                'Id': container['Id'],
                'State': container['State'],
                'Status': container['Status'],
            }}
        )
    return containerdict


def getstatus():
    if not portainerstatus():
        return False
    statusrefresh = listendpoints()
    for point in statusrefresh.values():
        point.update({'Containers': listcontainersonendpoint(point)})
    return statusrefresh


def startcontainer(endpointname, containername):
    status = getstatus()
    if not status:
        return False
    endid = status[endpointname]['Id']
    contid = status[endpointname]['Containers'][containername]['Id']
    starturl = baseurl + '/api/endpoints/' + str(endid) + '/docker/containers/' + str(contid) + '/start'
    startrequest = requests.post(starturl, headers=gettoken())
    return startrequest.status_code == 204


def restartcontainer(endpointname, containername):
    status = getstatus()
    if not status:
        return False
    endid = status[endpointname]['Id']
    contid = status[endpointname]['Containers'][containername]['Id']
    restarturl = baseurl + '/api/endpoints/' + str(endid) + '/docker/containers/' + str(contid) + '/restart'
    restartrequest = requests.post(restarturl, headers=gettoken())
    return restartrequest.status_code == 204


def stopcontainer(endpointname, containername):
    status = getstatus()
    if not status:
        return False
    endid = status[endpointname]['Id']
    contid = status[endpointname]['Containers'][containername]['Id']
    stopurl = baseurl + '/api/endpoints/' + str(endid) + '/docker/containers/' + str(contid) + '/stop'
    stoprequest = requests.post(stopurl, headers=gettoken())
    return stoprequest.status_code == 204
