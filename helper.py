#!/usr/bin/env python

import sys
import os.path
import shutil

PROGRAM_NAME = os.path.basename(sys.argv[0])

#-------------------------------------------------------------------------------
def log(messages):
    if not list == type(messages): messages = [messages]
    
    for message in messages:
        print "%s: %s" % (PROGRAM_NAME, message)

#-------------------------------------------------------------------------------
def error(messages):
    log(messages)
    sys.exit()

#-------------------------------------------------------------------------------
def ensureAndroidRoot(dir):
    if not os.path.isdir(dir): 
        error("directory not found: %s" % dir)
        
    if not os.path.exists(os.path.join(dir, "frameworks")):
        error("directory is not the Android source directory: %s" % dir)

#-------------------------------------------------------------------------------
def ensureCurrentDirectory():
    if os.path.isdir("epub-template-files"): return
    
    error("this program must be run from it's directory")

#-------------------------------------------------------------------------------
def copyTemplateFiles(name):
    iDir = "epub-template-files/%s" % name
    oDir = "build/%s" % name

    if os.path.exists(oDir):
        log("erasing %s" % oDir)
        shutil.rmtree(oDir)
    
    log("copying: %s to %s" % (iDir,oDir))
    shutil.copytree(iDir, oDir)
    
    
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    print "This file is not intended to be used as a main program"

