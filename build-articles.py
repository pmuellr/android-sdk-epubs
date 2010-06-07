#!/usr/bin/env python

import re
import os
import sys
import shutil
import datetime
import zipfile

from cStringIO import StringIO

from helper import *

#-------------------------------------------------------------------------------
AndroidRootDir  = "-filled-in-later-"
ArticlesRootDir = "-filled-in-later-"
BuildDir        = "build/articles"

#-------------------------------------------------------------------------------
class Article:

    #---------------------------------------------------------------------------
    def __init__(self, link, title, description):
        self.link        = link
        self.title       = toHTML(title)
        self.description = toHTML(description)
        self.fileName    = os.path.basename(link)
        
        parts = os.path.splitext(self.fileName)
        self.baseFileName = parts[0]
        
        self.fileNameJD  = "%s.jd" % self.baseFileName
        self.id          = "article-%s" % self.baseFileName

    #---------------------------------------------------------------------------
    def __str__(self):
        return "%s: %s: %s" % (self.link, self.title, self.description)

    #---------------------------------------------------------------------------
    def toHTML(self, iDir, oDir):
        iFileName = os.path.join(iDir, self.fileNameJD)
        oFileName = os.path.join(oDir, self.fileName)
        
        iFile = open(iFileName)
        contents = iFile.read()
        iFile.close()
        
        contents = filterJDfile(contents)
        
        oFile = open(oFileName, "w")
        print >>oFile, '<html xmlns="http://www.w3.org/1999/xhtml">'
        print >>oFile, '<head>'
        print >>oFile, '<title>%s</title>' % self.title
        print >>oFile, '<link type="text/css" rel="stylesheet" href="../stylesheet.css" />'
        print >>oFile, '</head>'
        print >>oFile, '<body>'
        print >>oFile, '<h1>%s</h1>' % self.title

        oFile.write(contents)
        
        print >>oFile, '</body>'
        print >>oFile, '</html>'
        
        oFile.close()

#-------------------------------------------------------------------------------
def toHTML(string):
    return string.replace("&", "&amp;").replace("<", "lt;").replace(">", "gt;")

#-------------------------------------------------------------------------------
def buildZip():
    eFiles = []
    os.chdir("build/articles")
    
    for dirName, dirs, files in os.walk('.'):
        for file in files:
            eFiles.append(os.path.join(dirName, file)[2:])
    
    os.chdir("../..")
        
    eFiles = [x for x in eFiles if x != "mimetype"]
    
    zipFileName = "build/android-articles.epub"
    log("generating ePub file %s" % zipFileName)
    zipFile = zipfile.ZipFile(zipFileName, "w")
    
    zipFile.write("build/articles/mimetype", "mimetype")
    
    for eFile in eFiles:
        zipFile.write(os.path.join("build/articles", eFile), eFile)
        
    zipFile.close()
        
    
#-------------------------------------------------------------------------------
def writeMimetype():
    oFileName = "build/articles/mimetype"
    log("writing %s" % oFileName)
    
    oFile = open(oFileName, "w")
    oFile.write("application/epub+zip")
    oFile.close()

#-------------------------------------------------------------------------------
def fixTocNcx(articles):
    iFileName = "build/articles/OEBPS/toc.ncx"
    log("updating %s" % iFileName)
    
    iFile = open(iFileName)
    contents = iFile.read()
    iFile.close()
    
    sub = generateNavPoints(articles)
    
    contents = contents.replace("%navPoints%", sub)
    
    oFile = open(iFileName, "w")
    oFile.write(contents)
    oFile.close()

#-------------------------------------------------------------------------------
def fixContentOpf(articles):
    iFileName = "build/articles/OEBPS/content.opf"
    log("updating %s" % iFileName)
    
    iFile = open(iFileName)
    contents = iFile.read()
    iFile.close()
    
    manifestItems = generateManifestItems(articles)
    spineItems    = generateSpineItems(articles)
    dcDate        = datetime.date.today().isoformat()
    
    contents = contents.replace("%manifestItems%", manifestItems)
    contents = contents.replace("%spineItems%", spineItems)
    contents = contents.replace("%dcDate%", dcDate)
    
    oFile = open(iFileName, "w")
    oFile.write(contents)
    oFile.close()

#-------------------------------------------------------------------------------
def fixCoverHtml(articles):
    iFileName = "build/articles/OEBPS/cover.html"
    log("updating %s" % iFileName)

    iFile = open(iFileName)
    contents = iFile.read()
    iFile.close()
    
    date = datetime.datetime.now().isoformat(" ")
    
    contents = contents.replace("%date%", date)
    
    oFile = open(iFileName, "w")
    oFile.write(contents)
    oFile.close()
    
#-------------------------------------------------------------------------------
def generateManifestItems(articles):
    oStream  = StringIO()
    template = '    <item id="%s" href="content/%s" media-type="application/xhtml+xml"/>'
    
    for article in articles:
        print >>oStream, template % (article.id, article.fileName)

    result = oStream.getvalue()
    oStream.close()
    return result
    
    
