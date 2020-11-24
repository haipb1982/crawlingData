import json
import requests
import time

# configs
# appId = '730'
# filesave='output-730.json'

# appId='570'
# filesave='output-570.json'

craw_steps = 199
status = 200
request_delay = 0.25

def processCrawling(appId, filesave):
    print("Start Crawling!!!")

    parms =''
    # url = 'https://inventories.cs.money/4.0/load_bots_inventory/{}?hasTradeLock=false&isStore=true&limit=60&offset={}'
    url ='https://inventories.cs.money/4.0/load_bots_inventory/{}?hasTradeLock=false&limit=60&offset={}'

    x= 1
    
    temp =[]
    while x < craw_steps or status !=200:
        try:
            response = requests.get(url.format(appId,str(x*60)))
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

        # time.sleep(request_delay)
        x += 1
    # end while x < 2 or status !=200:

    # update fullName ... from details
    print("Start Updating {} items!!!".format(len(temp)))
    url_update = 'https://cs.money/skin_info?appId={}&id={}&isBot=true&botInventory=true'

    k=0
    while k < len(temp):
        try:
            response = requests.get(url_update.format(appId,str(temp[k]['id'])))
            data  = json.dumps(response.json())
            status = response.status_code
            print('updating status {} id {} nameId {}'.format(status, temp[k]['id'],temp[k]['nameId']))
            
            details = json.loads(data)
            if 'fullName' in details:
                temp[k]['fullName']=details['fullName']
            elif 'name' in details:
                temp[k]['fullName']=details['name']
            else:
                temp[k]['fullName']=details['id']
        except:
            pass

        # time.sleep(request_delay)
        k+=1
    # end while k < len(temp)

    # write json file
    with open(filesave,'w') as f: 
        json.dump(temp, f, indent=4) 

# end processCrawling

def main():

    processCrawling('730','output-730.json')
    processCrawling('570','output-570.json')

# end main



if __name__ == "__main__":
    main()