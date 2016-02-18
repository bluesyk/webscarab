#-*- coding: utf-8 -*-
import os
import m3u8
import binascii
import shutil
import traceback
import mmap
import logging


#检测下载的日志文件，看是否下载成功
def checkdown():
    f = open('download.log')
    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    return s.find('(OK):download completed.(ERR):error occurred.') == -1


#删除目录函数
def remove_folder(path):
    # check if folder exists
    if os.path.exists(path):
         # remove if exists
         shutil.rmtree(path)

#Get m3u8 file in output directory
def GetFileList(dir, fileList):
    newDir = dir
    if os.path.isfile(dir):
        if dir.find(".key") == -1:
            fileList.append(dir.decode('gbk'))
    elif os.path.isdir(dir):
        for s in os.listdir(dir):
            newDir=os.path.join(dir,s)
            GetFileList(newDir, fileList)
    return fileList

#Decode hls encrypt key
def getkey(key):
    if len(key)<17:
        return key;
    result = bytearray(16);
    result[0:2]= key[9:11];
    result[2:8]=key[3:9];
    result[8:10]=key[1:3];
    result[10:16]=key[11:17];
    return  binascii.hexlify(result);


#读取上层目录下的key和m3u8文件
list = GetFileList('..\output', [])
print  'total m3u8 fies:' +str(len(list))
for count, m3u8file in enumerate(list, start=1):
    keyfile = m3u8file.replace('.m3u8','.key');

    #计算删除文件中文名称
    cn_outputfile =  m3u8file.replace('.m3u8','.mp4');
    index = cn_outputfile.rfind('\\');
    cn_outputfile = cn_outputfile[index+1:];

    #由于ffmpege的中文支持问题，临时文件用数字
    outputfile = 'job'+str(count)+'.mp4';
    print '\r\n'
    print 'm3u8 file:' +m3u8file
    print 'key  file:' +keyfile
    print 'tmp  file:' +outputfile
    try:
        fo =  open(keyfile);
        keystr=fo.read();
        fo.close();
        key=getkey(bytearray(keystr));
        print 'key    is:'+ key;

        # set openssl.exe ,ffmpeg.exe in path
        if not os.path.exists('decrypted.hls'):
            os.mkdir('decrypted.hls');

        #生成解密视频数据的脚本，生成下载文件清单和解密文件清单
        decryptbat = open('decrypt.bat','w');
        listfile = open('list.txt','w');
        wgetfile = open('wget.txt','w');

        m3u8_obj = m3u8.load(m3u8file);
        for seg in m3u8_obj.segments:
            wgetfile.write(seg.uri+'\r\n');
            index=seg.uri.rfind('/')+1;
            seg_filename= seg.uri[index:];
            decryptbat.write('openssl aes-128-cbc -d -K '+key+' -iv '+ seg.key.iv[2:]+ ' -in encrypted.hls\\' +seg_filename+ ' -out decrypted.hls\\' +seg_filename+'\r\n');
            listfile.write('file \'decrypted.hls\\' +seg_filename +'\'\r\n');
        wgetfile.close();
        listfile.close();
        decryptbat.close();

        #生成视频合并脚本
        mergebat = open('merge.bat','w');
        mergebat.write('ffmpeg.exe   -f concat -i list.txt -c copy -bsf:a aac_adtstoasc '+outputfile)
        mergebat.close();

        #生成视频下载脚本
        wgetbat= open('download.bat','w')
        wgetbat.write('aria2c -c -s 5 -d "encrypted.hls" -j 2 -i wget.txt');
        wgetbat.close();

        #按顺序执行脚本，如果download下载失败，丢出停止，停止decrrpt和merge等步骤。
        print 'begin to download hls segments(' +str(len(m3u8_obj.segments)) +')'
        os.system('download.bat >download.log');
        if not checkdown():
            raise Exception('donwload error!')
        else:
            print 'end of download ' +m3u8file

        print 'begin to decrypt hls segments ...'
        os.system('decrypt.bat > decrypt.log 2>&1')
        os.system('merge.bat')

        # 修改为中文名称
        os.rename(outputfile,cn_outputfile)
        print 'out  file:' +cn_outputfile

        #删除已成功下载的m3u8文件
        os.remove(m3u8file)
        os.remove(keyfile)
    except:
        print 'failed to process m3u8 file:' +m3u8file
        #print traceback.print_exc()
        pass
    finally:
        #clean tmp file
        remove_folder("decrypted.hls")
        remove_folder("encrypted.hls")
        os.remove('wget.txt');
        os.remove('download.bat');
        os.remove('decrypt.bat');
        os.remove('decrypt.log');
        os.remove('merge.bat');
        os.remove('list.txt');

