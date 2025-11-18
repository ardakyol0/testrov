import numpy as np
import math
from rov_path_planner import ROVPathPlanner, Position, Orientation

class DecisionMaker:
    
    def __init__(self):
        self.path_planner = ROVPathPlanner()
        self.decision_history = []
    
    def analyze_decision_patterns(self, video_data):
        movement_data = video_data.get('movement_data', [])
        circle_data = video_data.get('circle_detection_data', [])
        
        if len(movement_data) < 1:
            return {"total_decisions": 0, "decision_accuracy": 0.0, "average_velocity": 0.0}
        
        decisions = []
        good_decisions = 0
        orientation_data = []  # Roll-pitch-yaw verileri
        
        for i, data in enumerate(movement_data):
            velocity = data.get('velocity', 0)
            direction = data.get('direction', 0)
            yellow_detected = False
            
            # ROV pozisyon ve orientasyon hesaplaması
            frame_position_x = i * 2.5 + velocity * 5
            frame_position_y = velocity * math.sin(math.radians(direction)) * 3
            current_pos = Position(frame_position_x, frame_position_y, 0)
            current_orient = Orientation(0, 0, direction)  # Yaw açısı
            
            # Roll-pitch-yaw verilerini kaydet
            orientation_data.append({
                'frame': i,
                'position': (current_pos.x, current_pos.y, current_pos.z),
                'orientation': (current_orient.roll, current_orient.pitch, current_orient.yaw)
            })
            
            # Sarı çember kontrolü
            yellow_circles_in_frame = []
            normal_circles_in_frame = []
            for circle_info in circle_data:
                if circle_info.get('frame') == i:
                    if circle_info.get('yellow_circles'):
                        yellow_detected = True
                        yellow_circles_in_frame = circle_info.get('yellow_circles')
                    if circle_info.get('circles'):
                        normal_circles_in_frame = circle_info.get('circles')
                    break
            
            # Video analizi tabanlı karar verme
            velocity_change = 0
            direction_change = 0
            
            if i > 0:
                prev_velocity = movement_data[i-1].get('velocity', 0)
                prev_direction = movement_data[i-1].get('direction', 0)
                velocity_change = abs(velocity - prev_velocity)
                direction_change = abs(direction - prev_direction)
            
            decision_made = False
            decision_quality = 0  # 0-1 arası kalite skoru
            
            if yellow_detected:
                decisions.append('approach_yellow')
                # Sarı çembere yaklaşırken hız artışı = iyi karar
                if velocity > prev_velocity if i > 0 else velocity > 1.0:
                    decision_quality = 0.9
                else:
                    decision_quality = 0.6
                decision_made = True
                    
            elif velocity < 0.3:  # Çok yavaş hareket
                decisions.append('stop')
                # Durma kararının kalitesi: çevrede engel var mı?
                if len(normal_circles_in_frame) > 0:
                    decision_quality = 0.8  # Engel var, durma mantıklı
                else:
                    decision_quality = 0.4  # Engel yok ama durmuş
                decision_made = True
                
            elif velocity > 3.0:  # Hızlı hareket
                decisions.append('move')
                # Hızlı hareketin kalitesi: yön değişimi az mı?
                if direction_change < 15:  # Düz gidiyor
                    decision_quality = 0.8
                else:
                    decision_quality = 0.5  # Riskli
                decision_made = True
                
            elif len(normal_circles_in_frame) > 0:  # Çember var
                decisions.append('navigate')
                # Navigasyon kalitesi: çember etrafında uygun hareket
                if 0.5 < velocity < 2.5 and direction_change < 30:
                    decision_quality = 0.8
                else:
                    decision_quality = 0.6
                decision_made = True
                
            else:  # Varsayılan durum
                decisions.append('cruise')
                # Serbest hareket kalitesi: düzenli hız ve yön
                if 1.0 < velocity < 2.0 and direction_change < 20:
                    decision_quality = 0.7
                else:
                    decision_quality = 0.5
                decision_made = True
            
            # Kalite skoruna göre good_decisions hesapla
            if decision_quality > 0.7:
                good_decisions += 1
        
        # Analiz tabanlı istatistik hesaplamaları
        avg_velocity = sum(d.get('velocity', 0) for d in movement_data) / len(movement_data)
        accuracy = good_decisions / len(decisions) if decisions else 0  # Kalite skorları
        yellow_frames = sum(1 for d in circle_data if d.get('yellow_circles'))
        efficiency = yellow_frames / len(movement_data) if movement_data else 0
        
        # Ek metrikler
        total_circles = sum(d.get('circles_count', 0) for d in circle_data)
        avg_direction_change = 0
        if len(movement_data) > 1:
            direction_changes = []
            for i in range(1, len(movement_data)):
                prev_dir = movement_data[i-1].get('direction', 0)
                curr_dir = movement_data[i].get('direction', 0)
                direction_changes.append(abs(curr_dir - prev_dir))
            avg_direction_change = sum(direction_changes) / len(direction_changes)
        
        # Karar geçmişine ekle
        self.decision_history.extend(decisions)
        
        return {
            'decision_accuracy': accuracy,
            'total_decisions': len(decisions),
            'average_velocity': avg_velocity,
            'movement_efficiency': efficiency,
            'decisions': decisions,
            'orientation_data': orientation_data,
            'total_circles_detected': total_circles,
            'average_direction_change': avg_direction_change,
            'good_decisions_count': good_decisions
        }
    def generate_decision_report(self, analysis_results, output_path):
        """Karar analizi raporunu oluştur"""
        report = []
        report.append("ROV VIDEO ANALYSIS")
        report.append("=" * 55)
        report.append(f"Total Decisions: {analysis_results.get('total_decisions', 0)}")
        report.append(f"Decision Quality: {analysis_results.get('decision_accuracy', 0):.1%}")
        report.append(f"Average Speed: {analysis_results.get('average_velocity', 0):.2f} units/frame")
        report.append(f"Yellow Target Efficiency: {analysis_results.get('movement_efficiency', 0):.1%}")
        report.append(f"Circles Detected: {analysis_results.get('total_circles_detected', 0)}")
        report.append(f"Avg Direction Change: {analysis_results.get('average_direction_change', 0):.1f}°/frame")
        
        # Karar türleri analizi
        decisions = analysis_results.get('decisions', [])
        orientation_data = analysis_results.get('orientation_data', [])
        
        if decisions:
            report.append("")
            report.append("DECISION BREAKDOWN:")
            report.append("-" * 20)
            
            # Karar türlerini say
            decision_types = {}
            for decision in decisions:
                decision_types[decision] = decision_types.get(decision, 0) + 1
            
            for decision_type, count in decision_types.items():
                percentage = (count / len(decisions)) * 100
                report.append(f"  {decision_type}: {count} ({percentage:.1f}%)")
        
        # Roll-Pitch-Yaw analiz sonuçları
        if orientation_data:
            report.append("")
            report.append("ORIENTATION ANALYSIS :")
            report.append("-" * 45)
            
            yaw_values = [data['orientation'][2] for data in orientation_data]
            yaw_changes = [abs(yaw_values[i] - yaw_values[i-1]) for i in range(1, len(yaw_values))]
            
            avg_yaw = sum(yaw_values) / len(yaw_values)
            min_yaw = min(yaw_values)
            max_yaw = max(yaw_values)
            avg_yaw_change = sum(yaw_changes) / len(yaw_changes) if yaw_changes else 0
            
            report.append(f"  Average Yaw: {avg_yaw:.1f}°")
            report.append(f"  Yaw Range: {min_yaw:.1f}° to {max_yaw:.1f}°")
            report.append(f"  Avg Yaw Change: {avg_yaw_change:.1f}°/frame")
            report.append(f"  Orientation Stability: {'High' if avg_yaw_change < 5 else 'Medium' if avg_yaw_change < 15 else 'Low'}")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
    def visualize_decision_analysis(self, analysis_results, save_path=None):
        pass