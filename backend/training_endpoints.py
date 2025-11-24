"""
Training & Coaching Endpoints for GR-Pilot
Advanced driver improvement and learning features
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime

router = APIRouter(prefix="/api/training", tags=["training"])

# Import existing utilities (will be added to main.py)
# from main import load_telemetry, load_lap_times

class SkillScore(BaseModel):
    category: str
    score: float
    max_score: float
    rating: str
    description: str

class TrainingDrill(BaseModel):
    id: str
    name: str
    description: str
    duration_minutes: int
    difficulty: str
    target_skills: List[str]

class CoachingCue(BaseModel):
    location: str
    corner: Optional[str]
    message: str
    priority: str
    expected_gain_seconds: float
    visual_marker: Dict[str, Any]

class Scenario(BaseModel):
    id: str
    name: str
    description: str
    difficulty: str
    stars_achieved: int
    is_locked: bool
    requirements: Optional[str]

def calculate_skill_scores(telemetry_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate comprehensive skill scores across 8 categories.
    Returns normalized scores (0-100).
    """
    scores = {}

    # 1. Braking Precision
    if 'pbrake_f' in telemetry_df.columns:
        brake_data = telemetry_df['pbrake_f'].dropna()
        if len(brake_data) > 0:
            # Analyze braking consistency and modulation
            brake_events = brake_data[brake_data > 10]
            if len(brake_events) > 0:
                brake_std = brake_events.std()
                brake_smoothness = max(0, 100 - brake_std * 2)
                scores['braking_precision'] = min(100, brake_smoothness)
            else:
                scores['braking_precision'] = 50
        else:
            scores['braking_precision'] = 50
    else:
        scores['braking_precision'] = 50

    # 2. Throttle Control
    if 'ath' in telemetry_df.columns:
        throttle_data = telemetry_df['ath'].dropna()
        if len(throttle_data) > 0:
            throttle_changes = throttle_data.diff().abs().mean()
            throttle_smoothness = max(0, 100 - throttle_changes * 5)
            scores['throttle_control'] = min(100, throttle_smoothness)
        else:
            scores['throttle_control'] = 50
    else:
        scores['throttle_control'] = 50

    # 3. Racing Line Accuracy (based on speed consistency)
    if 'speed' in telemetry_df.columns:
        speed_data = telemetry_df['speed'].dropna()
        if len(speed_data) > 0:
            speed_cv = (speed_data.std() / speed_data.mean()) * 100 if speed_data.mean() > 0 else 50
            line_accuracy = max(0, 100 - speed_cv)
            scores['racing_line'] = min(100, line_accuracy)
        else:
            scores['racing_line'] = 50
    else:
        scores['racing_line'] = 50

    # 4. Consistency Index
    if 'speed' in telemetry_df.columns and 'ath' in telemetry_df.columns:
        speed_consistency = telemetry_df['speed'].rolling(window=10).std().mean()
        throttle_consistency = telemetry_df['ath'].rolling(window=10).std().mean()
        consistency = max(0, 100 - (speed_consistency + throttle_consistency))
        scores['consistency'] = min(100, consistency)
    else:
        scores['consistency'] = 50

    # 5. Tire Preservation (based on lateral G and speed variance)
    if 'accy_can' in telemetry_df.columns:
        lateral_g = telemetry_df['accy_can'].abs().dropna()
        if len(lateral_g) > 0:
            aggressive_corners = (lateral_g > 1.5).sum()
            total_corners = len(lateral_g)
            preservation = max(0, 100 - (aggressive_corners / total_corners * 200)) if total_corners > 0 else 50
            scores['tire_preservation'] = min(100, preservation)
        else:
            scores['tire_preservation'] = 50
    else:
        scores['tire_preservation'] = 50

    # 6. Corner Speed Optimization
    if 'speed' in telemetry_df.columns and 'Steering_Angle' in telemetry_df.columns:
        steering = telemetry_df['Steering_Angle'].abs().dropna()
        speed = telemetry_df['speed'].dropna()
        if len(steering) > 0 and len(speed) > 0:
            corner_mask = steering > 50
            if corner_mask.sum() > 0:
                avg_corner_speed = speed[corner_mask].mean()
                avg_straight_speed = speed[~corner_mask].mean() if (~corner_mask).sum() > 0 else 100
                speed_ratio = (avg_corner_speed / avg_straight_speed * 100) if avg_straight_speed > 0 else 50
                scores['corner_speed'] = min(100, speed_ratio * 1.5)
            else:
                scores['corner_speed'] = 50
        else:
            scores['corner_speed'] = 50
    else:
        scores['corner_speed'] = 50

    # 7. Sector Optimization (placeholder - requires sector data)
    scores['sector_optimization'] = np.random.uniform(60, 85)  # TODO: Implement with sector data

    # 8. Focus & Concentration (based on input stability)
    if 'Steering_Angle' in telemetry_df.columns:
        steering = telemetry_df['Steering_Angle'].dropna()
        if len(steering) > 0:
            steering_corrections = (steering.diff().abs() > 5).sum()
            correction_rate = steering_corrections / len(steering) * 1000 if len(steering) > 0 else 0
            focus = max(0, 100 - correction_rate)
            scores['focus'] = min(100, focus)
        else:
            scores['focus'] = 50
    else:
        scores['focus'] = 50

    return scores

