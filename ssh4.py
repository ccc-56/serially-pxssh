#!/usr/bin/env python                                                               
 
import pexpect                                                                      
import pxssh                                                                        
import sys                                                                          
import random                                                                       
from time import gmtime, strftime, localtime                                        
import subprocess                                                                   
import argparse
import os
 
 
def randname():                                                                     
    howlongstr = 25                                                                 
    howlong = int(howlongstr)                                                       
    charsetstr = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'  
    return 'cmD' + ''.join( random.sample(charsetstr , howlong) )                   
 
def execiplist(ipfile,cmdfile,prefix):                                              
        fh = open(ipfile,"r")                                                       
        iplist=[]                                                                   
        for line in fh:                                                             
            try:                                                                    
                #delete the '#' start line                                          
                line = line.strip()                                                 
                if line.startswith('#'):                                            
                    continue                                                        
                else:                                                               
                    firstfield = line                                               
 
 
                #put values in iplist list                                           
                if firstfield:                                                       
 
                    eles = firstfield.split()                                        
                    ip = eles[0]                                                     
                    username = eles[1]                                               
                    passwd = eles[2]                                                 
                    rootpass = eles[3]                                               
                    print "%s begin:" % (ip,),
                    print "#"*100
 
                    #logfile                                                         
                    towritefile = outputdir + "/" + ip                               
                    fout = open(towritefile ,"w")                                     
 
                    #copy file                                                        
                    linecmd = 'scp  -o StrictHostKeyChecking=no -P 2222 ' + cmdfile +'  ' + username + '@' + ip + ':/tmp/' + prefix
                    print "running: " + linecmd                                        
                    ch1 = pexpect.spawn(linecmd,timeout=3)                             
                    ch1.logfile_read = fout                                                  
                    ch1.expect('password: ')                                            
                    ch1.sendline(passwd)                                                
                    ch1.expect(pexpect.EOF)                                             
 
 
                    #interactive execute copied cmdfile in above step
                    s = pxssh.pxssh()
                    s.logfile_read = fout
                    if not s.login(server=ip, username=username, password=passwd,port=20755):
                        print "ip = %s, SSH session failed on login." % (ip,)
                        print str(s)
                    else:
                        print "ip = %s, SSH session login successful" % (ip,)
                        s.sendline ("su - -c '/bin/bash /tmp/" + prefix +"'")
                        s.prompt()
                        print s.before
                        s.sendline(rootpass)
                        s.prompt()
                        print s.before
                        s.sendline("/bin/rm -f /tmp/" + prefix)
                        s.prompt()
                        print s.before
                        s.logout()
 
                    fout.close()
                    fh1 = open(towritefile,"r")   
                    towritefilenew = towritefile + ".ok"
                    fh2 = open(towritefilenew,"w")
                    for line in fh1:
                        line = line.strip()
                        newline = removecontrolcharacters(line)
                        fh2.write(newline + "\n")
                    fh1.close() 
                    subprocess.call(["rm", "-f",towritefile])
                    fh2.close() 
                    print "logdir = %s" % (towritefilenew,)
                    print "%s end." % (ip,),
                    print "#"*100
                    print """
 
 
                          """
            except ValueError,e:
                print "the input file have wrong format: ",str(e)
                print "%s end." % (ip,),
                print "#"*100
                print """
 
 
                      """
            except pexpect.TIMEOUT, e1:
                print "%s timeout. " % (ip,)
                print "%s end." % (ip,),
                print "#"*100
                print """
 
 
                      """
def removecontrolcharacters(line):
    newln = ""
    for c in line:
        if c >= chr(32):
            newln = newln + c
    return newln
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iplist","-ip", help="iplist filename, which line has fields: ip, username, passwd, rootpass")
    parser.add_argument("--cmdfile","-cmd", help="command list filename, which have command list")
    args = parser.parse_args()
    if args.iplist and args.cmdfile:
        if os.path.exists(args.iplist):
            if os.path.exists(args.cmdfile):
                #print "iplist = %s and cmdfile = %s" % (args.iplist, args.cmdfile)
                currenttime = strftime("%Y%m%d%H%M%S", localtime())
                pref = "_" + sys.argv[0].replace('.py','')
                outputdir = "output" + currenttime + pref
                subprocess.call(["mkdir", "-p",outputdir])
 
                tmpprefix = randname()
                execiplist(args.iplist, args.cmdfile, tmpprefix)
            else:
                print "%s does not exists" % (args.cmdfile,)
                os._exit(11)
        else:
            print "%s does not exists" % (args.iplist,)
            os._exit(12)
			