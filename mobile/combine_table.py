# -*- coding: utf-8 -*-
import MySQLdb
import json

#connect to database
conn_data = MySQLdb.connect(
    host = "localhost",
    db = "zolmobile",
    user = "root",
    passwd = "12345678",
    charset = "utf8",
    use_unicode = True,
)

conn_newdb = MySQLdb.connect(
    host = "localhost",
    db = "zolmobile_infos",
    user = "root",
    passwd = "12345678",
    charset = "utf8",
    use_unicode = True,
)

cur_data = conn_data.cursor(cursorclass=MySQLdb.cursors.DictCursor)

cur_newdb = conn_newdb.cursor(cursorclass=MySQLdb.cursors.DictCursor)

#read from cur_data table
cur_data.execute("select * from price")
lines = cur_data.fetchall() #if too much data,use fetchmany on a cursor

#iterate through the price table
for line in lines:
    #info from price table
    proId = line['proId']
    source_url = line['source_url']
    anothername = line['anothername']
    #getting price from realprice table
    price = line['price']
    if price == "":
        cur_data.execute("select * from price_real where proId="+proId)
        temp_price = cur_data.fetchall()
        #if i can't find it, -1 --> dne
        if len(temp_price) == 0:
            price = -1
        #if i can find it but empty, problem from the website
        else:
            price = temp_price[0]['price']
            if price == "" or price == 0:
                price = -2
            else: 
                pass
    
    rate = line['rate']
    if rate == "":
        rate = 'null'
    commentCount = line['commentCount']
    if commentCount == "":
        commentCount = -1
    goodWords = line['goodWords']
    if goodWords == "":
        goodWords = 'null'
    badWords = line['goodWords']
    if badWords == "":
        badWords = 'null'
    #brand
    manuName = line['manuName']

    cur_data.execute("select * from info where zolproductid="+str(proId))
    temp_data = cur_data.fetchall()
    #ensure data found
    if len(temp_data) == 0:
        continue
    else:
        zolproduct = temp_data[0]['zolproduct']
        if anothername == "":
            anothername = zolproduct
        #model
        table = json.loads(temp_data[0]['spec'])
        release_date = table.get(u'上市日期','null')
        mobile_type = table.get(u'手机类型','null')
        os = table.get(u'操作系统', 'null')
        touch_type = table.get(u'触摸屏类型', 'null')
        screen_size = table.get(u'主屏尺寸', 'null')
        screen_material = table.get(u'主屏材质', 'null')
        resolution = table.get(u'主屏分辨率', 'null')
        ppi = table.get(u'屏幕像素密度', 'null')
        screen_percentage = table.get(u'屏幕占比', 'null')
        screen_other = table.get(u'其他屏幕参数', 'null')
        cpu_model = table.get(u'CPU型号', 'null')
        cpu_freq = table.get(u'CPU频率', 'null')
        core_num = table.get(u'核心数', 'null')
        ram = table.get(u'RAM容量', 'null')
        rom = table.get(u'ROM容量', 'null')
        sd_card = table.get(u'存储卡', 'null')
        storage_support = table.get(u'扩展容量', 'null')
        batt_type = table.get(u'电池类型', 'null')
        batt_size = table.get(u'电池容量', 'null')
        batt_charge = table.get(u'电池充电', 'null')
        info_4g = table.get(u'4G网络', 'null')
        info_3g = table.get(u'3G网络', 'null')
        network_freq = table.get(u'支持频段', 'null')
        sim_type = table.get(u'SIM卡类型', 'null')
        wlan = table.get(u'WLAN功能', 'null')
        connectivity = table.get(u'连接与共享', 'null')
        ports = table.get(u'机身接口', 'null')
        camera_total = table.get(u'摄像头总数', 'null')
        camera_back = table.get(u'后置摄像头', 'null')
        camera_front = table.get(u'前置摄像头', 'null')
        cmos = table.get(u'传感器类型', 'null')
        flash = table.get(u'闪光灯', 'null')
        aperture = table.get(u'光圈', 'null')
        video = table.get(u'视频拍摄', 'null')
        camera_func = table.get(u'拍照功能', 'null')
        design = table.get(u'造型设计', 'null')
        color = table.get(u'机身颜色', 'null')
        design_size = table.get(u'手机尺寸', 'null')
        weigh = table.get(u'手机重量', 'null')
        material = table.get(u'机身材质', 'null')
        interaction = table.get(u'操作类型', 'null')
        fingerprint = table.get(u'指纹识别设计', 'null')
        sensor_type = table.get(u'感应器类型', 'null')
        audio_supp = table.get(u'音频支持', 'null')
        video_supp = table.get(u'视频支持', 'null')
        pic_supp = table.get(u'图片支持', 'null')
        util = table.get(u'常用功能', 'null')
        other_util = table.get(u'其他功能参数', 'null')
        warrenty_policy = table.get(u'保修政策', 'null')
        warrenty_time = table.get(u'质保时间', 'null')
        warrenty_note = table.get(u'质保备注', 'null')
        warrenty_contact = table.get(u'客服电话', 'null')

        #data tuple to be inserted
        data_toinsert = tuple([proId,source_url,anothername,manuName,zolproduct,price,rate,commentCount,goodWords,badWords,release_date,mobile_type,os,touch_type,screen_size,screen_material,resolution,ppi, screen_percentage, screen_other, cpu_model, cpu_freq, core_num, ram, rom, sd_card, storage_support, batt_type, batt_size, batt_charge, info_4g, info_3g, network_freq, sim_type, wlan, connectivity, ports, camera_total, camera_back, camera_front, cmos, flash, aperture, video, camera_func, design, color, design_size, weigh, material, interaction, fingerprint, sensor_type, audio_supp, video_supp, pic_supp, util, other_util, warrenty_policy, warrenty_time, warrenty_note, warrenty_contact],)
        format_sql = 'insert into mobile (proId,source_url,anothername,manuName,zolproduct,price,rate,commentCount,goodWords,badWords,release_date,mobile_type,os,touch_type,screen_size,screen_material,resolution,ppi, screen_percentage, screen_other, cpu_model, cpu_freq, core_num, ram, rom, sd_card, storage_support, batt_type, batt_size, batt_charge, 4g, 3g, network_freq, sim_type, wlan, connectivity, ports, camera_total, camera_back, camera_front, cmos, flash, aperture, video, camera_func, design, color, design_size, weigh, material, interaction, fingerprint, sensor_type, audio_supp, video_supp, pic_supp, util, other_util, warrenty_policy, warrenty_time, warrenty_note, warrenty_contact) \
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        print format_sql % data_toinsert
        cur_newdb.executemany(format_sql, [data_toinsert,] )
        conn_newdb.commit()

print ("success")
cur_data.close()
cur_newdb.close()