import                 os, sys
import                 inspect
import                 coosbay
import                 json
import                 logging
from   datetime import datetime
import                 subprocess


class coosbayLogger(object) :
  def __init__(self, logger_name   = 'srvrAlert',
                     log_level     = 'DEBUG',
                     log_dir       = None,
                     logfile_name  = None,
                     MaxLogFileSizeInBytes   = int(5*10**6),
                     MaxNumberOfLogsToRetain = 200
               ) :
      '''
      logger_name : could be used in the message format, if more than 1
                    application used this same log file
      log_level   : handlers will be initialized to this logging level 
      log_dir     : the directory into which the log files will be written.
                    default: ...coosbay/logs/directory_name-of-application.
                    if specified, that exact path will be used
      logfile_name: the name of the logile.
                    default: log_dir/directory_name-of-application.log

      Examples.  Assume application resides in directory snafu
        coosbayLogger()  will write the logs in .../coosbay/logs/snafu/snafu.log

        coosbayLogger(logfile_name='George') will write logs to 
        .../coosbay/logs/snafu/George.log

        coosbayLogger(logfile_name='Prescott', log_dir='Samuel') will place
        logs in .../snafu/Samuel/Prescott.log

      coosbayLogger will exit if it cannot create log_dir or logfile.
      '''

      ##  The directory already exists
      FileExistsErrno         = 13
      ##  Rotating handler parameters
      #MaxLogFileSizeInBytes   = int(5*10**6)
      #MaxNumberOfLogsToRetain = 200
      #MaxLogFileSizeInBytes   = 5000
      #MaxNumberOfLogsToRetain =    3

      ##  Log levels
      self.log_levels = {
          'CRITICAL' : logging.CRITICAL,  #  50
          'ERROR'    : logging.ERROR   ,  #  40
          'WARNING'  : logging.WARNING ,  #  30
          'INFO'     : logging.INFO    ,  #  20
          'DEBUG'    : logging.DEBUG   ,  #  10
          'NOTSET'   : logging.NOTSET     #   0
          }

      self.logger_name = logger_name

      #logfile_name = os.path.split(os.path.realpath(__file__))[0]
      #self.logfile_name = os.path.split(logfile_name)[1]
      if logfile_name is None :
        self.logfile_base = os.path.split(os.getcwd())[1]
      else :
        self.logfile_base =  logfile_name
      print "LOGFILE_NAME 0", self.logfile_base

      if log_dir is None :
        log_dir = os.path.split(inspect.getfile(coosbay))[0]
        log_dir = os.path.join(log_dir, 'logs')
        self.log_dir = os.path.join(log_dir, self.logfile_base)
      else :
        self.log_dir = log_dir
      print "LOG_DIR", self.log_dir

      try : os.mkdir(self.log_dir, 0755)
      except OSError as ose :
        if ose.errno == FileExistsErrno : pass
      except Exception as ex :
        print "{} : {}".format(ex.filename, ex.strerror)
        print "Logger {} can't create log directory {}".format(
               self.logger_name, self.log_dir)
        print "Logger {} exiting".format(self.logger_name)
        sys.exit(1)

      self.logfile_name = self.logfile_base + ".log"
      print "LOGFILE_NAME", self.logfile_name

      self.full_log_name = os.path.join(self.log_dir, self.logfile_name)
      #logging.basicConfig(filename=logging.full_log_name, level=logging.DEBUG)
      print 'FULL-LOG-NAME', self.full_log_name

      self.logger        = logging.getLogger(self.logger_name)
      ## Simple file_handler
      #self.file_handler   = logging.FileHandler(self.full_log_name)
      ## Let's try the RotatingFileHandler:
      ## might be a little safer, because total disk usage is constrained
#class logging.handlers.RotatingFileHandler(filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0)
      self.file_handler  = logging.handlers.RotatingFileHandler(
                               self.full_log_name,
                               maxBytes    = MaxLogFileSizeInBytes,
                               backupCount = MaxNumberOfLogsToRetain)
## Another possibility is to rotate by time:
# class logging.handlers.TimedRotatingFileHandler(filename, when='h', interval=1,
#    backupCount=0, encoding=None, delay=False, utc=False)
# more convenient.

      self.file_handler.setLevel(self.set_log_level(log_level))
      self.file_formatter = logging.Formatter('%(levelname)s | %(message)s')
      #self.file_formatter = logging.Formatter('%(message)s')
      self.file_handler.setFormatter(self.file_formatter)
      self.logger.addHandler(self.file_handler)
      self.logger.setLevel(self.set_log_level(log_level))

      self.datapkt_l = [{'logger':self.logger_name + " Engaged"}]
      self.datapkt_l.append(self.df_h(self.datapkt_l[0]))
      msg = {'data' : self.datapkt_l, 'pkt': 'STATUS'}
      #msg = self.df_h(msg)
      self.info(msg)
  ## --------------------------------- ##

  def get_logger(self) :
      return self.logger
  ## --------------------------------- ##

  def set_log_level(self, level) :
      try :
        ## maybe log level-change
        self.logger.setLevel(self.log_levels[level])
        self.file_handler.setLevel(self.log_levels[level])
        return level
      except Exception :
        ## maybe log this error
        self.logger.setLevel(self.log_levels['DEBUG'])
        self.file_handler.setLevel(self.log_levels['DEBUG'])
        return 'DEBUG'
  ## --------------------------------- ##

  def fmt_msg_time(self) :
      return str(datetime.utcnow()).replace(' ', 'T')
  ## --------------------------------- ##

  def warn(self, message_d) :
      '''message_d : preformatted payload; just add ts and level_info
      '''
      self.std_issue(message_d)
      message_d['level'] = 'warn'
      msg = json.dumps(message_d)

      self.logger.warn(msg)
  ## --------------------------------- ##

  def info(self, message_d) :
      '''message_d : preformatted payload; just add ts and level_info
      '''
      self.std_issue(message_d)
      message_d['level'] = 'info'
      msg = json.dumps(message_d)

      self.logger.info(msg)
  ## --------------------------------- ##

  def debug(self, message_d) :
      '''message_d : preformatted payload; just add ts and level_info
      '''
      self.std_issue(message_d)
      message_d['level'] = 'debug'
      msg = json.dumps(message_d)

      self.logger.debug(msg)
  ## --------------------------------- ##

  def error(self, message_d) :
      '''message_d : list of dictionaries
      '''
      self.std_issue(message_d)
      message_d['level'] = 'error'
      msg = json.dumps(message_d)

      self.logger.error(msg)
  ## --------------------------------- ##

  def critical(self, message_d) :
      '''message_d : preformatted payload; just add ts and level_info
      '''
      self.std_issue(message_d)
      message_d['level'] = 'critical'
      msg = json.dumps(message_d)

      self.logger.critical(msg)
  ## --------------------------------- ##

  def df_h(self, message_d={}) :
      '''
      Capture output from the "df -h" command and add it to the
      pkt dict.
      '''
      dfh = subprocess.check_output(["df", "-h"])
      #message_d['df_h'] = json.dumps(dfh, sort_keys=True, indent=4, separators=(',', ': '))
      message_d['df_h'] = dfh
  ## --------------------------------- ##

  def std_issue(self, message_d) :
      '''
      Tack on any common items to the dict being logged
      '''
      ts = self.fmt_msg_time()
      message_d['ts'] = ts

