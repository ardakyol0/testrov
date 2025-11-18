import os
import sys
try:
    from video_analysis import VideoAnalyzer
    from movement_controller import MovementController, Position, Orientation
    from decision_maker import DecisionMaker
    print("Modules imported successfully")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_basic():
    try:
        controller = MovementController()
        controller.set_current_state(Position(0, 0, 0), Orientation(0, 0, 0))
        
        decision_maker = DecisionMaker()
        test_data = {
            'movement_data': [{'velocity': 1.0, 'direction': 0}],
            'circle_detection_data': [{'frame': 0, 'circles': [], 'yellow_circles': []}]
        }
        result = decision_maker.analyze_decision_patterns(test_data)
        
        print("Test passed")
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def run_tests():
    print("Running tests...")
    
    if test_basic():
        print("All tests passed")
        return True
    else:
        print("Tests failed")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
