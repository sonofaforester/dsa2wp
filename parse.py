import os
import sys
from pathlib import Path
from html.parser import HTMLParser

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

rootdir = os.getcwd()
outfileName = rootdir + "/py-outfile.txt" # hardcoded path
folderOut = open( outfileName, 'w' )
folderOut.write('sku,title,categories,description,images,"Attribute 1 name","Attribute 1 value(s)","Attribute 1 visible","Attribute 1 global"\n')

result = list(Path("./original_site").rglob("*.[hH][tT][mM]"))

count = 0

for file in result:

    f = open(file, 'r' ,encoding='UTF-8', errors='ignore')
    toWrite = f.read()
    parser = MyHTMLParser()
    parser.feed(toWrite);

    images = ""

    for img in parser.images.split(","):
        if "SOLD_17055" in img:
            continue;

        img = img.replace("http://www.dougschmittantiques.com/","");
        fileLocation = Path(f"{file.parent}/{img}").resolve();
        newFilename = f"{os.path.relpath(fileLocation).replace('/','__')}".replace(" & ","-").replace("'","").replace("(","").replace(")","").replace(" ","-");

        newFileDir = f"image_links/{count % 100}/";
        newFileLocation = f"{newFileDir}/{newFilename}".replace(" & ","-").replace("'","").replace("(","").replace(")","").replace(" ","-");
        os.makedirs(newFileDir, exist_ok=True)
        wpFileName = os.path.splitext(newFilename)[0]

        if os.path.exists(fileLocation):
            if not os.path.islink(newFileLocation):
                os.symlink(fileLocation, newFileLocation);
                count = count + 1;

            if images == "":
                images = wpFileName
            else:
                images = images + f",{wpFileName}"
        else:
            print ("no such file");

    category = ""

    if len(file.parts) > 2:
        category = file.parts[1]

    shash = abs(hash(str(file))) % (10 ** 10)

    #if "Visit to " in parser.title:
    folderOut.write(f'{shash},{parser.title},{category},"{parser.description}","{images}","Old URL","{str(file)}",0,0\n')
    #f.close()

folderOut.close()
