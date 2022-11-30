import urllib, json, math, requests, re

class Dynmap(object):
    def __init__(self,url): #Dynamp url, ie dynmap.starcatcher.us
        if not url.startswith('http'):
            url = "http://" + url
        self.url = url
        self.link = url+"/up/world/world/"
        
        try:
            f = urllib.request.urlopen(self.link)
            data = f.read() #Gets the data
            self.decoded = json.loads(data)
        except:
            raise Exception("The url could not be accessed, maybe you mistyped it?")
        
        try:
            self.claims = url+"/tiles/_markers_/marker_world.json"
            f = urllib.request.urlopen(self.claims)
            data = f.read() #Gets the data
            self.claimdata = json.loads(data)
            
            self.claims_nether = url+"/tiles/_markers_/marker_world_nether.json"
            f = urllib.request.urlopen(self.claims_nether).read
            self.claimdatanether = json.loads(data)
            
            self.claims_end = url+"/tiles/_markers_/marker_world_the_end.json"
            f = urllib.request.urlopen(self.claims_end).read
            self.claimdataend = json.loads(data)
        except:
            print("Warning: Could not get claim data. This might be because your server does not support GriefProtection claims or the url was misconfigered. (Ignore if your server doesn't have GreifProtection installed)")
        
        
    def update(self): #Update the current dynmap information
        f = urllib.request.urlopen(self.link)
        data = f.read() #Gets the data
        self.decoded = json.loads(data)
        
        try:
            f = urllib.request.urlopen(self.claims)
            data = f.read() #Gets the data
            self.claimdata = json.loads(data)
            
            self.claims_nether = self.url+"/tiles/_markers_/marker_world_nether.json"
            f = urllib.request.urlopen(self.claims_nether).read
            self.claimdatanether = json.loads(data)
            
            self.claims_end = self.url+"/tiles/_markers_/marker_world_the_end.json"
            f = urllib.request.urlopen(self.claims_end).read
            self.claimdataend = json.loads(data)
        except:
            print("Warning: Could not get claim data. This might be because your server does not support GriefProtection claims or the url was misconfigered.")
        
    def getServerTick(self): #Returns time in Minecraft ticks, 0-24000 I think
        return self.decoded["servertime"]
        
    def getServerTime(self): #Example output: {"time":"19:00","canSleep":True}
        time = int(self.decoded["servertime"])
        str_time = ""
        
        hours = time / 1000.0
        hours += 6
        if hours > 24:
            hours -= 24
            
        mins = (hours - math.floor(hours)) * 60
        hours = int(hours)
        hours = str(hours)
        canSleep = False
    
        if mins >= 10:
            str_time = hours + ":" + str(int(mins))
        if mins < 10:
            str_time = hours + ":0" + str(int(mins))
            
        if time >= 12541 and time <= 23458:
            canSleep = True
        elif self.decoded["isThundering"] == "true":
            canSleep = True
        return {"time":str_time,"canSleep":canSleep}
        
    def getPlayers(self): #Gets JSON of current players
        players = self.decoded["players"]
        return players

    def getPlayerData(self,name): #Get player data for name
        p = self.getPlayers()
        for i in p:
            if i["name"].lower() == name.lower():
                return {
                    "name":i["account"],
                    "x":i["x"],
                    "y":i["y"],
                    "z":i["z"],
                    "health":i["health"],
                    "armor":i["armor"],
                    "world":i["world"]
                }
        raise Exception('The player does not exist in the pymc.dynmap.getPlayers() dictionary, possibly hidden on dynmap?') #I know it's bad python, but still :P
    
    def isThundering(self):
        return self.decoded["isThundering"]
    
    def hasStorm(self):
        return self.decoded["hasStorm"]
        
    def getFace(self,player,res="32x32"): #Returns the url for a player face, avaliable resolutions are 8x8,16x16,32x32
        url = self.url + "/tiles/faces/{0}/{1}.png".format(res,player) 
        if res not in ["32x32","16x16","8x8"]:
            raise Exception("Resolution must be '32x32','16x16' or '8x8'")
        try: 
            requests.get(url)
            return url
        except: raise Exception("The player does not exist in dynmap!")
    
    def getChunkImage(self,x1,z1,zoom=0,world="overworld",render="flat"):
        if world == "nether" or world == "world_nether":
            world = "world_nether"
        elif world == "end" or world == "world_the_end":
            world = "world_the_end"
        else:
            world = "world"
            
        if zoom == 0:
            zoom = ""
        else:
            zoom = "z"*zoom + "_"

        if render == "3d" and world == "world_nether":
            render = "nt"
        elif render == "3d" and world == "world_the_end":
            render = "et"
        elif render == "3d":
            render = "t"
        return self.url + "/tiles/"+world+"/"+ render + "/2_-3/"+zoom+str(int(math.floor(x1/32.0)))+"_"+str(int(math.floor(z1/32.0)))+".png"
        
        
    def getClaims(self):  #Gets all claims
        claims = self.claimdata["sets"]["griefprevention.markerset"]["areas"]
        claimsnether = self.claimdatanether["sets"]["griefprevention.markerset"]["areas"]
        claimsend = self.claimdataend["sets"]["griefprevention.markerset"]["areas"]
        
        returned = {}
        for key in claims:
            claim = claims[key]
            desc = claim["desc"]
            claimType = re.findall('<div class="regioninfo"> <strong>= (.*) =</strong><br>',desc)[0]
            claimID = key.split("_")[-1] 
            claimTeleport = "/tp " + re.findall('<br> /tp (.*)<br><br>',desc)[0].split("<br>")[0] 
            claimOwner = claim["label"] 
            claimPermTrust = re.findall('strong>Permission Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br>","").replace("<br/>","").split(', ')
            claimTrust = re.findall('strong>Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br>","").replace("<br/>","").split(', ')
            claimAccessTrust = re.findall('strong>Access Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br/>","").replace("<br>","").split(', ')
            claimContainerTrust = re.findall('strong>Container Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br/>","").replace("<br>","").split(', ')

            currentData = {
                "trust":claimTrust,
                "accessTrust":claimAccessTrust,
                "containerTrust":claimContainerTrust,
                "type":claimType,
                "ID":claimID,
                "claimTeleport":claimTeleport,
                "permTrust":claimPermTrust,
                "world":"overworld",
                "corners":[ claim["x"][0], claim["z"][0], claim["x"][3], claim["z"][2] ],
                "ybottom": claim["ybottom"],
                "ytop": claim["ytop"],
                "data": {
                        "fillColor": claim["fillcolor"],
                        "fillOpacity": claim["fillopacity"],
                        "label":claim["label"],
                    },
                "xwidth": abs(claim["x"][0] - claim["x"][3]),
                "zwidth": abs(claim["z"][0] - claim["z"][3]),
                "area": abs(claim["x"][0] - claim["x"][3]) * abs(claim["z"][0] - claim["z"][2])
                }
            returned[claimOwner+"_"+claimID+"_overworld"] = currentData
            
        for key in claimsnether:
            claim = claimsnether[key]
            desc = claim["desc"]
            claimType = re.findall('<div class="regioninfo"> <strong>= (.*) =</strong><br>',desc)[0]
            claimID = key.split("_")[-1] 
            claimTeleport = "/tp " + re.findall('<br> /tp (.*)<br><br>',desc)[0].split("<br>")[0] 
            claimOwner = claim["label"] 
            claimPermTrust = re.findall('strong>Permission Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br/>","").replace("<br>","").split(', ')
            claimTrust = re.findall('strong>Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br/>","").replace("<br>","").split(', ')
            claimAccessTrust = re.findall('strong>Access Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br/>","").replace("<br>","").split(', ')
            claimContainerTrust = re.findall('strong>Container Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br/>","").replace("<br>","").split(', ')

            currentData = {
                "trust":claimTrust,
                "accessTrust":claimAccessTrust,
                "containerTrust":claimContainerTrust,
                "type":claimType,
                "ID":claimID,
                "claimTeleport":claimTeleport,
                "permTrust":claimPermTrust,
                "world":"nether",
                "corners":[ claim["x"][0], claim["z"][0], claim["x"][3], claim["z"][2] ],
                "ybottom": claim["ybottom"],
                "ytop": claim["ytop"],
                "data": {
                        "fillColor": claim["fillcolor"],
                        "fillOpacity": claim["fillopacity"],
                        "label":claim["label"],
                    },
                "xwidth": abs(claim["x"][0] - claim["x"][3]),
                "zwidth": abs(claim["z"][0] - claim["z"][2]),
                "area": abs(claim["x"][0] - claim["x"][3]) * abs(claim["z"][0] - claim["z"][2])
                }
            returned[claimOwner+"_"+claimID+"_nether"] = currentData
            
        for key in claimsend:
            claim = claimsend[key]
            desc = claim["desc"]
            claimType = re.findall('<div class="regioninfo"> <strong>= (.*) =</strong><br>',desc)[0]
            claimID = key.split("_")[-1] 
            claimTeleport = "/tp " + re.findall('<br> /tp (.*)<br><br>',desc)[0].split("<br>")[0] 
            claimOwner = claim["label"] 
            claimPermTrust = re.findall('strong>Permission Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br>","").replace("<br/>","").split(', ')
            claimTrust = re.findall('strong>Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br>","").replace("<br/>","").split(', ')
            claimAccessTrust = re.findall('strong>Access Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br>","").replace("<br/>","").split(', ')
            claimContainerTrust = re.findall('strong>Container Trust:</strong><br>(.*)<br>',desc)[0].lstrip().replace("<br>","").replace("<br/>","").split(', ')

            currentData = {
                "trust":claimTrust,
                "accessTrust":claimAccessTrust,
                "containerTrust":claimContainerTrust,
                "type":claimType,
                "ID":claimID,
                "claimTeleport":claimTeleport,
                "permTrust":claimPermTrust,
                "world":"end",
                "corners":[ claim["x"][0], claim["z"][0], claim["x"][3], claim["z"][2] ],
                "ybottom": claim["ybottom"],
                "ytop": claim["ytop"],
                "data": {
                        "fillColor": claim["fillcolor"],
                        "fillOpacity": claim["fillopacity"],
                        "label":claim["label"],
                    },
                "xwidth": abs(claim["x"][0] - claim["x"][3]),
                "zwidth": abs(claim["z"][0] - claim["z"][3]),
                "area": abs(claim["x"][0] - claim["x"][3]) * abs(claim["z"][0] - claim["z"][2])
                },
            returned[claimOwner+"_"+claimID+"_end"] = currentData
        return returned
    
    def getClaimPlayer(self,name, world="all"): #Gets the claims of a certain player
        returned = []
        world = world.lower()
        claims = self.getClaims()
        for key in claims:
            if key.split("_")[0].lower() == name.lower(): #It's the player!!
                if world == key.split("_")[2] or world == "all":
                    returned.append(claims[key])
        return returned