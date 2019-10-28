import datetime
import time

import MySQLdb as mysql
import GeoIP, requests, xlsxwriter
from bs4 import BeautifulSoup
from utils import logger
import geoip2.database
import ipinfo

class report_generator:
    __each_area_tab_name = "Each Area"
    __top_authetication_tab = "Top Authentications"
    __top_ttacker_tab_name = "Top Attacker"
    __top_iranian_attacker_tab_name = "Iranian Top Attacker"
    __top_iranian_attacker_protocol_tab_name = "Top Iranian Attacker Protocol"
    __attack_time_tab_name = "Attack Time"
    __protocol_count_tab_name = "Protocols"
    __per_day_count_tab_name = "Days"
    __protocol_per_day_tab_name = "protocol_per_day"
    __top_attacker_per_day_tab_name = "Top_attacker_per_day"
    __top_country = "top country"
    __top_country_protocol = "top country protocol"
    __attacker_info = "Attacker Information"
    __interface_count = "Interface Count"
    __interface_protocol_count = "Interface Protocol Count"
    __interface_checker = "Attack Check Between Interfaces"
    __smtp_ehlo_tabs = "SMTP Server"
    __bot_detection = "Bot Detection"
    __brute_force_tab = "Brute Force Attacks"
    __port_scan_tab = "Port Scan "

    @staticmethod
    def convert_date_timestamp(date_s):
        import time
        timestamp = time.mktime(time.strptime(date_s, '%Y-%m-%d_%H:%M:%S'))
        return timestamp

    def __init__(self, file_name="report", from_date="", to_date=""):
        self.line = "-------------------------------"
        self.filename = file_name
        self.open_file()
        self.from_date = str(report_generator.convert_date_timestamp(from_date))
        # logger.info( self.from_date,type(self.from_date)
        self.to_date = str(report_generator.convert_date_timestamp(to_date))
        self.db = mysql.connect("localhost", "amin", "amin", "honeypot")
        self.lab_db = mysql.connect("localhost", "amin", "amin", "honeypot_lab")
        self.cursor = self.db.cursor()
        self.lab_cursor = self.lab_db.cursor()
        # self.gi = GeoIP.open("GeoLiteCity.dat", GeoIP.GEOIP_INDEX_CACHE | GeoIP.GEOIP_CHECK_CACHE)
        self.gi = geoip2.database.Reader('GeoLite2-City.mmdb')
        self.area_count = {
            'web': 0,
            'linux': 0,
            'win': 0,
            'any': 0
        }
        self.top_attacker_count = 80
        self.top_attacker_list = []

    def open_file(self):
        self.workbook = xlsxwriter.Workbook(self.filename + ".xlsx")
        self.bold = self.workbook.add_format({'bold': True, 'bg_color': 'green'})

    def ensure_unicode(self, v):
        if isinstance(v, str):
            try:
                v = v
                v = v.decode('utf8')
            except UnicodeDecodeError as e:
                v = v
                v = v.decode('latin-1')
        # return unicode(v)
        return v

    def each_protocols(self):
        logger.info(self.line)
        logger.info("Each Protocol Report Generation")
        for key in self.__dic:
            worksheet = self.workbook.add_worksheet(key)
            worksheet.write('A1', 'IP', self.bold)
            worksheet.write('C1', 'COUNT', self.bold)
            worksheet.write('B1', 'COUNTRY', self.bold)
            sql = self.each_protocol_query % (self.from_date, self.to_date, key)
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            i = 0
            for row in results:
                # logger.info( row
                i = i + 1
                self.area_count[self.__dic[key]['area']] = self.area_count[self.__dic[key]['area']] + int(row[2])
                worksheet.write(i, 0, self.ensure_unicode(row[0]))
                worksheet.write(i, 1, self.ensure_unicode(row[1]))
                worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def top_authentication(self):
        logger.info(self.line)
        logger.info("Authentications Report Generation")
        worksheet = self.workbook.add_worksheet(self.__top_authetication_tab)
        worksheet.write('A1', 'USERNAME', self.bold)
        worksheet.write('C1', 'PASSWORD', self.bold)
        worksheet.write('B1', 'COUNT', self.bold)
        sql = self.top_authentication_query
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        i = 0
        for row in results:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def each_area(self):
        logger.info(self.line)
        logger.info("Each Area Report Generation")
        worksheet = self.workbook.add_worksheet(self.__each_area_tab_name)
        worksheet.write('A1', 'Linux Area', self.bold)
        worksheet.write('B1', 'Windows Area', self.bold)
        worksheet.write('C1', 'Web Area', self.bold)
        worksheet.write('D1', 'PCAP', self.bold)
        worksheet.write(1, 0, self.area_count['linux'])
        worksheet.write(1, 1, self.area_count['win'])
        worksheet.write(1, 2, self.area_count['web'])
        worksheet.write(1, 3, self.area_count['any'])

    def top_attacker(self):
        logger.info(self.line)
        logger.info("Top Attacker Report Generation")
        count = 0
        worksheet = self.workbook.add_worksheet(self.__top_ttacker_tab_name)
        worksheet.write('A1', 'IP', self.bold)
        worksheet.write('B1', 'Count', self.bold)
        worksheet.write('C1', 'Country', self.bold)
        sql = self.top_attacker_query % (self.from_date, self.to_date, self.top_attacker_count)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        i = 0

        for row in results:
            # print(row[0])
            i = i + 1
            self.top_attacker_list.append(row[0])
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            com = ""
            try:
                # com = self.gi.record_by_name(row[0])['country_name']
                response = self.gi.city(row[0])
                com1 = response.country.name
                com = com1.replace("'", " ")
            except Exception as e:
                com = "Not Found"
            worksheet.write(i, 2, self.ensure_unicode(com))

    def top_Iranian_attacker(self):
        logger.info(self.line)
        logger.info("Top Iranian Attacker Report Generation")
        count = 0
        worksheet = self.workbook.add_worksheet(self.__top_iranian_attacker_tab_name)
        worksheet.write('A1', 'IP', self.bold)
        worksheet.write('B1', 'Count', self.bold)
        worksheet.write('C1', 'Country', self.bold)
        sql = self.top_iranian_attacker_query.format(from_date=str(self.from_date), to_date=str(self.to_date),
                                                     limit=self.top_attacker_count)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        i = 0
        for row in results:
            i = i + 1
            self.top_attacker_list.append(row[0])
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            com = ""
            try:
                com = self.gi.record_by_name(row[0])['country_name']
            except Exception as e:
                com = "Not Found"
            worksheet.write(i, 2, self.ensure_unicode(com))

    def top_Iranian_attacker_protocol(self):
        logger.info(self.line)
        logger.info("Top Iranian Attacker Protocol Report Generation")
        count = 0
        worksheet = self.workbook.add_worksheet(self.__top_iranian_attacker_protocol_tab_name)
        worksheet.write('A1', 'Protocol', self.bold)
        worksheet.write('B1', 'IP', self.bold)
        worksheet.write('C1', 'Count', self.bold)
        worksheet.write('D1', 'Country', self.bold)
        sql = self.top_iranian_attacker_protocol_query.format(from_date=str(self.from_date),
                                                              to_date=str(self.to_date),
                                                              limit=self.top_attacker_count)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        i = 0
        for row in results:
            i = i + 1
            self.top_attacker_list.append(row[0])
            worksheet.write(i, 1, self.ensure_unicode(row[0]))
            worksheet.write(i, 0, self.ensure_unicode(row[1]))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))
            com = ""
            try:
                com = self.gi.record_by_name(row[0])['country_name']
            except Exception as e:
                com = "Not Found"
            worksheet.write(i, 3, self.ensure_unicode(com))

    def Attack_time_group(self):
        logger.info(self.line)
        logger.info("Attack Time Report Generation")
        sql = self.attack_time_query % (self.from_date, self.to_date)
        worksheet = self.workbook.add_worksheet(self.__attack_time_tab_name)
        worksheet.write('A1', 'Hour', self.bold)
        worksheet.write('B1', 'Attack Count', self.bold)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        i = 0
        for row in results:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))

    def per_protocol(self):
        logger.info(self.line)
        logger.info("Per Protocol Report Generation")
        self.cursor.execute(self.per_protocol_query % (self.from_date, self.to_date))
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__protocol_count_tab_name)
        worksheet.write('A1', 'protocol', self.bold)
        worksheet.write('B1', 'Count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))

    def per_day(self):
        logger.info(self.line)
        logger.info("Per Day Report Generation")
        query = self.attack_per_day_query % (self.from_date, self.to_date)
        # logger.info( query
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__per_day_count_tab_name)
        worksheet.write('A1', 'month', self.bold)
        worksheet.write('B1', 'day', self.bold)
        worksheet.write('C1', 'count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            if int(self.ensure_unicode(row[0])) <10:
                worksheet.write(i, 0,'0'+ str(self.ensure_unicode(row[0])))
            else:
                worksheet.write(i, 0, str(self.ensure_unicode(row[0])))
            if int(self.ensure_unicode(row[1])) <10:
                worksheet.write(i, 1, '0'+ str( self.ensure_unicode(row[1])))
            else:
                worksheet.write(i, 1, str(self.ensure_unicode(row[1])))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def top_country(self):
        logger.info(self.line)
        logger.info("Top country Report Generation")
        query = self.top_country_query % (self.from_date, self.to_date)
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        print(type(per_protocol_result))
        # print(per_protocol_result[0])
        worksheet = self.workbook.add_worksheet(self.__top_country)
        worksheet.write('A1', 'country', self.bold)
        worksheet.write('B1', 'count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            # print(row )
            com1 = self.ensure_unicode(row[0])
            if com1 == None:
                com = str(None)
            else:
                com = com1.replace("'", " ")

            worksheet.write(i, 0, self.ensure_unicode(com))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))

    def top_between_interface(self):
        logger.info(self.line)
        logger.info("attacker between interface ")
        query = self.top_interface_checker_query % (self.from_date, self.to_date)
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__interface_checker)
        worksheet.write('A1', 'attacker', self.bold)
        worksheet.write('B1', 'count of interface', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))

    def smtp_server(self):
        logger.info(self.line)
        logger.info("SMTP Server ")
        query = self.smtp_server_helo_query % ("%")
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__smtp_ehlo_tabs)
        worksheet.write('A1', 'SMTP Server', self.bold)
        worksheet.write('B1', 'Hit rate', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))

    def brute_force_detection(self):
        logger.info(self.line)
        logger.info("Brute Force Detection ")
        query = self.brute_force_attacker_query % (self.from_date, self.to_date)
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__brute_force_tab)
        worksheet.write('A1', 'Attacker', self.bold)
        worksheet.write('B1', 'protocol', self.bold)
        worksheet.write('C1', 'hit rate', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def port_scan_detection(self):
        logger.info(self.line)
        logger.info("port Scan Detection ")
        query = self.port_scan_query % (self.from_date, self.to_date , self.from_date, self.to_date)
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__port_scan_tab)
        worksheet.write('A1', 'Attacker', self.bold)
        worksheet.write('B1', 'first Protocol', self.bold)
        worksheet.write('C1', 'Second Protocol', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def bot_detection_function(self):
        logger.warning(self.line)
        logger.warning("Bot Detection")
        query = ""
        worksheet = self.workbook.add_worksheet(self.__bot_detection)
        worksheet.write('A1', 'bot name', self.bold)
        worksheet.write('B1', 'Hit rate', self.bold)
        i = 0
        for x in self.bot_detection:
            query = self.bot_detection[x]
            print (query)
            self.cursor.execute(query)
            i = i + 1
            per_protocol_result = self.cursor.fetchall()
            for row in per_protocol_result:
                worksheet.write(i, 0, str(x))
                worksheet.write(i, 1, self.ensure_unicode(row[0]))

    def top_country_protocol(self):
        logger.info(self.line)
        logger.info("Top country Report Generation")
        query = self.top_country_protocol_query % (self.from_date, self.to_date)
        self.cursor.execute(query)
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__top_country_protocol)
        worksheet.write('A1', 'country', self.bold)
        worksheet.write('B1', 'protocol', self.bold)
        worksheet.write('C1', 'count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            com1 = self.ensure_unicode(row[0])
            if com1 == None:
                com = str(None)
            else:
                com = com1.replace("'", " ")

            worksheet.write(i, 0,  self.ensure_unicode(com))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def per_protocol_day(self):
        logger.info(self.line)
        logger.info("Protocol Per Day Report Generation")
        self.cursor.execute(self.attack_per_protocol_per_day % (self.from_date, self.to_date))
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__protocol_per_day_tab_name)
        worksheet.write('A1', 'protocol', self.bold)
        worksheet.write('B1', 'month', self.bold)
        worksheet.write('C1', 'day', self.bold)
        worksheet.write('D1', 'count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            if int(self.ensure_unicode(row[1])) <10:
                worksheet.write(i, 1,'0'+ str(self.ensure_unicode(row[1])))
            else:
                worksheet.write(i, 1, str(self.ensure_unicode(row[1])))
            if int(self.ensure_unicode(row[2])) <10:
                worksheet.write(i, 2, '0'+ str(self.ensure_unicode(row[2])))
            else:
                worksheet.write(i, 2, str(self.ensure_unicode(row[2])))
            worksheet.write(i, 3, self.ensure_unicode(row[3]))

    def top_attacker_per_day(self):
        logger.info(self.line)
        logger.info("Top Attacker per Day Report Generation")
        sql = ""
        count = 0
        for x in self.top_attacker_list:
            count += 1
            if len(self.top_attacker_list) <= count:
                sql = sql + "'" + x + "'"
            else:
                sql = sql + "'" + x + "',"
        print('sql is >>>>>>>>', str(sql),self.to_date,self.from_date,sql)
        query = self.top_attacker_per_day_query %(sql,self.from_date, self.to_date)
        # query = self.top_attacker_per_day_query % (sql, self.from_date, '1549526400.0')
        self.cursor.execute(query)
        per_attacker_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__top_attacker_per_day_tab_name)
        worksheet.write('A1', 'ip', self.bold)
        worksheet.write('B1', 'month', self.bold)
        worksheet.write('C1', 'day', self.bold)
        worksheet.write('D1', 'count', self.bold)
        i = 0
        for row in per_attacker_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            if int(self.ensure_unicode(row[1])) <10:
                worksheet.write(i, 1,'0'+ str(self.ensure_unicode(row[1])))
            else:
                worksheet.write(i, 1, str(self.ensure_unicode(row[1])))
            if int(self.ensure_unicode(row[2])) <10:
                worksheet.write(i, 2, '0'+ str(self.ensure_unicode(row[2])))
            else:
                worksheet.write(i, 2, str(self.ensure_unicode(row[2])))
            worksheet.write(i, 3, str(self.ensure_unicode(row[3])))

    def interface_report(self):
        logger.info(self.line)
        logger.info("Interface Count Report Generation")
        self.cursor.execute(self.interface_count_query % (self.from_date, self.to_date))
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__interface_count)
        worksheet.write('A1', 'Interface', self.bold)
        worksheet.write('B1', 'Count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))

    def interface_protocol_report(self):
        logger.info(self.line)
        logger.info("Interface Protocol Count Report Generation")
        self.cursor.execute(self.interface_protocol_count_query % (self.from_date, self.to_date))
        per_protocol_result = self.cursor.fetchall()
        worksheet = self.workbook.add_worksheet(self.__interface_protocol_count)
        worksheet.write('A1', 'Interface', self.bold)
        worksheet.write('B1', 'Protocol', self.bold)
        worksheet.write('C1', 'Count', self.bold)
        i = 0
        for row in per_protocol_result:
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(row[0]))
            worksheet.write(i, 1, self.ensure_unicode(row[1]))
            worksheet.write(i, 2, self.ensure_unicode(row[2]))

    def attackers_state(self):
        logger.info(self.line)
        logger.info("Attacker State Report Generation")
        worksheet = self.workbook.add_worksheet(self.__attacker_info)
        worksheet.write('A1', 'ip', self.bold)
        worksheet.write('B1', 'Saba lab', self.bold)
        worksheet.write('C1', 'Abusedb lab', self.bold)
        worksheet.write('D1', 'BlockServers lab', self.bold)
        query = self.attackers_state_query % (self.from_date, self.to_date)
        self.cursor.execute(query)
        result = self.cursor.fetchall()

        i = 0
        for ip in result:

            logger.critical("get Info For : " + str(ip[0]))
            i = i + 1
            worksheet.write(i, 0, self.ensure_unicode(ip[0]))
            if self.find_in_lab_db(ip[0]):
                worksheet.write(i, 1, "1")
            else:
                worksheet.write(i, 1, "0")
            try:
                if self.find_over_internet_abusedb(ip[0]):
                    worksheet.write(i, 2, "1")
                else:
                    worksheet.write(i, 2, "0")
            except:
                worksheet.write(i, 2, "0")
            try:
                blocked_ip = self.find_over_internet_blockservers_lab(ip[0])
            except:
                blocked_ip = None
            if blocked_ip is None:
                worksheet.write(i, 3, "0")
            else:
                worksheet.write(i, 3, blocked_ip['blockedservers']['blocked_count'])

    def find_in_lab_db(self, ip):
        query = "select * from attackers where ip='%s'" % str(ip)
        self.lab_cursor.execute(query)
        result = self.lab_cursor.fetchone()
        try:
            for x in result:
                pass
            return True
        except:
            return False

    def find_over_internet_abusedb(self, ip):
        import abusedb_lab
        site_checker = abusedb_lab.parse_page(ip=ip)

        if site_checker['abusedb']['found']== 0:
            return False
        else:
            return True

    def find_over_internet_blockservers_lab(self, ip):
        import blockedservers_lab
        site_checker = blockedservers_lab.parse_page(ip=ip)
        print ('inthe blockserver >>>>>>>>>>', site_checker)
        return site_checker

    def country_fix(self):
        logger.info(self.line)
        logger.info("Fixing Country Data")
        self.cursor.execute(self.attackers_query)
        result = self.cursor.fetchall()
        country=open('country.txt','w+')
        self.count = 0
        for x in result:
            try:
                # ip_info = self.gi.record_by_name(x[1])
                ip_info = self.gi.city(x[0])
                print (x[0]+"  -> "+ip_info.country.name)
                country_name = ip_info.country.name
                self.count = self.count+1

                # country_name = ip_info['country_name'].replace("'", "")
                # city_name = ip_info['city'] or None
                query = self.update_query % (country_name, x[0])
                logger.critical(query)
                try:
                    self.cursor.execute(query)
                    self.db.commit()
                except Exception as e:
                    pass
            except Exception as e:
                # ip = x[1]
                # logger.info( ip,str(e)
                country.write(x[0]+'\n')
                # print (e)

    def isp_fix(self):
        pass

    def get_country_name(self, ip):
        access_token = '40ccd88f2e219a'
        handler =ipinfo.getHandler(access_token)
        detailes= handler.getDetails(ip)
        country= detailes.country_name

    def run(self):
        try:
            self.country_fix()
            self.per_protocol()
            self.each_protocols()
            self.each_area()
            self.top_between_interface()
            self.smtp_server()
            self.top_attacker()
            self.top_country()
            self.Attack_time_group()
            self.per_day()
            self.top_authentication()
            self.top_country_protocol()
            self.top_Iranian_attacker()
            self.top_Iranian_attacker_protocol()
            self.interface_report()
            self.interface_protocol_report()
            self.top_attacker_per_day()
            self.per_protocol_day()
            self.brute_force_detection()
            self.bot_detection_function()
            self.port_scan_detection()
            self.attackers_state()
            self.close()
        except KeyboardInterrupt as e:
            self.close()


    def close(self):
        self.workbook.close()


if __name__ == '__main__':
    from_date = ""
    to_date = "2019-05-16_00:00:00"
    filename = "Naft_report_" + str(datetime.datetime.now())
    analyzer = report_generator(from_date=from_date,
                                to_date=to_date,
                                file_name=filename)
    analyzer.run()

#> select * from (select country, count(*) from connections inner join attackers on connections.attacker_id= attackers.id  where connections.attack_time > 1553126400 and connections.attack_time < 1553472000 group by country) as T where country like Iran;


