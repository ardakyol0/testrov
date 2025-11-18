import math

class Position:
    """ROV'un 3B pozisyonu"""
    def __init__(self, x=0, y=0, z=0):
        self.x = x  # x pozisyon
        self.y = y  # y pozisyon  
        self.z = z  # z pozisyon

class Orientation:
    """ROV'un yönelimi"""
    def __init__(self, roll=0, pitch=0, yaw=0):
        self.roll = roll    # X ekseni dönüş 
        self.pitch = pitch  # Y ekseni dönüş 
        self.yaw = yaw      # Z ekseni dönüş 

class ROVPathPlanner:
    """ROV'un hareket ve yol planlama sistemi"""
    
    def __init__(self):
        # Mevcut durum
        self.current_position = Position()
        self.current_orientation = Orientation()
        
        # Hedef durum
        self.target_position = Position()
        self.target_orientation = Orientation()
    
    def set_current_state(self, position, orientation):
        """Mevcut pozisyon ve yönelimi güncelle"""
        self.current_position = position
        self.current_orientation = orientation
    
    def set_target_state(self, position, orientation):
        """Hedef pozisyon ve yönelimi belirle"""
        self.target_position = position
        self.target_orientation = orientation
    
    def calculate_movement_requirements(self):
        """Hedefe ulaşmak için gereken hareketleri hesapla"""
        # Pozisyon farkları
        delta_x = self.target_position.x - self.current_position.x
        delta_y = self.target_position.y - self.current_position.y
        delta_z = self.target_position.z - self.current_position.z
        
        # Açı farkları
        delta_roll = self.target_orientation.roll - self.current_orientation.roll
        delta_pitch = self.target_orientation.pitch - self.current_orientation.pitch
        delta_yaw = self.target_orientation.yaw - self.current_orientation.yaw
        
        # Açıları -180 ile +180 arasına normalleştir
        delta_yaw = self._normalize_angle(delta_yaw)
        delta_roll = self._normalize_angle(delta_roll)
        delta_pitch = self._normalize_angle(delta_pitch)
        
        return {
            'forward_movement': delta_x,      
            'sideways_movement': delta_y,     
            'vertical_movement': delta_z,     
            'roll_adjustment': delta_roll,    
            'pitch_adjustment': delta_pitch,  
            'yaw_adjustment': delta_yaw       
        }
    
    def plan_circle_approach(self, circle_center, approach_distance=50):
        """Sarı çembere yaklaşma yolu planla"""
        circle_x, circle_y = circle_center
        
        # Çembere olan uzaklık ve açı
        distance_to_circle = math.sqrt(
            (circle_x - self.current_position.x)**2 + 
            (circle_y - self.current_position.y)**2
        )
        
        # Çembere bakma açısı
        angle_to_circle = math.atan2(
            circle_y - self.current_position.y,
            circle_x - self.current_position.x
        )
        
        # Hedef pozisyon: çemberden approach_distance kadar uzakta
        target_x = circle_x - approach_distance * math.cos(angle_to_circle)
        target_y = circle_y - approach_distance * math.sin(angle_to_circle)
        
        # Hedef yönelim: çembere doğru bak
        target_yaw = math.degrees(angle_to_circle)
        
        # Hedef durumu ayarla
        self.set_target_state(
            Position(target_x, target_y, self.current_position.z),
            Orientation(0, 0, target_yaw)
        )
        
        return self.calculate_movement_requirements()
    
    def plan_circular_path(self, circle_center, radius=100):
        """Çember etrafında hareket yolu planla"""
        circle_x, circle_y = circle_center
        
        # Mevcut açı
        current_angle = math.atan2(
            self.current_position.y - circle_y,
            self.current_position.x - circle_x
        )
        
        # Sonraki açı 
        next_angle = current_angle + math.radians(5)  # 5 derece ilerle
        
        # Çember üzerindeki yeni pozisyon
        target_x = circle_x + radius * math.cos(next_angle)
        target_y = circle_y + radius * math.sin(next_angle)
        
        # Hareket yönü çembere teğet
        movement_direction = math.degrees(next_angle + math.pi/2)
        
        # Hedef durumu ayarla
        self.set_target_state(
            Position(target_x, target_y, self.current_position.z),
            Orientation(0, 0, movement_direction)
        )
        
        return self.calculate_movement_requirements()
    
    def generate_motor_commands(self, movements):
        """Hareket gereksinimlerini motor komutlarına çevir"""
        # Motor gücü -1.0 ile +1.0 arasında
        commands = {
            'forward_thruster': self._limit_power(movements['forward_movement'] / 100),
            'sideways_thruster': self._limit_power(movements['sideways_movement'] / 100),
            'vertical_thruster': self._limit_power(movements['vertical_movement'] / 100),
            'roll_motor': self._limit_power(movements['roll_adjustment'] / 45),
            'pitch_motor': self._limit_power(movements['pitch_adjustment'] / 45),
            'yaw_motor': self._limit_power(movements['yaw_adjustment'] / 45)
        }
        return commands
    
    def get_path_summary(self):
        """Yol planlama özeti"""
        movements = self.calculate_movement_requirements()
        total_distance = math.sqrt(
            movements['forward_movement']**2 + 
            movements['sideways_movement']**2 + 
            movements['vertical_movement']**2
        )
        
        return {
            'current_position': (self.current_position.x, self.current_position.y, self.current_position.z),
            'target_position': (self.target_position.x, self.target_position.y, self.target_position.z),
            'total_distance': total_distance,
            'required_movements': movements
        }
    
    def _normalize_angle(self, angle):
        while angle > 180:
            angle -= 360
        while angle < -180:
            angle += 360
        return angle
    
    def _limit_power(self, value):
        return max(-1.0, min(1.0, value))