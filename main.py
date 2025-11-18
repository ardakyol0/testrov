import os
import sys
from video_analysis import VideoAnalyzer
from decision_maker import DecisionMaker
class ROVAnalysisSystem:
    def __init__(self, videos_dir, output_dir="results"):
        self.videos_dir = videos_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.decision_maker = DecisionMaker()
        print(f"System started: {videos_dir} -> {output_dir}")
    def find_videos(self):
        videos = []
        for file in os.listdir(self.videos_dir):
            if file.endswith(('.avi',)):
                videos.append(os.path.join(self.videos_dir, file))
        return videos
    def analyze_video(self, video_path):
        print(f"Analyzing: {os.path.basename(video_path)}")
        analyzer = VideoAnalyzer(video_path)
        results = analyzer.analyze_video()
        
        name = os.path.splitext(os.path.basename(video_path))[0]
        results_file = os.path.join(self.output_dir, f"{name}_analysis.json")
        analyzer.save_analysis_results(results, results_file)
        
        decision_results = self.decision_maker.analyze_decision_patterns(results)
        report_file = os.path.join(self.output_dir, f"{name}_report.txt")
        self.decision_maker.generate_decision_report(decision_results, report_file)
        
        return results
    def analyze_all(self):
        videos = self.find_videos()
        print(f"Found {len(videos)} videos")
        for video in videos:
            try:
                self.analyze_video(video)
                print(f"✓ Done: {os.path.basename(video)}")
            except Exception as e:
                print(f"✗ Error: {e}")
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--videos-dir', default='videos')
    parser.add_argument('--output', default='results')
    parser.add_argument('--single-video')
    args = parser.parse_args()
    
    system = ROVAnalysisSystem(args.videos_dir, args.output)
    
    if args.single_video:
        system.analyze_video(args.single_video)
    else:
        system.analyze_all()
if __name__ == "__main__":
    main()
