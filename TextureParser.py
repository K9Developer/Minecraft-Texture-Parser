import datetime
import json
import os
import sys
import time
from multiprocessing.pool import ThreadPool
from pathlib import Path
import requests
import base64
#2980c7aed04246fec77ed0f14ad40fb4
import PIL.Image
from PIL import ImageOps

def texture_parser(path,res=None):
    def recursive_with_rglob(dir):
        assert dir.is_dir() # again, check if dir is dir
        stri = '\r' + f'Extracting all images from {dir}'
        print(stri)
        return [(str(file), file.name) for file in dir.rglob('*.png')]

    images = recursive_with_rglob(Path(path))

    def get_res():
        for t,i in enumerate(images):
            d = PIL.Image.open(i[0])
            w, h = d.size
            if w==h:
                return w

    if res == None:
        res = get_res()
        print(f'res argument was not given.. resoulotion detected: {res}x{res}')

    directories = []
    image_names = []
    urls = []
    wait_times = []

    print('Filtering images...')
    for i in images:
        d = PIL.Image.open(i[0])
        w, h = d.size
        if h%res == 0 and h != res and w==res:
            border = (0, h-res, 0, 0)
            d = ImageOps.crop(d, border)
            d.save(i[0])
            print(f'Converted animations to image - {i[0]}')
        else:
            continue

    for i in images:
        d = PIL.Image.open(i[0])
        w, h = d.size
        if h == res and w == res and '_layer_' not in i:
            if not i[0].split('_')[-1].replace('.'+i[0].split('.')[1], '').isdigit():
                directories.append(i[0])
        else:
            continue


    for i in directories:
        ii = os.path.basename(i)
        image_names.append(ii.replace('.png', ''))

    url = "https://api.imgbb.com/1/upload"
    print(f'Found {len(directories)} textures!')
    for t,i in enumerate(directories):
        with open(i, "rb") as file:
            payload = {
                "key": "2980c7aed04246fec77ed0f14ad40fb4",
                "image": base64.b64encode(file.read()),
                "album": 'KcWtLb'
            }
            start_time = time.time()
            res = requests.post(url, payload)
        if json.loads(res.text)['status'] == 200:
            urls.append(json.loads(res.text)['data']['url'])
            end_time = time.time()
            wait_time = (end_time - start_time)
            wait_times.append(wait_time)
            wait_time = (sum(wait_times) / len(wait_times)) * (len(directories) - t + 1) - 1
            wait_time = str(datetime.timedelta(seconds=wait_time)).split('.')[0]
            spaces = len(max(directories, key=len)) - len(i)
            stri = '\r uploading images: ' + str(t + 1) + '/' + str(len(
                directories)) + f' - {i}  {" " * spaces} -- estimated wait time: {str(wait_time).replace(".", "")} --'
            sys.stdout.write(stri)
            sys.stdout.flush()
        else:
            print('ERROR')
            print(i + "\n" + str(json.loads(res.text)))
            quit()


    with open('TextureData.txt', 'a') as f:
        f.write('{\n')
        for i,t in enumerate(urls):
            try:
                f.write(f'"{image_names[i]}": "{t}"{"," if i != len(urls)-1 else ""}\n')
            except:
                print('\nError occurred.. ignoring')
        f.write('}')

    print(f'\nUploaded and wrote all images! opening dictionary file (file directory: {os.path.abspath("TextureData.txt")})')
    os.startfile('TextureData.txt')

texture_parser(path='path')
