# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.17 (default, Feb 27 2021, 15:10:58) 
# [GCC 7.5.0]
# Embedded file name: /opt/magedst/utility/DSTControl.py
# Compiled at: 2021-04-20 08:24:52
__author__ = 'sandy.tu'
import sys
from utility import Logger
import traceback
from datetime import datetime, timedelta
import json, csv

class DSTControl(object):

    def __init__(self, dstCursor=None):
        self.dstCursor = dstCursor
        self.defaultCutoffDt = '2015-01-01'
        self.queries = {'getLastCutOffDateSQL': "SELECT max(last_cutoff_dt) as last_cutoff_dt FROM sync_control WHERE task = %s and sync_status = 'O'", 'insertSyncControlSQL': '\n                INSERT INTO sync_control\n                (task,sync_status,last_cutoff_entity_id,last_cutoff_dt,last_start_dt,last_end_dt,sync_notes)\n                VALUES (%s,%s,%s,%s,%s,%s,%s)\n            ', 
           'getLastCutOffEntityIdSQL': '\n                SELECT last_cutoff_entity_id\n                FROM sync_control\n                WHERE task = %s AND\n                last_cutoff_dt = %s\n            '}
        self.timezoneDiff = 0

    def getNowStr(self):
        now = datetime.now()
        nowstr = now.strftime('%Y-%m-%d %H:%M:%S')
        return nowstr

    def convertTimezone(self, time, timezoneDiff=None):
        if time is None:
            return time
        else:
            if time == '':
                return time
            else:
                if timezoneDiff is None:
                    if self.timezoneDiff is None:
                        timezoneDiff = 0
                    else:
                        timezoneDiff = self.timezoneDiff
                adjTime = time - timedelta(hours=timezoneDiff)
                return adjTime

            return

    def getTaskLastCutoffDate(self, task):
        self.dstCursor.execute(self.queries['getLastCutOffDateSQL'], [task])
        res = self.dstCursor.fetchone()
        lastCutoffDt = None
        if type(res) == dict:
            lastCutoffDt = res['last_cutoff_dt']
        else:
            lastCutoffDt = res[0]
        if lastCutoffDt is not None:
            if self.timezoneDiff is not None and self.timezoneDiff != 0:
                adjLastCutoffDt = lastCutoffDt + timedelta(hours=self.timezoneDiff)
                lastCutoffDt = str(adjLastCutoffDt)
        else:
            lastCutoffDt = self.defaultCutoffDt
        return lastCutoffDt

    def insertSyncControl(self, task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes):
        self.dstCursor.execute(self.queries['insertSyncControlSQL'], [
         task, syncStatus, lastCutoffEntityId, lastCutoffDt, lastStartDt, lastEndDt, syncNotes])

    def getTaskLastCutOffEntityId(self, task, lastCutoffDt=None):
        if lastCutoffDt is None:
            lastCutoffDt = self.getTaskLastCutoffDate(task)
        self.dstCursor.execute(self.queries['getLastCutOffEntityIdSQL'], [task, lastCutoffDt])
        res = self.dstCursor.fetchone()
        lastCutoffEntityId = 0
        if res is not None and len(res) > 0:
            lastCutoffEntityId = int(res['last_cutoff_entity_id'])
        return lastCutoffEntityId