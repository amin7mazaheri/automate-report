import os
import sys
# from string import lower

import MySQLdb as mysql
import xlsxwriter as xlsxwriter
import datetime

limit = 10000
fromdate = 1549267200
# todate = 1554595200

keyboard = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.']
]
shift_keyboard = [
    ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>']
]

shift_key = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '=', '_', '+', '~', '{', '}', '[', ']', '|']
similar_char = {"5": "s", "o": "0", "$": "s"}

db = mysql.connect("localhost", "amin", "amin")
cursor = db.cursor()

workbook = xlsxwriter.Workbook("Naft_authentications_report_03_08.xlsx")
bold = workbook.add_format({'bold': True, 'bg_color': 'green'})
worksheet = workbook.add_worksheet("password_analyzer")
worksheet.write('A1', 'password', bold)
worksheet.write('B1', 'hit rate', bold)
worksheet.write('C1', 'difficulty', bold)
worksheet.write('D1', 'similarity', bold)
worksheet.write('E1', 'strong', bold)
worksheet.write('F1', 'attacker Count', bold)
worksheet.write('G1', 'Username Count', bold)
count = 1


def compareTwoChar(a, b):
    log("*****************************************")
    log("comparing : " + str(a) + " & " + str(b))
    log(len(keyboard))
    if len(a) * len(b) != 1:
        return False
    if a != b:
        for key_index, x in enumerate(keyboard):
            if a in x:
                for index, y in enumerate(x):
                    if a != y:
                        continue
                    else:
                        log(a + "found in " + str(x))
                        try:
                            log("key_index is : " + str(key_index) + " -> index is : " + str(index + 1))
                            if b == fetch(key_index, index + 1) and index + 1 < len(x):
                                return True
                            log("key_index is : " + str(key_index) + " -> index is : " + str(index - 1))
                            if b == fetch(key_index, index - 1) and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(index + 1))
                            if b == fetch(key_index - 1, index + 1) and key_index - 1 >= 0 and index + 1 < len(x):
                                return True
                            log("key_index is : " + str(key_index) - 1 + " -> index is : " + str(index))
                            if b == fetch(key_index - 1, index) and key_index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(index - 1))
                            if b == fetch(key_index - 1, index - 1) and key_index - 1 >= 0 and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(index + 1))
                            if b == fetch(key_index + 1, index + 1) and index + 1 < len(x) and key_index + 1 < len(
                                    keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(index))
                            if b == fetch(key_index + 1, index) and key_index + 1 < len(keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(index - 1))
                            if b == fetch(key_index + 1, index - 1) and key_index + 1 < len(
                                    keyboard) and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + index + str(
                                " shift is on"))
                            if b == fetch(key_index, index + 1 + True) and index + 1 < len(x):
                                return True
                            log("key_index is : " + str(key_index) + " -> index is : " + str(
                                index - 1) + " shift is on")
                            if b == fetch(key_index, index - 1 + True) and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index + 1) + " shift is on")
                            if b == fetch(key_index - 1, index + 1 + True) and key_index - 1 >= 0 and index + 1 < len(
                                    x):
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(
                                index) + " shift is on")
                            if b == fetch(key_index - 1, index + True) and key_index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(
                                index - 1) + " shift is on")
                            if b == fetch(key_index - 1, index - 1 + True) and key_index - 1 >= 0 and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index + 1) + " shift is on")
                            if b == fetch(key_index + 1, index + 1 + True) and index + 1 < len(
                                    x) and key_index + 1 < len(
                                keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index) + " shift is on")
                            if b == fetch(key_index + 1, index + True) and key_index + 1 < len(keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index - 1) + " shift is on")
                            if b == fetch(key_index + 1, index - 1 + True) and key_index + 1 < len(
                                    keyboard) and index - 1 >= 0:
                                return True
                        except IndexError as e:
                            return False
                        except Exception as e:
                            log("+++++++++++++++++++++++++++++++++++++++++++++")
                            log("++++++++++++++++++,exception+++++++++++++++++")
                            log("+++++++++++++++++++++++++++++++++++++++++++++")
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            log("a is : " + a)
                            log("keyboard lenght is : " + str(len(keyboard)))
                            log("key_index is : " + str(key_index))
                            log("index is : " + str(index))
                            log(exc_type)
                            log(fname)
                            log(exc_tb.tb_lineno)
                            log("+++++++++++++++++++++++++++++++++++++++++++++")
                            return False
                        break
        for key_index, x in enumerate(shift_keyboard):
            if a in x:
                for index, y in enumerate(x):
                    if a != y:
                        continue
                    else:
                        log(a + "found in " + str(x))
                        try:
                            log("key_index is : " + str(key_index) + " -> index is : " + str(index + 1))
                            if b == fetch(key_index, index + 1) and index + 1 < len(x):
                                return True
                            log("key_index is : " + str(key_index) + " -> index is : " + str(index - 1))
                            if b == fetch(key_index, index - 1) and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(index + 1))
                            if b == fetch(key_index - 1, index + 1) and key_index - 1 >= 0 and index + 1 < len(x):
                                return True
                            log("key_index is : " + str(key_index) - 1 + " -> index is : " + str(index))
                            if b == fetch(key_index - 1, index) and key_index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(index - 1))
                            if b == fetch(key_index - 1, index - 1) and key_index - 1 >= 0 and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(index + 1))
                            if b == fetch(key_index + 1, index + 1) and index + 1 < len(x) and key_index + 1 < len(
                                    keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(index))
                            if b == fetch(key_index + 1, index) and key_index + 1 < len(keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(index - 1))
                            if b == fetch(key_index + 1, index - 1) and key_index + 1 < len(
                                    keyboard) and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + index + str(
                                " shift is on"))
                            if b == fetch(key_index, index + 1 + True) and index + 1 < len(x):
                                return True
                            log("key_index is : " + str(key_index) + " -> index is : " + str(
                                index - 1) + " shift is on")
                            if b == fetch(key_index, index - 1 + True) and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index + 1) + " shift is on")
                            if b == fetch(key_index - 1, index + 1 + True) and key_index - 1 >= 0 and index + 1 < len(
                                    x):
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(
                                index) + " shift is on")
                            if b == fetch(key_index - 1, index + True) and key_index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index - 1) + " -> index is : " + str(
                                index - 1) + " shift is on")
                            if b == fetch(key_index - 1, index - 1 + True) and key_index - 1 >= 0 and index - 1 >= 0:
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index + 1) + " shift is on")
                            if b == fetch(key_index + 1, index + 1 + True) and index + 1 < len(
                                    x) and key_index + 1 < len(
                                keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index) + " shift is on")
                            if b == fetch(key_index + 1, index + True) and key_index + 1 < len(keyboard):
                                return True
                            log("key_index is : " + str(key_index + 1) + " -> index is : " + str(
                                index - 1) + " shift is on")
                            if b == fetch(key_index + 1, index - 1 + True) and key_index + 1 < len(
                                    keyboard) and index - 1 >= 0:
                                return True
                        except IndexError as e:
                            return False
                        except Exception as e:
                            log("+++++++++++++++++++++++++++++++++++++++++++++")
                            log("++++++++++++++++++,exception+++++++++++++++++")
                            log("+++++++++++++++++++++++++++++++++++++++++++++")
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            log("a is : " + a)
                            log("keyboard lenght is : " + str(len(keyboard)))
                            log("key_index is : " + str(key_index))
                            log("index is : " + str(index))
                            log(exc_type)
                            log(fname)
                            log(exc_tb.tb_lineno)
                            log("+++++++++++++++++++++++++++++++++++++++++++++")
                            return False
                        break
        return False
    else:
        return True


