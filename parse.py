# Download all content from web: wget -r -nc http://www.dougschmittantiques.com/
# Scp images to server: scp -rp * root@172.28.195.229:/var/www/wordpress/wp-content/images/
# Register all media:  for i in {0..99}; do sudo wp media import $i/* --allow-root --path=/var/www/html; rm -r $i; done

import os
import sys
from pathlib import Path
from html.parser import HTMLParser
import hashlib

excluded_text = ["","\n","\n\n",'www.dougschmittantiques.com','\xa0',' or ']
excluded_images = ['signsSOLD_17055.gif','SOLD_17055.gif']


class MyHTMLParser(HTMLParser):
    startTitle = False;
    startBody = False;
    title = "";
    description = "";
    images = "";

    def handle_starttag(self, tag, attrs):
        tag = tag.lower();

        if tag == 'title':
            self.startTitle = True;
        if tag == 'img':
            for attr in attrs:
                if attr[0] == 'src' and attr[1] not in excluded_images:
                    if self.images != "":
                        self.images = f"{self.images},{attr[1]}"
                    else:
                        self.images = f"{attr[1]}"
        if tag == 'body':
            self.startBody = True;



    def handle_endtag(self, tag):
        if tag == 'title':
            self.startTitle = False;
        if tag == 'body':
            self.startBody = False;


    def handle_data(self, data):
        if(self.startTitle):
            self.title = self.title + data.replace('\n', ' ')

        if(self.startBody):
            if data not in excluded_text:
                self.description = self.description + data.replace("\"","\"\"") + "\n"


    def __init__(self):
        HTMLParser.__init__(self)

rootdir = "C://temp//www.dougschmittantiques.com//"
outfileName = "py-outfile.txt" # hardcoded path
folderOut = open( outfileName, 'w' )
folderOut.write('sku,title,categories,stock,description,images,"Attribute 1 name","Attribute 1 value(s)","Attribute 1 visible","Attribute 1 global"\n')

result = list(Path(rootdir).rglob("*.[hH][tT][mM]"))

img_count = 0
file_count = 0

for file in result:
    file_count = file_count + 1

    f = open(file, 'r' ,encoding='UTF-8', errors='ignore')
    toWrite = f.read()
    parser = MyHTMLParser()
    parser.feed(toWrite);

    images = ""

    for img in parser.images.split(","):
        if "SOLD_17055" in img:
            continue;
        if img == '':
            continue;

        img_cleaned = img.replace("http://www.dougschmittantiques.com/","").replace("%20"," ");
        fileLocation = Path(f"{file.parent}/{img_cleaned}").resolve();
        newFilename = f"{os.path.relpath(fileLocation,rootdir)}".replace('/','__').replace('\\','__').replace(" & ","-").replace("'","").replace("(","").replace(")","").replace(" ","-");

        newFileDir = f"image_links2/{img_count % 100}";
        newFileLocation = f"{newFileDir}/{newFilename}".replace(" & ","-").replace("'","").replace("(","").replace(")","").replace(" ","-").replace("%20","-");
        os.makedirs(newFileDir, exist_ok=True)
        wpFileName = os.path.splitext(newFilename)[0]

        if os.path.exists(fileLocation):
            if not os.path.islink(newFileLocation):
                os.symlink(fileLocation, newFileLocation);

            if images == "":
                images = wpFileName
            else:
                images = images + f",{wpFileName}"

            img_count = img_count + 1;
        else:
            print ("no such file");

    category = ""

    if len(file.parts) > 4:
        category = file.parts[3]

    shash = int(hashlib.md5(str(file).encode()).hexdigest(), 16) % (10 ** 10)

    #if "Visit to " in parser.title:
    if images != '':
        folderOut.write(f'{shash},{parser.title},{category},0,"{parser.description}","{images}","Old URL","{str(file)}",0,0\n')
    #f.close()

folderOut.close()
