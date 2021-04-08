import json
import requests
import time

# ------------ configs ------------ #
craw_steps = 99 # get 60 items per step
status = 200
request_delay = 0.25

# ------------ suport functions ------------ #

# function to add to JSON 
def write_json(data, filename='data.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4) 

def processCrawling(appId, filesave):

    print("Start Crawling!!!")    
    x= 1    
    temp =[]
    while x < craw_steps or status !=200:
        try:
            url ='https://inventories.cs.money/4.0/load_bots_inventory/{}?hasTradeLock=false&limit=60&offset={}'
            response = requests.get(url.format(appId,str(x*60)))
            time.sleep(request_delay)
            data  = json.dumps(response.json())
            status = response.status_code
            print('crawling status {} step {}'.format(status, x))

            item_dict = json.loads(data)
            print(len(item_dict['items']))
            
            for data_items in item_dict['items']:
                d = {}
                for key, value in data_items.items():
                    if key=='nameId':
                        d['nameId'] = value
                        d['fullName'] =''
                    if key=='price':
                        d['price'] = value
                    if key=='id':
                        d['id'] = value
                # print(d)
            
                # does not exist
                if d is not None:
                    i=0
                    while i < len(temp):
                        if d['nameId'] == temp[i]['nameId']:
                            if d['price'] > temp[i]['price']:                            
                                d['price'] = temp[i]['price']   
                            del temp[i]              
                        i+=1
                        
                    temp.append(d)
                    
                # end if d is not None

            # end for data_items in item_dict['items']:           
        except:
            pass

        x += 1
    # end while x < 2 or status !=200:

    # update fullName 
    print("Start Updating {} items!!!".format(len(temp)))
   
    with open('fullName.json') as json_file:
        data_fname = json.load(json_file)     

        k=0    
        while k < len(temp):
            try:
                print('updating nameId {}'.format( temp[k]['nameId']))

                fname =''
                # get full name in filesave
                for p in data_fname:
                    if temp[k]['nameId'] == p['nameId']:
                        fname = p['fullName']

                # get full name by crawling
                if fname =='':
                    url_update = 'https://cs.money/skin_info?appId={}&id={}&isBot=true&botInventory=true'
                    response = requests.get(url_update.format(appId,str(temp[k]['id'])))
                    time.sleep(request_delay)
                    data  = json.dumps(response.json())
                    status = response.status_code            
                                    
                    details = json.loads(data)
                    if 'fullName' in details:
                        temp[k]['fullName']=details['fullName']
                    elif 'name' in details:
                        temp[k]['fullName']=details['name']
                    else:
                        temp[k]['fullName']=details['id']
                    
                    # add missing fullName
                    n = {}
                    n['nameId'] = temp[k]['nameId']
                    n['fullName'] = temp[k]['fullName']

                    data_fname.append(n)

                else:
                    temp[k]['fullName']= fname
                    
            except:      
                pass

            k+=1

        # end while k < len(temp)

    # end with open('fullName.json')

    # write json file cs, dota

    write_json(data_fname,'fullName.json')
    write_json(temp,filesave)

# end processCrawling

# ------------ main function ------------ #

def main():

    processCrawling('730','output-cs.json')
    processCrawling('570','output-dota.json')

# end main

if __name__ == "__main__":
    main()