def fetch(key_index, index, shift=False):
    if shift:
        return shift_keyboard[key_index][index]
    return keyboard[key_index][index]


def difficulllty(pass_word):
    last_compare_result = []
    count_true = 0
    count_false = 0
    for index, x in enumerate(pass_word):
        print (' in the  loop the index and x is ::::::', index , "      x is: ",x)
        log("index : " + str(index) + "-" + x)
        if index + 1 < len(pass_word):
            log("Going to compare : " + x + " -> " + pass_word[index + 1])
            result = compareTwoChar(x, pass_word[index + 1])
            last_compare_result.append(result)
        else:
            continue
    for x in last_compare_result:

        if x:
            count_true += 1
        else:
            count_false += 1
    return count_true, count_false


def username_count(password):
    global todate
    global fromdate
    global limit
    print ('in the user name count',datetime.datetime.now() )
    query = "select honeypot.authentications.username,count(*) as cnt from honeypot.authentications where" \
            " honeypot.authentications.password " \
            "is not null and  honeypot.authentications.password ='{password}' and" \
            " honeypot.authentications.attack_time >= '{from_date}'" \
            "group by " \
            "honeypot.authentications.username order by cnt desc;".format(password=password, from_date =fromdate)
    print (query)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except:
        return 0
    return cursor.rowcount


