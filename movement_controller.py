from rov_path_planner import ROVPathPlanner, Position, Orientation

class MovementController:
    
    def __init__(self):
        self.path_planner = ROVPathPlanner()
        self.movement_history = []
    
    def set_current_state(self, position, orientation):
        """Mevcut durum güncelle"""
        self.path_planner.set_current_state(position, orientation)
    
    def calculate_movement_vector(self):
        """Temel hareket vektörü hesapla"""
        movements = self.path_planner.calculate_movement_requirements()
        motor_commands = self.path_planner.generate_motor_commands(movements)
        
        # Hareket geçmişine ekle
        self.movement_history.append(motor_commands)
        
        return motor_commands
    
    def calculate_circle_approach_strategy(self, center, radius):
        """Çembere yaklaşma stratejisi"""
        movements = self.path_planner.plan_circle_approach(center, radius)
        return self.path_planner.generate_motor_commands(movements)
    
    def get_movement_summary(self):
        """Hareket özeti"""
        path_summary = self.path_planner.get_path_summary()
        
        # Verimlilik hesapla
        total_commands = len(self.movement_history)
        efficiency = 0.8 if total_commands > 0 else 0.0
        
        return {
            'path_summary': path_summary,
            'total_commands': total_commands,
            'efficiency_metrics': {'efficiency': efficiency}
        }
