"""
Based on Schedule library by Dan Bader (https://github.com/dbader/schedule)
Python job scheduling for humans.
An in-process scheduler for periodic jobs that uses the builder pattern
for configuration. Schedule lets you run Python functions (or any other
callable) periodically at pre-determined intervals using a simple,
human-friendly syntax.
Usage:

>>> import scheduler
>>> schedule = Schedule()
>>> def print_msg(message = 'stuff'):
>>>     print("I'm working on:", message)
>>> schedule.every(tag = 'job1', unit = 'day', at_time = '22:05',
                   job_func = print_msg, message = 'things')
>>> schedule.every(tag = 'job2', interval = 5, unit = 'sec',
                   job_func = print_msg)
>>> schedule.every(tag = 'job3', start_day = 'mon', at_time = '12:58',
                   job = print_msg)
>>> schedule.every(tag = 'job4', interval = 5, unit = 'min',
                   job_func = print_msg)
>>> schedule.every(tag = 'job5', unit = 'hour', at_time = '00:38',
                   job_func = print_msg)

Schedule of existing job can be updated without supplying new job_func

>>> schedule.every(tag = 'job1', unit = 'hour', at_time = '00:21')

Output:
schedule.every returns True/False, if correctly/incorrectly configured
"""

import utils  # to get function providing CET time
import utime
import functools

class Schedule():

    def __init__(self):
        self.jobs = {}

    def __iter__(self):
        self.job_tags = list(self.jobs.keys())
        return self

    def __next__(self):
        if len(self.job_tags) >= 1:
            return self.job_tags.pop()
        else:
            raise StopIteration

    def every(self, tag = None, interval = 1, unit = None, start_day = None,
              at_time = None, job_func = None, *args, **kwargs):
        """Schedule a new periodic job. If tag already in dictionary,
           scheduling is updated, but original job_func kept"""

        job = { 'interval' : 1,
                'unit'     : None,
                'at_time'  : None,
                'last_run' : None,
                'next_run' : None,
                'period'   : None,
                'start_day': None,
                'active'   : True }

        if interval > 0:
            job['interval'] = int(interval)
        else:
            return False

        if unit in ('sec', 'min', 'hour'):
            job['unit'] = unit
        elif unit in ('day', 'week'):
            if interval != 1:
                return False
            job['unit'] = unit
        elif unit != None:
            return False

        if start_day in ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'):
            if interval != 1:
                return False
            job['start_day'] = start_day
            job['unit'] = 'week'
        elif job['unit'] == None:
            return False

        if at_time:
            if (job['unit'] in ('hour', 'day') or job['start_day']):
                hour, minute = [t for t in at_time.split(':')]
                minute = int(minute)
                if job['unit'] == 'day' or job['start_day']:
                   hour = int(hour)
                   if hour < 0 or hour > 23:
                       return False
                elif job['unit'] == 'hour':
                   hour = 0
                if minute < 0 or minute >59:
                    return False
                job['at_time'] = [hour, minute]
            else:
                return False

        if tag in self.jobs:
            self.jobs[tag].update(job)
        else:
            try:
                job['job_func'] = functools.partial(job_func, *args, **kwargs)
                self.jobs[tag] = job
            except:
                return False
        self._schedule_next_run(tag)
        return True

    def toggle(self, tag, active = None):
        """toggle active state of particular job. State can be set explicitely
           by setting the argument active to True/False. Returns state of job
           as bool"""
        if active == None:
            self.jobs[tag]['active'] = not self.jobs[tag]['active']
            if self.jobs[tag]['active']:
                self._schedule_next_run(tag)
            return self.jobs[tag]['active']
        else:
            if active and not self.jobs[tag]['active']:
                self._schedule_next_run(tag)
            self.jobs[tag]['active'] = bool(active)
            return bool(active)

    def cancel(self, tag):
        return True if self.jobs.pop(tag, False) else False

    def run(self, tag):
        """Run the job and immediately reschedule it."""
        ret = self.jobs[tag]['job_func']()
        self.jobs[tag]['last_run'] = self._now()
        self._schedule_next_run(tag)
        return ret

    def run_pending(self):
        """Run all jobs that are scheduled to run and are in an active state
        Please note that it is *intended behavior that tick() does not
        run missed jobs*. For example, if you've registered a job that
        should run every minute and you only call tick() in one hour
        increments then your job won't be run 60 times in between but
        only once.
        """
        runnable_tags = ((tag, self.jobs[tag]['next_run']) for tag in self.jobs
                          if self.should_run(tag))
        for tag, next_run in sorted(runnable_tags, key = lambda x : x[1]):
            self.run(tag)

    def should_run(self, tag):
        """True if the job identified by tag should run now"""
        return ((self._now() >= self.jobs[tag]['next_run']) and
                self.jobs[tag]['active'])

    def _now(self):
        """ current time in sec based on CET"""
        return int(utils.cettime(in_sec = True))

    def _schedule_next_run(self, tag):
        """Compute the instant when this job should run next."""
        f = 1
        if self.jobs[tag]['unit'] == 'min':
            f = 60
        elif self.jobs[tag]['unit'] == 'hour':
            f = 60 * 60
        elif self.jobs[tag]['unit'] == 'day':
            f = 60 * 60 * 24
        elif self.jobs[tag]['unit'] == 'week':
            f = 60 * 60 * 24 * 7
        self.jobs[tag]['period'] = f * self.jobs[tag]['interval']
        self.jobs[tag]['next_run'] = self._now()

        if self.jobs[tag]['at_time'] is not None:
            tm = list(utime.localtime(self.jobs[tag]['next_run']))
            # Check if the target time may is passed for today
            passed_today = (self.jobs[tag]['period'] > 60 * 60 * 24)
            passed_today = passed_today or(
                (self.jobs[tag]['unit'] == 'day') and
                (tm[3] > self.jobs[tag]['at_time'][0]) or (
                    tm[3] == self.jobs[tag]['at_time'][0] and tm[4] >=
                    self.jobs[tag]['at_time'][1]))
            passed_today = passed_today or (
                (self.jobs[tag]['unit'] == 'hour') and
                (tm[4] >= self.jobs[tag]['at_time'][1]))

            # only force the target hour for days and weeks, not for hours
            if self.jobs[tag]['unit'] in ('day', 'week'):
                tm[3] = self.jobs[tag]['at_time'][0]
            tm[4] = self.jobs[tag]['at_time'][1]
            tm[5] = 0
            self.jobs[tag]['next_run'] = utime.mktime(tuple(tm))

            # if the target time is not passed for today then the task may be
            # run today
            if not passed_today:
                self.jobs[tag]['next_run'] -= self.jobs[tag]['period']

        self.jobs[tag]['next_run'] += self.jobs[tag]['period']

        if self.jobs[tag]['start_day'] is not None:
            weekdays = (
                'mon',
                'tue',
                'wed',
                'thu',
                'fri',
                'sat',
                'sun'
            )
            wd = utime.localtime(self.jobs[tag]['next_run'])[6]
            weekday = weekdays.index(self.jobs[tag]['start_day'])
            days_ahead = weekday - wd
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            self.jobs[tag]['next_run'] += (days_ahead * 60 * 60 * 24 -
            self.jobs[tag]['period'])

        if (self.jobs[tag]['start_day'] is not None and
            self.jobs[tag]['at_time'] is not None):
            # Let's see if we will still make that time we specified today
            if (self.jobs[tag]['next_run'] - self._now()) >= 7 * 60 * 60 * 24:
                self.jobs[tag]['next_run'] -= self.jobs[tag]['period']
