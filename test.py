from outline_vpn.outline_vpn import OutlineVPN

#sha="0141ED49C355B5697B9D18A237F1C468083035F04B8780C310F4499AFCA46EA2"
url="https://194.87.207.132:46784/WvjLYO1yBj0NiukGbHtvUw"
client = OutlineVPN(api_url=url)
new_key = client.create_key(str(id))
print(new_key)