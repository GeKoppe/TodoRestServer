from RestServer import RestServer as rs

print('Starting now')
server = rs(host='0.0.0.0', port=13376)
server.boot()