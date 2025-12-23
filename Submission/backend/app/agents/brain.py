from typing import List, Dict, Optional, Any
import numpy as np

class AgentBrain:
    def __init__(self, agent):
        self.agent = agent
        self.action_queue: List[Dict] = []
        self.current_goal: Optional[str] = None
        self.last_plan_step: int = 0
        
    def get_next_action(self, world) -> Optional[Dict]:
        """
        Main entry point. Returns an action plan or None.
        """
        # 1. Validate Current Plan
        if self.action_queue:
            # Check if current action is still valid?
            # For simplicity, just pop. 
            # Ideally, we verify: "Am I still where I should be?"
            action = self.action_queue[0]
            
            # Simple validity check: If target is gone?
            # We'll assume actions are robust enough or will fail gracefully in execute.
            pass

        # 2. Re-Plan if empty or stale (every 20 steps)
        if not self.action_queue or (world.time_step - self.last_plan_step > 20):
            self.formulate_plan(world)
            self.last_plan_step = world.time_step
            
        # 3. Return next action
        if self.action_queue:
            action = self.action_queue[0] # Peek
            
            # STICKY ACTIONS Logic
            # Some actions (like find_resource) take multiple steps (move -> gather).
            # We must NOT pop them until they are actually done.
            
            if action['action'] == 'find_resource':
                # Check Completion: Do we have the item?
                res_type = action.get('resource')
                found = False
                
                # Check Inventory
                for slot in self.agent.inventory:
                    # Normalize resource type
                    rt = res_type.lower()
                    if rt in ['consumable', 'food', 'fruit', 'berry']:
                        if "consumable" in slot['item']['tags']: found = True
                    elif rt == 'wood':
                        if slot['item']['name'] == 'Wood': found = True
                    elif res_type == 'stone':
                         if slot['item']['name'] == 'Stone': found = True
                
                if found:
                    # Success! We can proceed.
                    self.action_queue.pop(0)
                    if self.action_queue:
                         return self.action_queue.pop(0) # Return the next step
                    else:
                         return None
                else:
                    # Still running. Check Timeout.
                    start_time = action.get('started_at')
                    if not start_time:
                        action['started_at'] = world.time_step
                        start_time = world.time_step
                        
                    if world.time_step - start_time > 50:
                        # Timeout - Failed to find resource
                        self.agent.log_diary(f"Plan Timeout: Could not find {res_type}.")
                        self.action_queue = [] # Abort plan
                        self.current_goal = "Plan Failed (Timeout)"
                        return None
                    
                    # Return current action again (don't pop)
                    return action

            # Normal Action: Pop and Return
            return self.action_queue.pop(0)
            
        return None

    def formulate_plan(self, world):
        """
        Simulates future and generates a sequence of actions.
        """
        self.action_queue = [] # Clear old plan
        
        # A. Simulation (Lookahead 100 steps)
        # Predict State
        current_hunger = self.agent.nafs.hunger
        predicted_hunger = current_hunger + (0.002 * 100) # 100 steps decay
        
        # B. Goal Prioritization
        
        # 1. Critical Survival (Starvation Horizon) - Proactive (40%)
        if predicted_hunger >= 0.4:
            # Plan: Find Food -> Go -> Gather -> Eat
            plan = self._plan_acquire_food(world)
            if plan:
                self.current_goal = "Prevent Starvation"
                self.action_queue = plan
                return

        # 2. Tribe Duties (If Leader)
        if self.agent.attributes.leader_id == self.agent.id:
            tribe = world.tribes.get(self.agent.attributes.tribe_id)
            if tribe:
                # Check Tribe Needs
                if tribe.resources['food'] < len(tribe.members) * 2:
                     # Plan: Gather Food for Tribe
                     plan = self._plan_stockpile(world, 'food')
                     if plan:
                         self.current_goal = "Tribe Duty: Food"
                         self.action_queue = plan
                         return
                # Check Safety/Territory? (Future)

        # 3. Personal Prosperity (Hoarding/Crafting)
        # Always be useful.
        
        # Priority A: Gather Essential Materials (Wood/Stone)
        # Random choice to avoid synchronization
        resource = 'wood' if np.random.random() < 0.5 else 'stone'
        plan = self._plan_stockpile(world, resource)
        if plan:
             self.current_goal = f"Gather {resource.capitalize()}"
             self.action_queue = plan
             return
             
        # Priority B: Exploration
        self.current_goal = "Explore"
        self.action_queue = [{'action': 'panic_search'}] # Reusing search logic for exploring
        return

    def _plan_acquire_food(self, world) -> List[Dict]:
        """
        Generates action sequence to handle hunger.
        """
        # 1. Do I have food?
        for slot in self.agent.inventory:
            if "consumable" in slot['item']['tags']:
                return [{'action': 'eat_from_inventory'}]
                
        # 2. Find Food in World
        # Reuse Logic? Or reimplement A*?
        # We need a 'find' action that works. 
        # But Brain should be specific: "Go to (x,y)"
        
        # Scan Memory first
        known_food = self.agent.spatial_memory.get('food', [])
        target = None
        
        # Filter valid
        valid_targets = []
        for pos in known_food:
            dist = (pos[0]-self.agent.x)**2 + (pos[1]-self.agent.y)**2
            valid_targets.append((dist, pos))
            
        valid_targets.sort() # Nearest first
        
        if valid_targets:
            target_pos = valid_targets[0][1]
            # Sequence: Reach -> Gather -> Eat
            # Note: 'find_resource' action handles navigation + gathering logic usually.
            # But Brain should be explicit.
            # Let's use high-level "find_resource" for now as it encapsulates "Go To + Gather"
            return [
                {'action': 'find_resource', 'resource': 'food'},
                {'action': 'eat_from_inventory'} # Scheduled after find
            ]
            
        # If no memory, Explore?
        return [{'action': 'panic_search'}]

    def _plan_stockpile(self, world, resource_type) -> List[Dict]:
        """
        Plan to gather resource and bring to tribe (placeholder logic).
        For now, just efficient gathering.
        """
        return [{'action': 'find_resource', 'resource': resource_type}]

    def to_dict(self):
        return {
            "current_goal": self.current_goal,
            "action_queue": [a.get('action') + (f" ({a.get('resource')})" if 'resource' in a else "") for a in self.action_queue],
            "plan_length": len(self.action_queue)
        }