@router.get("/skill_assessment/{lap}")
async def get_skill_assessment(lap: int):
    """
    Endpoint 1: Comprehensive skill assessment for a given lap.
    Returns radar chart data with 8 skill categories.
    """
    try:
        # Load telemetry (placeholder - integrate with main.py's load function)
        from main import load_telemetry
        telemetry_df = load_telemetry()

        if telemetry_df is None or telemetry_df.empty:
            raise HTTPException(status_code=404, detail="Telemetry data not available")

        # Filter for specific lap
        lap_data = telemetry_df[telemetry_df['lap'] == lap]

        if lap_data.empty:
            raise HTTPException(status_code=404, detail=f"Lap {lap} not found")

        # Calculate skill scores
        scores = calculate_skill_scores(lap_data)

        # Generate skill details
        skills = []
        skill_descriptions = {
            'braking_precision': 'Brake modulation and consistency',
            'throttle_control': 'Smooth throttle application',
            'racing_line': 'Optimal path through corners',
            'consistency': 'Lap-to-lap repeatability',
            'tire_preservation': 'Gentle on tire wear',
            'corner_speed': 'Maintaining speed through turns',
            'sector_optimization': 'Time efficiency per sector',
            'focus': 'Mental concentration and stability'
        }

        for category, score in scores.items():
            rating = 'Excellent' if score >= 85 else 'Good' if score >= 70 else 'Average' if score >= 50 else 'Needs Work'
            skills.append({
                'category': category.replace('_', ' ').title(),
                'score': round(score, 1),
                'max_score': 100,
                'rating': rating,
                'description': skill_descriptions.get(category, '')
            })

        # Calculate overall rating
        avg_score = np.mean(list(scores.values()))
        overall_rating = 'Elite' if avg_score >= 85 else 'Advanced' if avg_score >= 70 else 'Intermediate' if avg_score >= 50 else 'Developing'

        return {
            'lap': lap,
            'overall_score': round(avg_score, 1),
            'overall_rating': overall_rating,
            'skills': skills,
            'strengths': sorted(skills, key=lambda x: x['score'], reverse=True)[:3],
            'weaknesses': sorted(skills, key=lambda x: x['score'])[:3],
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating skill assessment: {str(e)}")

@router.get("/benchmark/{lap}/vs/{reference_type}")
async def get_benchmark_comparison(lap: int, reference_type: str):
    """
    Endpoint 2: Compare lap against various benchmarks.
    reference_type: 'personal_best' | 'track_record' | 'perfect' | 'peer'
    """
    try:
        from main import load_telemetry, load_lap_times

        telemetry_df = load_telemetry()
        lap_times_df = load_lap_times()

        if telemetry_df is None or lap_times_df is None:
            raise HTTPException(status_code=404, detail="Data not available")

        # Get current lap time (column is 'value' not 'lap_time')
        current_lap_time = lap_times_df[lap_times_df['lap'] == lap]['value'].values
        if len(current_lap_time) == 0:
            raise HTTPException(status_code=404, detail=f"Lap {lap} not found")

        current_lap_time = current_lap_time[0]

        # Get reference lap time based on type
        if reference_type == 'personal_best':
            reference_lap = lap_times_df['value'].idxmin()
            reference_time = float(lap_times_df['value'].min())
            reference_lap_num = int(lap_times_df.loc[reference_lap, 'lap'])
            reference_name = f"Your Best Lap {reference_lap_num}"
        elif reference_type == 'track_record':
            reference_lap = lap_times_df['value'].idxmin()
            reference_time = float(lap_times_df['value'].min() * 0.98)  # Simulate track record
            reference_name = "Track Record (Simulated)"
        elif reference_type == 'perfect':
            reference_time = float(lap_times_df['value'].min() * 0.95)  # Perfect lap simulation
            reference_name = "Perfect Lap (Theoretical)"
        else:  # peer
            reference_time = float(lap_times_df['value'].median())
            reference_name = "Average Competitor"

        delta = current_lap_time - reference_time
        percentage_diff = (delta / reference_time * 100) if reference_time > 0 else 0

        # Calculate micro-sector deltas (50 segments)
        lap_data = telemetry_df[telemetry_df['lap'] == lap]

        micro_sectors = []
        if not lap_data.empty:
            num_segments = min(50, len(lap_data))
            segment_size = len(lap_data) // num_segments if num_segments > 0 else 1

            for i in range(num_segments):
                start_idx = i * segment_size
                end_idx = min((i + 1) * segment_size, len(lap_data))
                segment = lap_data.iloc[start_idx:end_idx]

                # Simulate delta (would be real comparison in production)
                segment_delta = np.random.uniform(-0.05, 0.05) * (1 + i * 0.01)

                micro_sectors.append({
                    'segment': i + 1,
                    'delta_seconds': round(segment_delta, 3),
                    'cumulative_delta': round(segment_delta * (i + 1) / 10, 3),
                    'status': 'faster' if segment_delta < 0 else 'slower'
                })
        else:
            # If no telemetry data for this lap, create simulated micro-sectors
            for i in range(50):
                segment_delta = np.random.uniform(-0.1, 0.1)
                micro_sectors.append({
                    'segment': i + 1,
                    'delta_seconds': round(segment_delta, 3),
                    'cumulative_delta': round(segment_delta * (i + 1) / 10, 3),
                    'status': 'faster' if segment_delta < 0 else 'slower'
                })

        return {
            'lap': int(lap),
            'current_lap_time': round(float(current_lap_time), 3),
            'reference_type': reference_type,
            'reference_name': reference_name,
            'reference_time': round(float(reference_time), 3),
            'delta': round(float(delta), 3),
            'percentage_difference': round(float(percentage_diff), 2),
            'micro_sectors': micro_sectors,
            'overall_status': 'faster' if delta < 0 else 'slower',
            'areas_to_improve': [
                {
                    'sector': f"Segment {s['segment']}",
                    'time_loss': s['delta_seconds']
                }
                for s in sorted(micro_sectors, key=lambda x: x['delta_seconds'], reverse=True)[:5]
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in benchmark comparison: {str(e)}")

@router.post("/practice_plan")
async def generate_practice_plan(lap: int):
    """
    Endpoint 3: Generate personalized practice plan based on skill assessment.
    """
    try:
        # Get skill assessment first
        skill_data = await get_skill_assessment(lap)

        weaknesses = skill_data['weaknesses']
        strengths = skill_data['strengths']

        # Generate drills for top 3 weaknesses
        drills = []
        drill_templates = {
            'braking_precision': {
                'name': 'Brake Point Mastery',
                'description': 'Practice consistent brake markers. Focus on hitting the same point ±2m for 5 consecutive laps.',
                'duration': 20,
                'difficulty': 'Medium'
            },
            'throttle_control': {
                'name': 'Smooth Throttle Application',
                'description': 'Work on progressive throttle inputs. Avoid sudden throttle spikes. Aim for smooth acceleration curves.',
                'duration': 15,
                'difficulty': 'Easy'
            },
            'racing_line': {
                'name': 'Apex Hunter',
                'description': 'Focus on hitting every apex. Use reference points and visual markers. Record and review onboard footage.',
                'duration': 25,
                'difficulty': 'Hard'
            },
            'consistency': {
                'name': 'Consistency Challenge',
                'description': 'Complete 10 laps within 0.5s of each other. Focus on repeatability over raw speed.',
                'duration': 30,
                'difficulty': 'Medium'
            },
            'tire_preservation': {
                'name': 'Tire Saving Mode',
                'description': 'Practice gentle steering inputs and smooth weight transfer. Monitor tire temperatures.',
                'duration': 20,
                'difficulty': 'Medium'
            },
            'corner_speed': {
                'name': 'Minimum Speed Challenge',
                'description': 'Focus on carrying more speed through corners. Work on later braking and earlier throttle.',
                'duration': 25,
                'difficulty': 'Hard'
            },
            'focus': {
                'name': 'Mental Stamina Session',
                'description': 'Long stint practice. Maintain concentration for 20+ laps. Notice when focus drops.',
                'duration': 40,
                'difficulty': 'Hard'
            }
        }

        for idx, weakness in enumerate(weaknesses):
            category_key = weakness['category'].lower().replace(' ', '_')
            template = drill_templates.get(category_key, {
                'name': f"Improve {weakness['category']}",
                'description': f"Focus training on {weakness['category']} skills",
                'duration': 20,
                'difficulty': 'Medium'
            })

            drills.append({
                'id': f"drill_{idx + 1}",
                'name': template['name'],
                'description': template['description'],
                'duration_minutes': template['duration'],
                'difficulty': template['difficulty'],
                'target_skills': [weakness['category']],
                'current_level': round(weakness['score'], 1),
                'target_level': min(100, round(weakness['score'] + 15, 1)),
                'priority': 'High' if idx == 0 else 'Medium'
            })

        # Estimate time to improvement
        avg_weakness_score = np.mean([w['score'] for w in weaknesses])
        weeks_to_improve = max(2, int((85 - avg_weakness_score) / 5))

        return {
            'lap': lap,
            'overall_level': skill_data['overall_rating'],
            'plan_generated': datetime.now().isoformat(),
            'drills': drills,
            'estimated_weeks_to_improvement': weeks_to_improve,
            'focus_areas': [w['category'] for w in weaknesses],
            'strengths_to_maintain': [s['category'] for s in strengths],
            'recommended_session_frequency': '3-4 sessions per week',
            'total_weekly_hours': sum(d['duration_minutes'] for d in drills) * 3 / 60
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating practice plan: {str(e)}")

@router.get("/live_coaching/{lap}")
async def get_live_coaching(lap: int):
    """
    Endpoint 4: Real-time coaching insights for a lap.
    Returns corner-by-corner advice.
    """
    try:
        from main import load_telemetry

        telemetry_df = load_telemetry()
        lap_data = telemetry_df[telemetry_df['lap'] == lap]

        if lap_data.empty:
            raise HTTPException(status_code=404, detail=f"Lap {lap} not found")

        # Identify corners (high steering angle zones)
        corners = []
        if 'Steering_Angle' in lap_data.columns:
            steering = lap_data['Steering_Angle'].abs()
            corner_threshold = 50

            in_corner = False
            corner_start = 0

            for idx, angle in enumerate(steering):
                if angle > corner_threshold and not in_corner:
                    in_corner = True
                    corner_start = idx
                elif angle <= corner_threshold and in_corner:
                    in_corner = False
                    corners.append({
                        'start': corner_start,
                        'end': idx,
                        'duration': idx - corner_start
                    })

        # Generate coaching cues for corners
        coaching_cues = []
        cue_templates = [
            "Brake {offset}m {direction} for better entry",
            "Carry {speed} more speed through apex",
            "Earlier throttle application - potential {gain}s gain",
            "Smoother steering input needed - {corrections} corrections detected",
            "Trail braking opportunity - reduce {reduction}% brake pressure gradually"
        ]

        for i, corner in enumerate(corners[:10]):  # Top 10 corners
            # Simulate coaching insights
            advice_type = np.random.choice(['braking', 'speed', 'throttle', 'steering', 'trail_brake'])

            if advice_type == 'braking':
                offset = np.random.randint(5, 15)
                direction = np.random.choice(['later', 'earlier'])
                message = f"Brake {offset}m {direction} for better entry"
                priority = 'high'
                gain = round(np.random.uniform(0.05, 0.2), 2)
            elif advice_type == 'speed':
                speed = np.random.randint(3, 8)
                message = f"Carry {speed} km/h more speed through apex"
                priority = 'medium'
                gain = round(np.random.uniform(0.1, 0.3), 2)
            elif advice_type == 'throttle':
                gain = round(np.random.uniform(0.08, 0.15), 2)
                message = f"Earlier throttle application - potential {gain}s gain"
                priority = 'high'
            elif advice_type == 'steering':
                corrections = np.random.randint(3, 8)
                message = f"Smoother steering input needed - {corrections} corrections detected"
                priority = 'medium'
                gain = round(np.random.uniform(0.03, 0.1), 2)
            else:  # trail_brake
                reduction = np.random.randint(10, 30)
                message = f"Trail braking opportunity - reduce {reduction}% brake pressure gradually"
                priority = 'low'
                gain = round(np.random.uniform(0.05, 0.12), 2)

            coaching_cues.append({
                'id': f"cue_{i + 1}",
                'location': f"Corner {i + 1}",
                'corner': f"Turn {i + 1}",
                'message': message,
                'priority': priority,
                'expected_gain_seconds': gain,
                'visual_marker': {
                    'type': 'corner',
                    'index': i
                },
                'category': advice_type
            })

        # Sort by priority and expected gain
        coaching_cues.sort(key=lambda x: (
            {'high': 0, 'medium': 1, 'low': 2}[x['priority']],
            -x['expected_gain_seconds']
        ))

        total_potential_gain = sum(c['expected_gain_seconds'] for c in coaching_cues)

        return {
            'lap': lap,
            'total_coaching_points': len(coaching_cues),
            'total_potential_gain_seconds': round(total_potential_gain, 2),
            'coaching_cues': coaching_cues,
            'summary': {
                'high_priority': len([c for c in coaching_cues if c['priority'] == 'high']),
                'medium_priority': len([c for c in coaching_cues if c['priority'] == 'medium']),
                'low_priority': len([c for c in coaching_cues if c['priority'] == 'low'])
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating coaching insights: {str(e)}")

@router.get("/learning_curve/{lap_start}/{lap_end}")
async def get_learning_curve(lap_start: int, lap_end: int):
    """
    Endpoint 5: Analyze learning progression across multiple laps.
    Shows improvement trajectory and plateau detection.
    """
    try:
        from main import load_lap_times

        lap_times_df = load_lap_times()

        if lap_times_df is None or lap_times_df.empty:
            raise HTTPException(status_code=404, detail="Lap times not available")

        # Filter lap range
        lap_range_df = lap_times_df[
            (lap_times_df['lap'] >= lap_start) &
            (lap_times_df['lap'] <= lap_end)
        ].copy()

        if lap_range_df.empty:
            raise HTTPException(status_code=404, detail="No laps in specified range")

        lap_range_df = lap_range_df.sort_values('lap')

        # Calculate learning metrics (column is 'value' not 'lap_time')
        lap_times = lap_range_df['value'].values
        laps = lap_range_df['lap'].values

        # Calculate moving average and trend
        window = min(5, len(lap_times))
        moving_avg = pd.Series(lap_times).rolling(window=window).mean().fillna(lap_times[0])

        # Calculate improvement rate
        if len(lap_times) > 1:
            improvement_rate = (lap_times[0] - lap_times[-1]) / len(lap_times)
        else:
            improvement_rate = 0

        # Detect plateaus (less than 0.1s improvement over 3 laps)
        plateaus = []
        for i in range(len(lap_times) - 3):
            improvement = lap_times[i] - lap_times[i + 3]
            if abs(improvement) < 0.1:
                plateaus.append({
                    'lap_start': int(laps[i]),
                    'lap_end': int(laps[i + 3]),
                    'average_time': round(float(np.mean(lap_times[i:i+4])), 3)
                })

        # Predict breakthrough
        best_time = float(lap_times.min())
        current_time = float(lap_times[-1])
        current_rate = abs(improvement_rate)

        if current_rate > 0:
            laps_to_breakthrough = int((current_time - best_time * 0.99) / current_rate)
        else:
            laps_to_breakthrough = 999

        # Learning stage classification
        total_improvement = float(lap_times[0] - lap_times[-1])
        if total_improvement > 2.0:
            learning_stage = "Rapid Improvement"
        elif total_improvement > 0.5:
            learning_stage = "Steady Progress"
        elif total_improvement > 0:
            learning_stage = "Fine-Tuning"
        else:
            learning_stage = "Plateau/Regression"

        return {
            'lap_range': {
                'start': int(lap_start),
                'end': int(lap_end),
                'total_laps': len(lap_times)
            },
            'learning_metrics': {
                'best_lap_time': round(best_time, 3),
                'worst_lap_time': round(float(lap_times.max()), 3),
                'average_lap_time': round(float(lap_times.mean()), 3),
                'total_improvement_seconds': round(total_improvement, 3),
                'improvement_rate_per_lap': round(improvement_rate, 4),
                'consistency_std': round(float(lap_times.std()), 3)
            },
            'learning_stage': learning_stage,
            'lap_data': [
                {
                    'lap': int(lap),
                    'lap_time': round(float(time), 3),
                    'moving_average': round(float(ma), 3),
                    'delta_from_best': round(float(time - best_time), 3)
                }
                for lap, time, ma in zip(laps, lap_times, moving_avg)
            ],
            'plateaus_detected': plateaus,
            'breakthrough_prediction': {
                'estimated_laps_to_next_pb': min(laps_to_breakthrough, 999),
                'predicted_best_time': round(best_time * 0.99, 3)
            },
            'recommendations': [
                "Focus on consistency - your lap time variance is high" if lap_times.std() > 1.0 else "Great consistency!",
                "Try different lines to break through plateau" if len(plateaus) > 0 else "Keep pushing!",
                "You're improving rapidly - maintain focus" if total_improvement > 1.0 else "Consider coaching session"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing learning curve: {str(e)}")

@router.get("/scenarios")
async def get_training_scenarios():
    """
    Endpoint 6: List available training scenarios with unlock status.
    """
    scenarios = [
        {
            'id': 'wet_weather',
            'name': 'Wet Weather Master',
            'description': 'Practice driving in low-grip conditions. Focus on smooth inputs and early braking.',
            'difficulty': 'Hard',
            'stars_achieved': 0,
            'max_stars': 3,
            'is_locked': False,
            'requirements': None,
            'objectives': [
                'Complete 5 laps without spinning',
                'Stay within 2s of dry weather best',
                'Maintain 90%+ throttle smoothness'
            ],
            'icon': 'cloud-rain'
        },
        {
            'id': 'traffic_management',
            'name': 'Traffic Master',
            'description': 'Navigate through slower cars while maintaining optimal pace.',
            'difficulty': 'Medium',
            'stars_achieved': 2,
            'max_stars': 3,
            'is_locked': False,
            'requirements': None,
            'objectives': [
                'Overtake 5 cars cleanly',
                'Maintain lap time within 105%',
                'Zero contact incidents'
            ],
            'icon': 'users'
        },
        {
            'id': 'tire_degradation',
            'name': 'Tire Whisperer',
            'description': 'Manage tire wear over a long stint. Adapt driving style as grip drops.',
            'difficulty': 'Hard',
            'stars_achieved': 1,
            'max_stars': 3,
            'is_locked': False,
            'requirements': None,
            'objectives': [
                'Complete 20-lap stint',
                'Final lap within 103% of first lap',
                'Tire stress score < 75%'
            ],
            'icon': 'circle-dot'
        },
        {
            'id': 'fuel_saving',
            'name': 'Fuel Strategist',
            'description': 'Balance speed with fuel efficiency. Hit target lap times while saving fuel.',
            'difficulty': 'Medium',
            'stars_achieved': 0,
            'max_stars': 3,
            'is_locked': False,
            'requirements': None,
            'objectives': [
                'Complete 10 laps with 15% fuel saving',
                'Stay within 102% of target pace',
                'Smooth throttle (>85% score)'
            ],
            'icon': 'gauge'
        },
        {
            'id': 'qualifying_sim',
            'name': 'Qualifying Hero',
            'description': 'Single-lap perfection. Push to the absolute limit on new tires.',
            'difficulty': 'Hard',
            'stars_achieved': 3,
            'max_stars': 3,
            'is_locked': False,
            'requirements': None,
            'objectives': [
                'Beat personal best by 0.5s',
                'Zero mistakes (anomaly-free)',
                'CPI score > 85'
            ],
            'icon': 'zap'
        },
        {
            'id': 'race_start',
            'name': 'Race Start Specialist',
            'description': 'Perfect the critical first 3 laps. Warm up tires and find rhythm.',
            'difficulty': 'Medium',
            'stars_achieved': 0,
            'max_stars': 3,
            'is_locked': True,
            'requirements': 'Complete Qualifying Hero',
            'objectives': [
                'Progressive lap time improvement',
                'Tire temps in optimal range',
                'Clean racing line'
            ],
            'icon': 'play'
        },
        {
            'id': 'defensive_driving',
            'name': 'Defensive Master',
            'description': 'Hold position against faster cars. Strategic blocking and positioning.',
            'difficulty': 'Hard',
            'stars_achieved': 0,
            'max_stars': 3,
            'is_locked': True,
            'requirements': 'Complete Traffic Master',
            'objectives': [
                'Hold position for 10 laps',
                'Force 3+ failed overtake attempts',
                'Maintain racing line 90%+'
            ],
            'icon': 'shield'
        },
        {
            'id': 'night_driving',
            'name': 'Night Vision',
            'description': 'Master limited visibility conditions. Trust your instincts and reference points.',
            'difficulty': 'Expert',
            'stars_achieved': 0,
            'max_stars': 3,
            'is_locked': True,
            'requirements': 'Achieve 80+ overall skill rating',
            'objectives': [
                'Complete 5 laps in dark conditions',
                'Within 103% of daylight pace',
                'Hit all apexes'
            ],
            'icon': 'moon'
        }
    ]

    return {
        'total_scenarios': len(scenarios),
        'completed_scenarios': len([s for s in scenarios if s['stars_achieved'] == s['max_stars']]),
        'total_stars': sum(s['stars_achieved'] for s in scenarios),
        'max_stars': sum(s['max_stars'] for s in scenarios),
        'scenarios': scenarios
    }

@router.get("/scenario/{scenario_id}/evaluate/{lap}")
async def evaluate_scenario_performance(scenario_id: str, lap: int):
    """
    Endpoint 7: Evaluate lap performance against scenario objectives.
    """
    try:
        from main import load_telemetry

        telemetry_df = load_telemetry()
        lap_data = telemetry_df[telemetry_df['lap'] == lap]

        if lap_data.empty:
            raise HTTPException(status_code=404, detail=f"Lap {lap} not found")

        # Get scenario details
        scenarios_response = await get_training_scenarios()
        scenario = next((s for s in scenarios_response['scenarios'] if s['id'] == scenario_id), None)

        if not scenario:
            raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

        # Simulate objective completion
        objectives_status = []
        stars_earned = 0

        for obj in scenario['objectives']:
            completed = np.random.choice([True, False], p=[0.6, 0.4])
            if completed:
                stars_earned += 1

            objectives_status.append({
                'objective': obj,
                'completed': completed,
                'progress': np.random.randint(60, 100) if completed else np.random.randint(30, 70)
            })

        return {
            'scenario_id': scenario_id,
            'scenario_name': scenario['name'],
            'lap': lap,
            'stars_earned': stars_earned,
            'max_stars': scenario['max_stars'],
            'objectives': objectives_status,
            'overall_completion': round(np.mean([o['progress'] for o in objectives_status]), 1),
            'feedback': [
                "Great job on smooth inputs!" if stars_earned >= 2 else "Focus on consistency",
                "Try braking a bit later" if stars_earned < 2 else "Excellent brake points",
                "Keep pushing!" if stars_earned == scenario['max_stars'] else "You're improving!"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating scenario: {str(e)}")

@router.get("/multi_compare")
async def multi_lap_compare(laps: str):
    """
    Endpoint 8: Compare 3+ laps simultaneously with statistical envelope.
    laps parameter format: "1,5,10,15"
    """
    try:
        from main import load_telemetry, load_lap_times

        # Parse lap numbers
        lap_list = [int(lap.strip()) for lap in laps.split(',')]

        if len(lap_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 laps required")

        telemetry_df = load_telemetry()
        lap_times_df = load_lap_times()

        # Collect lap data
        lap_comparisons = []
        for lap in lap_list:
            lap_data = telemetry_df[telemetry_df['lap'] == lap]
            lap_time = lap_times_df[lap_times_df['lap'] == lap]['lap_time'].values

            if not lap_data.empty and len(lap_time) > 0:
                avg_speed = lap_data['speed'].mean() if 'speed' in lap_data.columns else 0
                max_speed = lap_data['speed'].max() if 'speed' in lap_data.columns else 0

                lap_comparisons.append({
                    'lap': lap,
                    'lap_time': round(float(lap_time[0]), 3),
                    'avg_speed': round(float(avg_speed), 1),
                    'max_speed': round(float(max_speed), 1),
                    'data_points': len(lap_data)
                })

        if len(lap_comparisons) < 2:
            raise HTTPException(status_code=404, detail="Insufficient lap data found")

        # Calculate statistical envelope
        lap_times = [lc['lap_time'] for lc in lap_comparisons]
        avg_speeds = [lc['avg_speed'] for lc in lap_comparisons]

        envelope = {
            'best_lap_time': min(lap_times),
            'worst_lap_time': max(lap_times),
            'average_lap_time': round(np.mean(lap_times), 3),
            'std_deviation': round(np.std(lap_times), 3),
            'consistency_score': round((1 - np.std(lap_times) / np.mean(lap_times)) * 100, 1) if np.mean(lap_times) > 0 else 0,
            'speed_envelope': {
                'min': round(min(avg_speeds), 1),
                'max': round(max(avg_speeds), 1),
                'average': round(np.mean(avg_speeds), 1)
            }
        }

        # Improvement trajectory
        if len(lap_comparisons) > 2:
            first_lap_time = lap_comparisons[0]['lap_time']
            last_lap_time = lap_comparisons[-1]['lap_time']
            improvement = first_lap_time - last_lap_time

            trajectory = {
                'direction': 'improving' if improvement > 0 else 'regressing' if improvement < 0 else 'stable',
                'total_improvement_seconds': round(improvement, 3),
                'average_improvement_per_lap': round(improvement / len(lap_comparisons), 4)
            }
        else:
            trajectory = {'direction': 'insufficient_data'}

        return {
            'laps_compared': lap_list,
            'total_laps': len(lap_comparisons),
            'lap_data': lap_comparisons,
            'statistical_envelope': envelope,
            'improvement_trajectory': trajectory,
            'fastest_lap': min(lap_comparisons, key=lambda x: x['lap_time'])['lap'],
            'most_consistent_range': f"{min(lap_times):.3f}s - {max(lap_times):.3f}s"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in multi-lap comparison: {str(e)}")

@router.get("/predict_potential")
async def predict_ultimate_potential():
    """
    Endpoint 9: Predict driver's ultimate pace based on best sectors and improvement rate.
    """
    try:
        from main import load_lap_times

        lap_times_df = load_lap_times()

        if lap_times_df is None or lap_times_df.empty:
            raise HTTPException(status_code=404, detail="Lap times not available")

        # Get current best (column is 'value' not 'lap_time')
        current_best = lap_times_df['value'].min()

        # Calculate improvement rate (last 10 laps)
        recent_laps = lap_times_df.tail(10)
        if len(recent_laps) > 1:
            improvement_rate = (recent_laps['value'].iloc[0] - recent_laps['value'].iloc[-1]) / len(recent_laps)
        else:
            improvement_rate = 0

        # Predict ultimate pace (optimistic scenario)
        # Assume 95% of current best is theoretical limit
        theoretical_best = current_best * 0.97

        # Calculate time to reach based on improvement rate
        if improvement_rate > 0:
            laps_to_theoretical = int((current_best - theoretical_best) / improvement_rate)
        else:
            laps_to_theoretical = 999

        # Break down by skill areas
        focus_areas = [
            {
                'area': 'Braking Optimization',
                'current_lap_time_impact': '~0.3s',
                'potential_gain': '0.15s',
                'effort_required': 'Medium',
                'timeline': '2-3 weeks'
            },
            {
                'area': 'Corner Entry Speed',
                'current_lap_time_impact': '~0.4s',
                'potential_gain': '0.20s',
                'effort_required': 'High',
                'timeline': '3-4 weeks'
            },
            {
                'area': 'Throttle Timing',
                'current_lap_time_impact': '~0.2s',
                'potential_gain': '0.10s',
                'effort_required': 'Low',
                'timeline': '1-2 weeks'
            },
            {
                'area': 'Racing Line',
                'current_lap_time_impact': '~0.5s',
                'potential_gain': '0.25s',
                'effort_required': 'High',
                'timeline': '4-6 weeks'
            }
        ]

        total_potential_gain = sum(float(area['potential_gain'].replace('s', '')) for area in focus_areas)

        return {
            'current_best_lap': round(float(current_best), 3),
            'predicted_ultimate_pace': round(float(theoretical_best), 3),
            'total_potential_improvement': round(total_potential_gain, 3),
            'improvement_breakdown': focus_areas,
            'timeline_to_ultimate': {
                'optimistic': f"{laps_to_theoretical} laps (~{laps_to_theoretical // 20} sessions)",
                'realistic': f"{laps_to_theoretical * 2} laps (~{laps_to_theoretical // 10} sessions)",
                'pessimistic': f"{laps_to_theoretical * 3} laps (~{laps_to_theoretical // 7} sessions)"
            },
            'confidence_level': 'Medium' if improvement_rate > 0 else 'Low',
            'recommendations': [
                "Focus on high-impact areas first (Corner Entry, Racing Line)",
                "Track your progress weekly to adjust predictions",
                "Consider data logging for more accurate analysis",
                "Work with coach to accelerate improvement"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting potential: {str(e)}")

@router.get("/team/rankings")
async def get_team_rankings():
    """
    Endpoint 10: Team-wide skill rankings and benchmarking (simulated).
    """
    # Simulate team data
    team_members = [
        {'id': 1, 'name': 'You', 'overall_score': 72.5, 'best_lap': 95.234, 'total_laps': 156},
        {'id': 2, 'name': 'Driver A', 'overall_score': 78.3, 'best_lap': 94.122, 'total_laps': 203},
        {'id': 3, 'name': 'Driver B', 'overall_score': 68.9, 'best_lap': 96.445, 'total_laps': 142},
        {'id': 4, 'name': 'Driver C', 'overall_score': 81.2, 'best_lap': 93.876, 'total_laps': 189},
        {'id': 5, 'name': 'Driver D', 'overall_score': 74.1, 'best_lap': 95.001, 'total_laps': 167},
    ]

    # Sort by overall score
    team_members.sort(key=lambda x: x['overall_score'], reverse=True)

    for idx, member in enumerate(team_members):
        member['rank'] = idx + 1

    # Your ranking
    your_data = next(m for m in team_members if m['name'] == 'You')

    return {
        'team_size': len(team_members),
        'your_rank': your_data['rank'],
        'your_score': your_data['overall_score'],
        'team_average': round(np.mean([m['overall_score'] for m in team_members]), 1),
        'top_performer': team_members[0],
        'rankings': team_members,
        'skill_comparison': {
            'braking': {'your_score': 68, 'team_avg': 72, 'top_score': 85},
            'cornering': {'your_score': 75, 'team_avg': 71, 'top_score': 82},
            'consistency': {'your_score': 80, 'team_avg': 74, 'top_score': 88},
        },
        'improvement_opportunities': [
            "Focus on braking - you're below team average",
            "Great cornering - you're above team average!",
            "Excellent consistency - keep it up!"
        ]
    }
