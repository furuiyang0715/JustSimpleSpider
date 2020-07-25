import sys
import os
import time
import atexit
import logging

from signal import SIGTERM

# from log_write import LoggerWriter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Daemon(object):
    """Class to demonize the application

    Args:
        pidfile (str): path for the pidfile
        stdin (Optional[str]): path to stdin. Default to /dev/null
        stdout (Optional[str]): path to stdout. Default to /dev/null
        stderr (Optional[str]): path to stderr. Default to /dev/null
        log_err (Optional[object]): :class:`.LoggerWriter` object. Default to None

    """
    def __init__(self,
                 pidfile,
                 stdin='/dev/null',
                 stdout='/dev/null',
                 stderr='/dev/null',
                 log_err=None,
                 ):
        # 记录进程号的文件
        self.pidfile = pidfile
        # 表示这个守护进程的标准输入\输出\错误流
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        if log_err is not None:
            self.log_err = log_err
        # 在正常启动前 用于显示信息
        self.logger = logger
        self.modules = dict()

    def daemonize(self):
        """Deamonize, do double-fork magic.
        """
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent.
                self.logger.info("Done first fork")
                sys.exit(0)
        except OSError as e:
            message = "Fork #1 failed: {}\n".format(e)
            self.logger.error(message)
            sys.stderr.write(message)
            sys.exit(1)

        # Decouple from parent environment.
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do second fork.
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent.
                self.logger.info("Done second fork")
                sys.exit(0)
        except OSError as e:
            message = "Fork #2 failed: {}\n".format(e)
            self.logger.error(message)
            sys.stderr.write(message)
            sys.exit(1)

        self.logger.info('deamon going to background, PID: {}'.format(os.getpid()))

        # Redirect standard file descriptors.
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Write pidfile.
        pid = str(os.getpid())
        self.logger.info(f"-----------------> {pid}")
        self.logger.info(self.pidfile)
        open(self.pidfile, 'w+').write("{}\n".format(pid))
        self.logger.info(f"-----------------> {pid}")

        # Register a function to clean up.
        # 用于注册程序退出时间的回调函数
        atexit.register(self.delpid)

    def delpid(self):
        """Delete pid file created by the daemon

        """
        os.remove(self.pidfile)

    def start(self):
        """Start daemon.
        """
        pids = None
        # Check pidfile to see if the daemon already runs.
        try:
            with open(self.pidfile) as f:
                pids = f.readlines()
        except IOError:
            pid = None

        self.logger.info(pids)
        if pids:
            message = "Pidfile {} already exist. Daemon already running?\n".format(self.pidfile)
            self.logger.error(message)
            sys.stderr.write(message)
            sys.exit(1)

        # Start daemon.
        self.daemonize()

        self.logger.info("Demonized. Start run")
        # 继承该类的守护进程真正完成的任务
        self.run()

    def status(self):
        """Get status of daemon.
        """
        try:
            with open(self.pidfile) as f:
                pids = f.readlines()
        except IOError:
            message = "There is not PID file. Daemon is not running\n"
            sys.stderr.write(message)
            sys.exit(1)

        for pid in pids:
            pid = pid.strip()
            sys.stdout.write(f'{pids}')
            self.logger.info(f'{pids}')
            # 此处是 Linux 上的状态信息 MacOS 上的与此有区别
            try:
                procfile = open("/proc/{}/status".format(pid), 'r')
                procfile.close()
                message = "There is a process with the PID {}\n".format(pid)
                sys.stdout.write(message)
            except IOError:
                message = "There is not a process with the PID {}\n".format(self.pidfile)
                sys.stdout.write(message)

    def stop(self):
        """Stop the daemon.
        """
        # Get the pid from pidfile.
        try:
            with open(self.pidfile) as f:
                pids = f.readlines()
        except IOError as e:
            message = str(e) + "\nDaemon not running?\n"
            sys.stderr.write(message)
            self.logger.error(message)
            sys.exit(1)

        for pid in pids:
            # Try killing daemon process.
            try:
                logging.info('Trying to kill pid: '+pid.strip())
                os.kill(int(pid.strip()), SIGTERM)
                self.logger.info('Killed pid: '+pid.strip())
                time.sleep(1)
            except OSError as e:
                self.logger.error('Cannot kill process with pid: '+pid.strip())
                self.logger.error(str(e))
            # sys.exit(1)

        try:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
        except IOError as e:
            message = str(e) + "\nCan not remove pid file {}".format(self.pidfile)
            sys.stderr.write(message)
            self.logger.error(message)
            sys.exit(1)

    def restart(self):
        """Restart daemon.
        """
        self.stop()
        time.sleep(1)
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by start() or restart().

        Example:

        class MyDaemon(Daemon):
            def run(self):
                while True:
                    time.sleep(1)
        """


# class MyTestDaemon(Daemon):
#     def run(self):
#         sys.stdout.write(str(int(sys.stdout is self.stdout)))
#         print("hello")
#         print(sys.stdout is self.stdout)
#         print(sys.stdout is self.stdout)
#
#         sys.stdout.write('Daemon started with pid {}\n'.format(os.getpid()))
#         while True:
#             sys.stdout.write('Daemon Alive! {}\n'.format(time.ctime()))
#             sys.stdout.flush()
#             time.sleep(5)

