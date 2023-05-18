# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/utility/utility.py
# Compiled at: 2021-04-20 08:24:52
import logging, logging.handlers, json, decimal, traceback, MySQLdb, smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

class Logger:

    def __init__(self, appName, logFilename):
        LOG_FILENAME = logFilename
        self.logger = logging.getLogger(appName)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def __del__(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def info(self, message):
        self.logger.info(message)

    def exception(self, ex):
        self.logger.exception(ex)


class DecimalEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class DSTMailer:

    def __init__(self, mageConf, dstConf, mailConf):
        if dstConf['dbEngine'] == 'mssql':
            self.dstDbEngine = __import__('pymssql')
        else:
            self.dstDbEngine = MySQLdb
        if 'logFileName' not in mageConf or mageConf['logFileName'] == '':
            now = datetime.now()
            today = '%s-%s-%s' % (now.year, now.month, now.day)
            updatedAt = '%s-%s-%s %s:%s:%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
            logFileName = 'log/magento_dst_sync_' + updatedAt + '.' + 'log'
            mageConf['logFileName'] = logFileName
        self.logger = Logger('Mail', mageConf['logFileName'])
        self.mageConf = mageConf
        self.dstConf = dstConf
        self.mailConf = mailConf
        self.projectName = mageConf['projectName']
        self.mailHost = mailConf['host']
        self.mailFrom = mailConf['mail_from']
        self.mailTo = mailConf['mail_to']
        self.getErrorLogSQL = "\n            SELECT *\n            FROM {dstTableName}\n            WHERE sync_status = 'F'\n            AND TIMESTAMPDIFF(MINUTE,sync_dt,now()) <= %s\n        "
        self.openDstDb()

    def __del__(self):
        self.closeDstDb()

    def openDstDb(self, connection=None):
        if connection and connection.open:
            self.dstConn = connection
        else:
            try:
                self.dstConn = self.dstDbEngine.connect(self.dstConf['host'], self.dstConf['user'], self.dstConf['password'], self.dstConf['db'], charset='utf8')
                self.logger.info('Open DST database connection')
            except Exception as e:
                log = ('Failed to connect to DST Database with error: {0}').format(str(e))
                self.logger.exception(log)
                raise

        self.dstCursor = self.dstConn.cursor()
        if self.dstDbEngine == MySQLdb:
            self.dstCursor.execute('SET NAMES utf8')

    def closeDstDb(self):
        self.dstConn.close()
        self.logger.info('Disconnect from DST Database')

    def getErrorLogs(self, dstTableName, duration):
        self.getErrorLogSQL = self.getErrorLogSQL.format(dstTableName=dstTableName)
        self.dstCursor.execute(self.getErrorLogSQL, [duration])
        columns = tuple([ d[0].decode('utf8') for d in self.dstCursor.description ])
        errorLogs = [columns]
        for row in self.dstCursor:
            errorLogs.append(row)

        return errorLogs

    def sendErrorLogMail(self, processName, dstTableName, duration=None):
        if duration is None:
            if processName in self.mailConf['processDuration']:
                duration = self.mailConf['processDuration'][processName]
            else:
                duration = -1
        errorLogs = self.getErrorLogs(dstTableName, duration)
        if len(errorLogs) > 1:
            errorLogsStr = ('\r\n').join([ (',').join([ str(x) for x in list(row) ]) for row in errorLogs ])
            subject = ('[{0}]Error logs for process: {1}').format(self.projectName, processName)
            content = subject
            try:
                msg = MIMEText(content, _subtype='html', _charset='utf-8')
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = self.mailFrom
                msg['To'] = (',').join(self.mailTo)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(errorLogsStr)
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % 'error_details.txt')
                msg.attach(part)
                msg.attach(MIMEText(content))
                s = smtplib.SMTP()
                s.connect(self.mailHost)
                if 'user' in self.mailConf and self.mailConf['user'] != '':
                    s.login(self.mailConf['user'], self.mailConf['password'])
                s.sendmail(self.mailFrom, self.mailTo, msg.as_string())
                s.close()
                mailLog = ('Mail sent successfully to {0}').format(self.mailTo)
                self.logger.info(mailLog)
                return True
            except Exception as e:
                mailLog = ('Mail failed to send to {0} with error: {1}').format(self.mailTo, traceback.format_exc())
                self.logger.info(mailLog)
                return False

        else:
            mailLog = ('No errors happenen for {0} at last {1} minutes').format(processName, duration)
            self.logger.info(mailLog)
        return