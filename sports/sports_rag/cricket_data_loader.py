import json
import os
from typing import List, Dict
from collections import defaultdict

def load_cricket_match(file_path: str) -> str:
    """
    Load and format a cricket match JSON file into a text format suitable for RAG.
    """
    with open(file_path, 'r') as f:
        match_data = json.load(f)
    
    # Initialize formatted text
    formatted_text = []
    
    # Match Info
    info = match_data.get('info', {})
    teams = info.get('teams', ['Team A', 'Team B'])
    formatted_text.append(f"Match Analysis: {teams[0]} vs {teams[1]}")
    formatted_text.append(f"Date: {info.get('dates', ['Unknown'])[0]}")
    formatted_text.append(f"Venue: {info.get('venue', 'Unknown')}")
    formatted_text.append(f"Event: {info.get('event', {}).get('name', 'Unknown')}")
    formatted_text.append(f"Match Type: {info.get('match_type', 'Unknown')}")
    formatted_text.append(f"Gender: {info.get('gender', 'Unknown')}")
    formatted_text.append(f"Season: {info.get('season', 'Unknown')}")
    formatted_text.append("")
    
    # Teams and Players
    for team in teams:
        players = info.get('players', {}).get(team, [])
        formatted_text.append(f"{team} Playing XI:")
        for player in players:
            formatted_text.append(f"- {player}")
        formatted_text.append("")
    
    # Match Details
    if 'toss' in info:
        formatted_text.append(f"Toss: {info['toss'].get('winner', 'Unknown')} won and chose to {info['toss'].get('decision', 'Unknown')}")
    
    # Officials
    if 'officials' in info:
        officials = info['officials']
        if 'umpires' in officials:
            formatted_text.append(f"Umpires: {', '.join(officials['umpires'])}")
        if 'match_referees' in officials:
            formatted_text.append(f"Match Referees: {', '.join(officials['match_referees'])}")
    formatted_text.append("")
    
    # Innings Analysis
    match_stats = {
        'total_runs': 0,
        'total_wickets': 0,
        'total_fours': 0,
        'total_sixes': 0,
        'total_extras': 0,
        'total_balls': 0
    }
    
    if 'innings' in match_data:
        for inning_num, inning in enumerate(match_data['innings'], 1):
            batting_team = inning.get('team', 'Unknown')
            formatted_text.append(f"Innings {inning_num}: {batting_team}")
            
            # Initialize innings statistics
            innings_stats = defaultdict(int)
            batsmen_stats = defaultdict(lambda: {
                'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'strike_rate': 0.0,
                'vs_bowlers': defaultdict(lambda: {
                    'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dots': 0,
                    'dismissals': 0, 'strike_rate': 0.0
                })
            })
            bowler_stats = defaultdict(lambda: {
                'overs': 0, 'maidens': 0, 'runs': 0, 'wickets': 0, 'economy': 0.0,
                'vs_batters': defaultdict(lambda: {
                    'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dots': 0,
                    'wickets': 0, 'economy': 0.0
                })
            })
            fielder_stats = defaultdict(lambda: {
                'catches': 0, 'stumpings': 0, 'run_outs': 0,
                'catches_by_position': defaultdict(int),
                'run_outs_by_position': defaultdict(int)
            })
            
            # Partnership tracking
            partnership_stats = []
            current_partnership = {
                'batters': [], 'runs': 0, 'balls': 0,
                'fours': 0, 'sixes': 0, 'dots': 0,
                'start_score': 0, 'end_score': 0,
                'overs': [], 'vs_bowlers': defaultdict(lambda: {
                    'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'dots': 0
                })
            }
            
            # Track current batters and phase of play
            current_batters = set()
            match_phase = 'powerplay' if 0 < 6 else 'middle' if 0 < 16 else 'death'
            
            # Process each over
            for over_data in inning.get('overs', []):
                over_num = over_data.get('over', 0)
                over_stats = {
                    'over_number': over_num + 1,
                    'runs': 0, 'wickets': 0,
                    'boundaries': {'fours': 0, 'sixes': 0},
                    'extras': 0, 'dots': 0,
                    'balls': 0, 'valid_balls': 0,
                    'partnerships': []
                }
                
                # Update match phase
                match_phase = 'powerplay' if over_num < 6 else 'middle' if over_num < 16 else 'death'
                
                # Process each delivery
                for delivery in over_data.get('deliveries', []):
                    over_stats['balls'] += 1
                    match_stats['total_balls'] += 1
                    
                    # Get delivery details
                    batter = delivery.get('batter', 'Unknown')
                    bowler = delivery.get('bowler', 'Unknown')
                    non_striker = delivery.get('non_striker', 'Unknown')
                    
                    # Update current batters and partnership
                    if not current_partnership['batters']:
                        current_partnership['batters'] = [batter, non_striker]
                        current_partnership['start_score'] = 0
                    current_batters.update([batter, non_striker])
                    
                    # Calculate runs
                    runs_info = delivery.get('runs', {})
                    batter_runs = runs_info.get('batter', 0)
                    extras = runs_info.get('extras', 0)
                    total_runs = runs_info.get('total', 0)
                    
                    # Track extras
                    extras_detail = delivery.get('extras', {})
                    is_wide = 'wides' in extras_detail
                    is_noball = 'noballs' in extras_detail
                    is_valid_ball = not (is_wide or is_noball)
                    is_dot_ball = total_runs == 0 and is_valid_ball
                    
                    # Update valid balls count
                    if is_valid_ball:
                        over_stats['valid_balls'] += 1
                    
                    # Update dot ball statistics
                    if is_dot_ball:
                        over_stats['dots'] += 1
                        batsmen_stats[batter]['vs_bowlers'][bowler]['dots'] += 1
                        bowler_stats[bowler]['vs_batters'][batter]['dots'] += 1
                        current_partnership['dots'] += 1
                        current_partnership['vs_bowlers'][bowler]['dots'] += 1
                    
                    # Update partnership statistics
                    current_partnership['runs'] += total_runs
                    current_partnership['balls'] += 1 if is_valid_ball else 0
                    current_partnership['vs_bowlers'][bowler]['runs'] += total_runs
                    current_partnership['vs_bowlers'][bowler]['balls'] += 1 if is_valid_ball else 0
                    
                    # Update batter vs bowler statistics
                    if is_valid_ball:
                        batsmen_stats[batter]['vs_bowlers'][bowler]['balls'] += 1
                        batsmen_stats[batter]['vs_bowlers'][bowler]['runs'] += batter_runs
                        bowler_stats[bowler]['vs_batters'][batter]['balls'] += 1
                        bowler_stats[bowler]['vs_batters'][batter]['runs'] += batter_runs
                    
                    # Track boundaries in partnership
                    if batter_runs == 4:
                        current_partnership['fours'] += 1
                        current_partnership['vs_bowlers'][bowler]['fours'] += 1
                        batsmen_stats[batter]['vs_bowlers'][bowler]['fours'] += 1
                        bowler_stats[bowler]['vs_batters'][batter]['fours'] += 1
                    elif batter_runs == 6:
                        current_partnership['sixes'] += 1
                        current_partnership['vs_bowlers'][bowler]['sixes'] += 1
                        batsmen_stats[batter]['vs_bowlers'][bowler]['sixes'] += 1
                        bowler_stats[bowler]['vs_batters'][batter]['sixes'] += 1
                    
                    # Process wickets and update partnership
                    if 'wickets' in delivery:
                        for wicket in delivery['wickets']:
                            player_out = wicket.get('player_out', 'Unknown')
                            dismissal_type = wicket.get('kind', 'Unknown')
                            
                            # Update batter vs bowler dismissal stats
                            if dismissal_type not in ['run out', 'retired hurt']:
                                batsmen_stats[player_out]['vs_bowlers'][bowler]['dismissals'] += 1
                                bowler_stats[bowler]['vs_batters'][player_out]['wickets'] += 1
                            
                            # Handle fielding contributions
                            if 'fielders' in wicket:
                                fielders = [f for f in wicket.get('fielders', [])]
                                for fielder_info in fielders:
                                    fielder_name = fielder_info.get('name', 'Unknown')
                                    fielder_position = fielder_info.get('position', 'Unknown')
                                    
                                    if dismissal_type == 'caught':
                                        if fielder_name == fielders[0].get('name', 'Unknown'):  # Primary catcher
                                            fielder_stats[fielder_name]['catches'] += 1
                                            fielder_stats[fielder_name]['catches_by_position'][fielder_position] += 1
                                    elif dismissal_type == 'stumped':
                                        fielder_stats[fielder_name]['stumpings'] += 1
                                    elif dismissal_type == 'run out':
                                        fielder_stats[fielder_name]['run_outs'] += 1
                                        fielder_stats[fielder_name]['run_outs_by_position'][fielder_position] += 1
                # Calculate over summary
                over_stats.update({
                    'running_total': 0,
                    'running_wickets': 0,
                    'run_rate': (0 * 6.0) / ((over_num + 1) * 6) if over_num >= 0 else 0,
                    'this_over_run_rate': (over_stats['runs'] * 6.0) / max(over_stats['valid_balls'], 1)
                })
                
                # Update bowler statistics
                bowler_stats[bowler]['overs'] = over_num + 1
                bowler_stats[bowler]['runs'] += over_stats['runs']
                if over_stats['runs'] == 0 and over_stats['valid_balls'] == 6:
                    bowler_stats[bowler]['maidens'] += 1
            
            # Calculate strike rates for batsmen
            for batter, stats in batsmen_stats.items():
                if stats['balls'] > 0:
                    stats['strike_rate'] = (stats['runs'] * 100.0) / stats['balls']
            
            # Calculate economy rates for bowlers
            for bowler, stats in bowler_stats.items():
                if stats['overs'] > 0:
                    stats['economy'] = stats['runs'] / stats['overs']
            
            # Innings Summary
            formatted_text.append(f"\nInnings Summary for {batting_team}:")
            formatted_text.append(f"Total Score: {innings_stats['runs']}/{innings_stats['wickets']}")
            if 0 < 1:
                formatted_text.append(f"Run Rate: {0:.2f}")
            
            # Add detailed over-by-over analysis
            formatted_text.append("\nDetailed Over-by-Over Analysis:")
            for over_stats in []:
                over_num = over_stats['over_number']
                formatted_text.append(
                    f"Over {over_num}: {over_stats['runs']} runs ({over_stats['extras']} extras), "
                    f"{over_stats['wickets']} wickets, "
                    f"{over_stats['boundaries']['fours']} fours, {over_stats['boundaries']['sixes']} sixes | "
                    f"Score: {over_stats['running_total']}/{over_stats['running_wickets']} "
                    f"(Over RR: {over_stats['this_over_run_rate']:.2f}, Match RR: {over_stats['run_rate']:.2f})"
                )
            
            # Add phase analysis
            if len([]) >= 6:  # Only add if at least powerplay overs are completed
                powerplay_stats = [][:6]
                powerplay_runs = sum(over['runs'] for over in powerplay_stats)
                powerplay_wickets = sum(over['wickets'] for over in powerplay_stats)
                powerplay_fours = sum(over['boundaries']['fours'] for over in powerplay_stats)
                powerplay_sixes = sum(over['boundaries']['sixes'] for over in powerplay_stats)
                powerplay_balls = sum(over['valid_balls'] for over in powerplay_stats)
                
                formatted_text.append("\nPowerplay Analysis (First 6 overs):")
                formatted_text.append(
                    f"Runs: {powerplay_runs}, Wickets: {powerplay_wickets}, "
                    f"Run Rate: {(powerplay_runs * 6.0) / powerplay_balls:.2f}, "
                    f"Boundaries: {powerplay_fours} fours, {powerplay_sixes} sixes"
                )
            
            # Add partnership analysis
            if partnership_stats:
                formatted_text.append("\nPartnership Analysis:")
                for i, p in enumerate(partnership_stats, 1):
                    runs = p['runs']
                    balls = p['balls']
                    run_rate = (runs * 6.0) / max(balls, 1)
                    boundary_rate = ((p['fours'] + p['sixes']) * 100.0) / max(balls, 1)
                    
                    formatted_text.append(
                        f"\n{i}. {' & '.join(p['batters'])}"
                        f"\nRuns: {runs} ({balls} balls, RR: {run_rate:.2f})"
                        f"\nBoundaries: {p['fours']} fours, {p['sixes']} sixes ({boundary_rate:.1f}% boundary rate)"
                        f"\nDot Balls: {p['dots']} ({(p['dots'] * 100.0) / max(balls, 1):.1f}%)"
                    )
                    
                    # Add bowler-wise breakdown for significant partnerships (>20 runs)
                    if runs >= 20:
                        formatted_text.append("vs Bowlers:")
                        for bowler, stats in p['vs_bowlers'].items():
                            if stats['balls'] > 0:
                                bowler_rr = (stats['runs'] * 6.0) / stats['balls']
                                formatted_text.append(
                                    f"  {bowler}: {stats['runs']}/{stats['balls']} balls "
                                    f"(RR: {bowler_rr:.2f}, "
                                    f"Boundaries: {stats['fours']}x4 {stats['sixes']}x6, "
                                    f"Dots: {stats['dots']})"
                                )
            
            # Add batter vs bowler analysis
            formatted_text.append("\nBatter vs Bowler Analysis:")
            for batter in batsmen_stats:
                if any(stats['balls'] > 0 for stats in batsmen_stats[batter]['vs_bowlers'].values()):
                    formatted_text.append(f"\n{batter} against:")
                    for bowler, stats in batsmen_stats[batter]['vs_bowlers'].items():
                        if stats['balls'] > 0:
                            sr = (stats['runs'] * 100.0) / stats['balls']
                            boundary_pc = ((stats['fours'] + stats['sixes']) * 100.0) / stats['balls']
                            formatted_text.append(
                                f"  {bowler}: {stats['runs']} runs ({stats['balls']} balls, "
                                f"SR: {sr:.1f}, "
                                f"Boundaries: {stats['fours']}x4 {stats['sixes']}x6 ({boundary_pc:.1f}%), "
                                f"Dots: {stats['dots']} ({(stats['dots'] * 100.0) / stats['balls']:.1f}%)"
                                + (f", Dismissed {stats['dismissals']} time(s)" if stats['dismissals'] > 0 else "")
                            )
            
            # Batting Statistics
            formatted_text.append("\nBatting Statistics:")
            for batter, stats in batsmen_stats.items():
                formatted_text.append(f"{batter}: {stats['runs']} runs ({stats['balls']} balls, "
                                   f"{stats['fours']} fours, {stats['sixes']} sixes, "
                                   f"SR: {stats['strike_rate']:.2f})")
            
            # Bowling Statistics
            formatted_text.append("\nBowling Statistics:")
            for bowler, stats in bowler_stats.items():
                formatted_text.append(f"{bowler}: {stats['wickets']}/{stats['runs']} "
                                   f"({stats['overs']} overs, {stats['maidens']} maidens, "
                                   f"Econ: {stats['economy']:.2f})")
            
            # Wicket Analysis
            if any(stats['wickets'] > 0 for stats in bowler_stats.values()):
                formatted_text.append("\nWicket Analysis:")
                total_wickets = sum(stats['wickets'] for stats in bowler_stats.values())
                for bowler, stats in bowler_stats.items():
                    if stats['wickets'] > 0:
                        percentage = (stats['wickets'] * 100.0) / total_wickets
                        formatted_text.append(f"{bowler}: {stats['wickets']} ({percentage:.1f}%)")
            
            # Fielding Analysis
            if any(stats['catches'] + stats['stumpings'] + stats['run_outs'] > 0 
                  for stats in fielder_stats.values()):
                formatted_text.append("\nFielding Analysis:")
                for fielder, stats in fielder_stats.items():
                    if stats['catches'] + stats['stumpings'] + stats['run_outs'] > 0:
                        contributions = []
                        
                        # Catches with position breakdown
                        if stats['catches'] > 0:
                            catch_details = []
                            for position, count in stats['catches_by_position'].items():
                                catch_details.append(f"{count} at {position}")
                            contributions.append(
                                f"{stats['catches']} catch{'es' if stats['catches'] > 1 else ''} "
                                f"({', '.join(catch_details)})"
                            )
                        
                        # Stumpings
                        if stats['stumpings'] > 0:
                            contributions.append(
                                f"{stats['stumpings']} stumping{'s' if stats['stumpings'] > 1 else ''}"
                            )
                        
                        # Run outs with position breakdown
                        if stats['run_outs'] > 0:
                            runout_details = []
                            for position, count in stats['run_outs_by_position'].items():
                                runout_details.append(f"{count} from {position}")
                            contributions.append(
                                f"{stats['run_outs']} run out{'s' if stats['run_outs'] > 1 else ''} "
                                f"({', '.join(runout_details)})"
                            )
                        
                        formatted_text.append(f"{fielder}: {', '.join(contributions)}")
    
    # Match Summary
    formatted_text.append("\nMatch Summary:")
    formatted_text.append(f"Total Runs Scored: {match_stats['total_runs']}")
    formatted_text.append(f"Total Wickets: {match_stats['total_wickets']}")
    formatted_text.append(f"Total Boundaries: {match_stats['total_fours']} fours, {match_stats['total_sixes']} sixes")
    formatted_text.append(f"Total Extras: {match_stats['total_extras']}")
    
    # Result
    if 'outcome' in info:
        outcome = info['outcome']
        if 'winner' in outcome:
            formatted_text.append(f"\nResult: {outcome['winner']} won")
            if 'by' in outcome:
                margin = outcome['by']
                margin_text = ', '.join(f"by {value} {key}" for key, value in margin.items())
                formatted_text.append(f"Margin: {margin_text}")
            if 'method' in outcome:
                formatted_text.append(f"Method: {outcome['method']}")
        elif 'result' in outcome:
            formatted_text.append(f"\nResult: {outcome['result']}")
    
    return '\n'.join(formatted_text)

def process_all_matches(data_dir: str) -> List[Dict[str, str]]:
    """
    Process all cricket match JSON files in the data directory.
    Returns a list of dictionaries containing the match text and metadata.
    """
    matches = []
    
    # Process all JSON files in the directory
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(data_dir, filename)
            try:
                # Load and process the match
                match_text = load_cricket_match(file_path)
                
                # Create metadata
                with open(file_path, 'r') as f:
                    match_data = json.load(f)
                
                metadata = {
                    'filename': filename,
                    'match_id': os.path.splitext(filename)[0],
                    'teams': match_data.get('info', {}).get('teams', []),
                    'date': match_data.get('info', {}).get('dates', ['Unknown'])[0],
                    'venue': match_data.get('info', {}).get('venue', 'Unknown'),
                    'event': match_data.get('info', {}).get('event', {}).get('name', 'Unknown')
                }
                
                matches.append({
                    'text': match_text,
                    'metadata': metadata
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    return matches
