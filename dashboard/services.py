import re
from datetime import timedelta
from django.utils import timezone
from .models import Task, AIActionLog, Notification, ActivityFeed, RewardPoints


class AIService:
    """AI Service for processing commands and suggestions."""

    def __init__(self, user):
        self.user = user

    def process_prompt(self, prompt):
        """Main entry point for processing user prompts."""
        intent = self._detect_intent(prompt)
        
        if intent == 'create_task':
            return self._handle_create_task(prompt)
        elif intent == 'list_tasks':
            return self._handle_list_tasks()
        elif intent == 'summary':
            return self._handle_summary()
        elif intent == 'help':
            return self._handle_help()
        else:
            return self._handle_general(prompt)

    def _detect_intent(self, prompt):
        """Detect user intent from prompt."""
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in ['create task', 'add task', 'new task', 'remind me']):
            return 'create_task'
        if any(kw in prompt_lower for kw in ['show tasks', 'list tasks', 'my tasks']):
            return 'list_tasks'
        if any(kw in prompt_lower for kw in ['summary', 'report', 'overview']):
            return 'summary'
        if 'help' in prompt_lower:
            return 'help'
        return 'general'

    def _extract_task_info(self, prompt):
        """Extract task details from prompt."""
        # Remove common prefixes
        title = re.sub(r'^(create task|add task|new task|remind me to):?\s*', '', prompt, flags=re.I).strip()
        
        # Detect priority
        priority = 'medium'
        if any(kw in prompt.lower() for kw in ['urgent', 'asap', 'critical']):
            priority = 'urgent'
        elif any(kw in prompt.lower() for kw in ['important', 'high priority']):
            priority = 'high'
        elif any(kw in prompt.lower() for kw in ['low priority', 'whenever']):
            priority = 'low'
        
        # Detect due date
        due_date = None
        if 'tomorrow' in prompt.lower():
            due_date = timezone.now() + timedelta(days=1)
        elif 'next week' in prompt.lower():
            due_date = timezone.now() + timedelta(weeks=1)
        elif 'today' in prompt.lower():
            due_date = timezone.now() + timedelta(hours=8)

        return {'title': title[:200], 'priority': priority, 'due_date': due_date}

    def _handle_create_task(self, prompt):
        """Create a task from prompt."""
        info = self._extract_task_info(prompt)
        
        if not info['title']:
            return {'success': False, 'message': 'Could not extract task title. Try: "Create task: your task description"'}

        task = Task.objects.create(
            title=info['title'],
            priority=info['priority'],
            due_date=info['due_date'],
            created_by=self.user,
            assigned_to=self.user,
            ai_generated=True,
            description=f"Created via AI. Original: {prompt}"
        )

        # Log action
        AIActionLog.objects.create(
            user=self.user,
            action_type='task_create',
            input_text=prompt,
            output_text=f"Created: {task.title}",
            success=True
        )

        # Create notification
        Notification.objects.create(
            user=self.user,
            notification_type='ai_action',
            title='Task Created by AI',
            message=f'Created: {task.title}',
            related_object_id=task.id
        )

        # Log activity
        ActivityFeed.objects.create(
            user=self.user,
            action_type='task_created',
            description=f'Created task: {task.title}',
            related_object_id=task.id
        )

        msg = f"✅ **Task Created!**\n\n**{task.title}**\nPriority: {task.get_priority_display()}"
        if task.due_date:
            msg += f"\nDue: {task.due_date.strftime('%b %d, %Y')}"

        return {'success': True, 'message': msg, 'task_id': task.id, 'actions': ['refresh_tasks']}

    def _handle_list_tasks(self):
        """List user's pending tasks."""
        tasks = Task.objects.filter(
            assigned_to=self.user,
            status__in=['pending', 'in_progress']
        )[:5]

        if not tasks:
            return {'success': True, 'message': "🎉 No pending tasks! You're all caught up."}

        task_list = "\n".join([f"• {t.title} ({t.get_priority_display()})" for t in tasks])
        return {'success': True, 'message': f"**Your Tasks:**\n\n{task_list}"}

    def _handle_summary(self):
        """Generate activity summary."""
        week_ago = timezone.now() - timedelta(days=7)
        
        created = Task.objects.filter(created_by=self.user, created_at__gte=week_ago).count()
        completed = Task.objects.filter(assigned_to=self.user, status='done', completed_at__gte=week_ago).count()
        pending = Task.objects.filter(assigned_to=self.user, status__in=['pending', 'in_progress']).count()
        points = RewardPoints.get_user_total(self.user)

        msg = f"""📊 **Weekly Summary**

• Tasks Created: {created}
• Tasks Completed: {completed}
• Tasks Pending: {pending}
• Total Points: {points}"""

        return {'success': True, 'message': msg}

    def _handle_help(self):
        """Return help message."""
        return {'success': True, 'message': """🤖 **AI Assistant Help**

**Commands:**
• "Create task: [description]" - Create a new task
• "Show my tasks" - List pending tasks
• "Summary" - Get weekly activity summary

**Tips:**
• Add "urgent" or "high priority" for priority
• Add "tomorrow" or "next week" for due dates"""}

    def _handle_general(self, prompt):
        """Handle general queries."""
        return {'success': True, 'message': f'I understood: "{prompt}"\n\nTry "help" to see what I can do!'}

    @staticmethod
    def suggest_priority(task):
        """Suggest priority based on task content."""
        text = f"{task.title} {task.description}".lower()
        
        if any(kw in text for kw in ['urgent', 'asap', 'critical', 'emergency']):
            return 'urgent'
        if any(kw in text for kw in ['important', 'priority', 'client']):
            return 'high'
        if any(kw in text for kw in ['whenever', 'optional', 'maybe']):
            return 'low'
        return 'medium'