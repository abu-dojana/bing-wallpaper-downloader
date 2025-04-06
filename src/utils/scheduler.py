class Scheduler:
    def __init__(self):
        self.scheduled_tasks = []

    def schedule_download(self, frequency, wallpaper_type, resolution):
        # Logic to schedule wallpaper downloads based on user-defined settings
        task = {
            'frequency': frequency,
            'type': wallpaper_type,
            'resolution': resolution
        }
        self.scheduled_tasks.append(task)
        return task

    def cancel_schedule(self, task):
        # Logic to cancel a scheduled wallpaper download
        if task in self.scheduled_tasks:
            self.scheduled_tasks.remove(task)
            return True
        return False

    def get_scheduled_tasks(self):
        return self.scheduled_tasks