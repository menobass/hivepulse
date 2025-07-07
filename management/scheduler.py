"""
Scheduler Module
Handles automated daily report scheduling for the Hive Ecuador Pulse bot
"""

import logging
from datetime import datetime, time
from typing import Optional
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from utils.helpers import get_ecuador_timezone, get_ecuador_time


class ReportScheduler:
    """Manages scheduled daily reports"""
    
    def __init__(self, pulse_bot):
        """Initialize scheduler with bot instance"""
        self.pulse_bot = pulse_bot
        self.logger = logging.getLogger(__name__)
        
        # Initialize scheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # Ecuador timezone
        self.ecuador_tz = get_ecuador_timezone()
        
        # Schedule daily report
        self._schedule_daily_report()
    
    def _schedule_daily_report(self):
        """Schedule daily report at 9 PM Ecuador time"""
        try:
            # Create cron trigger for 9 PM Ecuador time
            trigger = CronTrigger(
                hour=21,  # 9 PM
                minute=0,
                timezone=self.ecuador_tz
            )
            
            # Add job to scheduler
            self.scheduler.add_job(
                self._generate_daily_report,
                trigger=trigger,
                id='daily_report',
                name='Daily Hive Ecuador Pulse Report',
                replace_existing=True
            )
            
            self.logger.info("Daily report scheduled for 21:00 Ecuador time")
            
        except Exception as e:
            self.logger.error(f"Error scheduling daily report: {str(e)}")
            raise
    
    def _generate_daily_report(self):
        """Generate and post daily report"""
        try:
            self.logger.info("Generating scheduled daily report")
            
            # Get current Ecuador time
            ecuador_time = get_ecuador_time()
            date_str = ecuador_time.strftime('%Y-%m-%d')
            
            # Generate report
            report_content, chart_files = self.pulse_bot.create_daily_report(date_str)
            
            # Post report if not in dry run mode
            if not self.pulse_bot.config.get('dry_run', False):
                success = self.pulse_bot.post_daily_report(report_content, chart_files)
                
                if success:
                    self.logger.info("Daily report posted successfully")
                else:
                    self.logger.error("Failed to post daily report")
            else:
                self.logger.info("Dry run mode - report generated but not posted")
                
        except Exception as e:
            self.logger.error(f"Error generating daily report: {str(e)}")
            # Don't raise exception to prevent scheduler from stopping
    
    def _job_listener(self, event):
        """Listen for job execution events"""
        if event.exception:
            self.logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            self.logger.info(f"Job {event.job_id} executed successfully")
    
    def start(self):
        """Start the scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.logger.info("Report scheduler started")
            else:
                self.logger.warning("Scheduler is already running")
                
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {str(e)}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.logger.info("Report scheduler stopped")
            else:
                self.logger.warning("Scheduler is not running")
                
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {str(e)}")
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Get next scheduled run time"""
        try:
            job = self.scheduler.get_job('daily_report')
            if job:
                return job.next_run_time
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting next run time: {str(e)}")
            return None
    
    def reschedule_daily_report(self, hour: int = 21, minute: int = 0):
        """Reschedule daily report to different time"""
        try:
            # Remove existing job
            self.scheduler.remove_job('daily_report')
            
            # Create new trigger
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=self.ecuador_tz
            )
            
            # Add new job
            self.scheduler.add_job(
                self._generate_daily_report,
                trigger=trigger,
                id='daily_report',
                name='Daily Hive Ecuador Pulse Report',
                replace_existing=True
            )
            
            self.logger.info(f"Daily report rescheduled to {hour:02d}:{minute:02d} Ecuador time")
            
        except Exception as e:
            self.logger.error(f"Error rescheduling daily report: {str(e)}")
            raise
    
    def trigger_manual_report(self, date: Optional[str] = None):
        """Trigger manual report generation"""
        try:
            if date is None:
                date = get_ecuador_time().strftime('%Y-%m-%d')
            
            self.logger.info(f"Triggering manual report for {date}")
            
            # Generate report
            report_content, chart_files = self.pulse_bot.create_daily_report(date)
            
            # Post report if not in dry run mode
            if not self.pulse_bot.config.get('dry_run', False):
                success = self.pulse_bot.post_daily_report(report_content, chart_files)
                return success
            else:
                self.logger.info("Dry run mode - report generated but not posted")
                return True
                
        except Exception as e:
            self.logger.error(f"Error triggering manual report: {str(e)}")
            return False
    
    def get_scheduler_status(self) -> dict:
        """Get scheduler status information"""
        try:
            status = {
                'running': self.scheduler.running,
                'jobs': [],
                'next_run': None
            }
            
            # Get job information
            for job in self.scheduler.get_jobs():
                job_info = {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                status['jobs'].append(job_info)
                
                # Set next run time for daily report
                if job.id == 'daily_report':
                    status['next_run'] = job.next_run_time.isoformat() if job.next_run_time else None
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting scheduler status: {str(e)}")
            return {'running': False, 'jobs': [], 'next_run': None}
    
    def add_test_job(self, delay_minutes: int = 1):
        """Add a test job for debugging"""
        try:
            from datetime import timedelta
            
            # Calculate run time
            run_time = get_ecuador_time() + timedelta(minutes=delay_minutes)
            
            # Add test job
            self.scheduler.add_job(
                self._test_job,
                'date',
                run_date=run_time,
                id='test_job',
                name='Test Job',
                replace_existing=True
            )
            
            self.logger.info(f"Test job scheduled for {run_time}")
            
        except Exception as e:
            self.logger.error(f"Error adding test job: {str(e)}")
    
    def _test_job(self):
        """Test job for debugging"""
        try:
            self.logger.info("Test job executed successfully")
            print("🎉 Test job executed at:", get_ecuador_time())
            
        except Exception as e:
            self.logger.error(f"Error in test job: {str(e)}")
    
    def list_jobs(self) -> list:
        """List all scheduled jobs"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                jobs.append({
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                })
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error listing jobs: {str(e)}")
            return []
    
    def remove_job(self, job_id: str):
        """Remove a specific job"""
        try:
            self.scheduler.remove_job(job_id)
            self.logger.info(f"Job {job_id} removed")
            
        except Exception as e:
            self.logger.error(f"Error removing job {job_id}: {str(e)}")
    
    def pause_job(self, job_id: str):
        """Pause a specific job"""
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f"Job {job_id} paused")
            
        except Exception as e:
            self.logger.error(f"Error pausing job {job_id}: {str(e)}")
    
    def resume_job(self, job_id: str):
        """Resume a specific job"""
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f"Job {job_id} resumed")
            
        except Exception as e:
            self.logger.error(f"Error resuming job {job_id}: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running
    
    def __del__(self):
        """Cleanup scheduler on deletion"""
        try:
            if hasattr(self, 'scheduler') and self.scheduler.running:
                self.scheduler.shutdown()
        except:
            pass