# def attacker_count(password):
#     print ('in the attacker count //////////////////////////')
#     global limit
#     query = "select count(*) as cnt from honeypot.authentications where " \
#             "honeypot.authentications.password is not null and honeypot.authentications.password='{password}' group by " \
#             "honeypot.authentications.attacker_id ".format(password=password)
#     try:
#         cursor.execute(query)
#         result = cursor.fetchall()
#     except:
#         return 0
#     print ('in the end of the attacker count/////////////////////')
#     return cursor.rowcount


def similarity(password):
    query = "select count(*) from defaults.`default-passwords` where password='{password}'".format(password=password)
    try:
        cursor.execute(query)
        result = cursor.fetchone()
    except:
        return 0
    (count,) = result
    return count


def is_stronge(password):

    if password == password.lower():
        return False
    if password == password.upper():
        return False
    else:
        sign_result = False
        digit_result = False
        for x in password:
            if x in shift_key:
                sign_result = True
        for x in password:
            try:
                int(x)
                digit_result = True
            except:
                pass
        return sign_result & digit_result


def run():
    global limit
    global fromdate
    # global todate
    query = "select honeypot.authentications.password,count(*) as cnt from honeypot.authentications where " \
            " password is not null and honeypot.authentications.attack_time >= '{from_date}' " \
            " group by honeypot.authentications.password"  \
            " order by cnt desc limit {limit};".format(limit=limit, from_date = fromdate)

    cursor.execute(query)
    result = cursor.fetchall()
    dict_password_count={}
    dict_username_count={}
    for x in result :
        dict_password_count[str(x[0])]= x[1]
        dict_username_count[str(x[0])] = username_count(x[0])

    for password in result:
        try:
            pass_word = password[0]

            pass_len = len(str(pass_word))
            if pass_len == 0:
                continue
            hit_rate = password[1]

            diff_true_count, diff_false_count = difficulllty(pass_word)
            user_count = dict_username_count[pass_word]

            attackers_count = dict_password_count[pass_word]
            isstrong = is_stronge(pass_word)
            similarity_count = similarity(pass_word)
            print ("---------------------------------------")
            print (pass_word)
            # print hit_rate
            # print diff_true_count
            # print diff_false_count
            # print user_count
            # print attackers_count
            # print isstrong
            # print similarity_count
            write(pass_word, hit_rate, diff_true_count, similarity_count, isstrong, attackers_count,user_count)
        except Exception as e:
            print (str(e))

    close()


def write(password, hitrate, difficulty, similarity, strong, attacker_count,username_count):
    global count
    try:
        worksheet.write(count, 0, ensure_unicode(password))
        worksheet.write(count, 1, ensure_unicode(hitrate))
        worksheet.write(count, 2, ensure_unicode(difficulty))
        worksheet.write(count, 3, ensure_unicode(similarity))
        worksheet.write(count, 4, ensure_unicode(strong))
        worksheet.write(count, 5, ensure_unicode(attacker_count))
        worksheet.write(count, 6, ensure_unicode(username_count))
    except Exception as e:
        print (str(e))
    count += 1


def ensure_unicode(v):
    if isinstance(v, str):
        try:
            v = v
            v = v.decode('utf8')
        except UnicodeDecodeError as e:
            v = v
            v = v.decode('latin-1')
    return v


def close():
        workbook.close()



def log(msg):
    pass
    # print msg


if __name__ == '__main__':
    run()
