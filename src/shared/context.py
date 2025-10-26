from typing import Dict, Any, List
from datetime import datetime, timedelta
from src.core.models import IntelligenceEvent

class SharedContext:
    """Manages shared intelligence context across modules"""
    
    def __init__(self):
        self.user_profiles: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.task_context: Dict[str, Any] = {}
        self.insight_cache: Dict[str, Any] = {}
        self.behavior_patterns: Dict[str, Any] = {}
        self.last_updated = datetime.now()

    def update_from_event(self, event: IntelligenceEvent):
        """Update shared context based on incoming events"""
        self.last_updated = datetime.now()
        
        if event.event_type.value.startswith('task_'):
            self._update_task_context(event)
        elif event.event_type.value.startswith('message_'):
            self._update_conversation_context(event)
        elif event.event_type.value == 'user_activity':
            self._update_user_behavior(event)
        elif event.event_type.value == 'insight_generated':
            self._update_insight_cache(event)

    def _update_task_context(self, event: IntelligenceEvent):
        """Update task-related context"""
        task_id = event.payload.get('task_id', 'unknown')
        if task_id not in self.task_context:
            self.task_context[task_id] = {}
        
        self.task_context[task_id].update({
            'last_activity': datetime.now(),
            'status': event.payload.get('status', 'unknown'),
            **event.payload
        })

    def _update_conversation_context(self, event: IntelligenceEvent):
        """Update conversation history and context"""
        conversation_entry = {
            'timestamp': datetime.now(),
            'event_type': event.event_type.value,
            'source': str(event.source_module),
            'content': event.payload.get('content', ''),
            'metadata': event.payload.get('metadata', {})
        }
        self.conversation_history.append(conversation_entry)
        
        if len(self.conversation_history) > 100:
            self.conversation_history.pop(0)

    def _update_user_behavior(self, event: IntelligenceEvent):
        """Update user behavior patterns"""
        user_id = event.payload.get('user_id', 'default')
        activity_type = event.payload.get('activity_type', 'unknown')
        
        if user_id not in self.behavior_patterns:
            self.behavior_patterns[user_id] = {}
        
        if activity_type not in self.behavior_patterns[user_id]:
            self.behavior_patterns[user_id][activity_type] = 0
        
        self.behavior_patterns[user_id][activity_type] += 1

    def _update_insight_cache(self, event: IntelligenceEvent):
        """Cache generated insights for future reference"""
        insight_key = f"{event.source_module}_{datetime.now().timestamp()}"
        self.insight_cache[insight_key] = {
            'insight': event.payload.get('insight', {}),
            'timestamp': datetime.now(),
            'source_module': event.source_module
        }
        
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.insight_cache = {
            k: v for k, v in self.insight_cache.items() 
            if v['timestamp'] > cutoff_time
        }

    def get_relevant_context(self, event: IntelligenceEvent) -> Dict[str, Any]:
        """Get context relevant to the current event"""
        relevant_context = {
            'recent_conversations': self.conversation_history[-5:],
            'active_tasks': {
                k: v for k, v in self.task_context.items() 
                if v.get('status') in ['pending', 'in_progress']
            },
            'recent_insights': list(self.insight_cache.values())[-3:],
        }
        
        user_id = event.payload.get('user_id')
        if user_id and user_id in self.behavior_patterns:
            relevant_context['user_behavior'] = self.behavior_patterns[user_id]
        
        return relevant_context

    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about the shared context"""
        return {
            'total_conversations': len(self.conversation_history),
            'active_tasks': len([t for t in self.task_context.values() if t.get('status') in ['pending', 'in_progress']]),
            'cached_insights': len(self.insight_cache),
            'tracked_users': len(self.behavior_patterns),
            'last_updated': self.last_updated.isoformat()
        }