#-------------------------------------------------------------------------------
def generateSpineItems(articles):
    oStream  = StringIO()
    template = '    <itemref idref="%s"/>'

    for article in articles:
        print >>oStream, template % article.id
    
    result = oStream.getvalue()
    oStream.close()
    return result

#-------------------------------------------------------------------------------
def generateNavPoints(articles):
    oStream = StringIO()
    
    index = 2
    for article in articles:
        print >>oStream, '    <navPoint id="navpoint-%d" playOrder="%d">' % (index, index)
        print >>oStream, '      <navLabel>'
        print >>oStream, '        <text>%s</text>' % article.title
        print >>oStream, '      </navLabel>'
        print >>oStream, '      <content src="content/%s"/>' % article.fileName 
        print >>oStream, '    </navPoint>'
        
        index += 1
    
    result = oStream.getvalue()
    oStream.close()
    return result

#-------------------------------------------------------------------------------
def filterJDfile(contents):
    patternPageTitle = re.compile(r'^page\.title=.*?$', re.DOTALL + re.MULTILINE)
    patternJDBody    = re.compile(r'^@jd:body$', re.DOTALL + re.MULTILINE)
    patternLink      = re.compile(r'{@link\s+(.*?)}')
    
    contents = patternPageTitle.sub("", contents)
    contents = patternJDBody.sub("", contents)
    contents = patternLink.sub(r"<code>\1</code>", contents)
    
    return contents
        
#-------------------------------------------------------------------------------
def buildIndexHTML(oDir, articles):
    oFileName = os.path.join(oDir, "index.html")
    oFile     = open(oFileName, "w")

    log("writing %s" % oFileName)
    
    print >>oFile, "<ul>"
    
    for article in articles:
        print >>oFile, "<li><p><a href='%s'>%s</a><br>%s" % (
            article.fileName,
            article.title,
            article.description
            )
    
    print >>oFile, "</ul>"
    
    oFile.close()

#-------------------------------------------------------------------------------
def readIndex():
    iFileName = "%s/index.jd" % ArticlesRootDir
    
    if not os.path.exists(iFileName): error("file not found: %s" % iFileName)
        
    log("reading %s" % iFileName)
    
    iFile = open(iFileName)
    contents = iFile.read()
    iFile.close()
    
# <dl>
#   <dt><a href="{@docRoot}resources/articles/avoiding-memory-leaks.html">Avoiding Memory Leaks</a></dt>
#   <dd>Mobile devices often have limited memory, and memory leaks can cause your application to waste this valuable resource without your knowledge. This article provides tips to help you avoid common causes of memory leaks on the Android platform.</dd>
# </dl>
  
    patternDL = re.compile(r'.*?<dl>(.*?)</dl>(.*)', re.DOTALL)
    patternDT = re.compile(r'.*<dt>.*<a\s*href\=\"(.*)\">(.*)</a>.*')
    patternDT = re.compile(r'.*<a\s*href\=\"(.*)\">(.*)</a>.*', re.DOTALL)
    patternDD = re.compile(r'.*<dd>(.*)</dd>.*', re.DOTALL)
    
    result = []
    
    match = patternDL.match(contents)
    while match:
        dlBody   = match.group(1)
        contents = match.group(2)
        
        dt = patternDT.match(dlBody)
        dd = patternDD.match(dlBody)
        
        if not dt: error("unable to interpret <dt> for %s" % dlBody)
        if not dd: error("unable to interpret <dd> for %s" % dlBody)
            
        link        = dt.group(1)
        title       = dt.group(2)
        description = dd.group(1)
        
        article = Article(link, title, description)
        result.append(article)
    
        match = patternDL.match(contents)
        
    return result

#-------------------------------------------------------------------------------
def copyImages():
    iDir = os.path.join(ArticlesRootDir, "images")
    oDir = "build/articles/OEBPS/content/images"
    
    log("copying images from %s to %s" % (iDir, oDir))
    shutil.copytree(iDir, oDir)
    
    
#-------------------------------------------------------------------------------
def main():
    global AndroidRootDir
    global ArticlesRootDir
    
    if len(sys.argv) < 2:
        error("expecting the Android source directory name as parameter")
        
    AndroidRootDir = sys.argv[1]
    ensureAndroidRoot(AndroidRootDir)
    
    ArticlesRootDir = os.path.join(AndroidRootDir, "frameworks/base/docs/html/resources/articles")
    
    ensureCurrentDirectory()
    copyTemplateFiles("articles")
    copyImages()
    
    articles = readIndex()

    oDir = "build/articles/OEBPS/content"
    for article in articles:
        article.toHTML(ArticlesRootDir, oDir)
        
    buildIndexHTML(oDir, articles)
    writeMimetype()
    fixTocNcx(articles)
    fixContentOpf(articles)
    fixCoverHtml(articles)
    
    buildZip()
    
#-------------------------------------------------------------------------------
if __name__ == "__main__": main()