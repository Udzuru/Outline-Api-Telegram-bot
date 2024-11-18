from outline_vpn.outline_vpn import OutlineVPN

def getkey(url,sha,id):
    
    client = OutlineVPN(api_url=url,cert_sha256=sha)
    new_key = client.create_key(str(id))
    print(new_key)
    return new_key

def deletekey(url,sha,name):
    client = OutlineVPN(api_url=url,cert_sha256=sha)
    tmp=[]
    for key in client.get_keys():
        if key.name == str(name):
            tmp.append(key.key_id)
    print(tmp)
    for t in tmp:
        client.delete_key(t)
    
    return True
