"""
Pit Strategy Simulator
Real-time race strategy optimization

GERÇEK YARIŞ MÜHENDİSLİĞİ:
- Tire degradation modeling
- Fuel consumption calculation
- Undercut/Overcut scenarios
- Caution flag strategy
- Multi-stint optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PitStrategySimulator:
    """
    Pit stop stratejisi simülatörü

    Toyota TRD race engineers kullanır:
    - Real-time pit window calculation
    - Tire life prediction
    - Fuel strategy
    - Race position impact
    """

    def __init__(self):
        self.pit_loss_time = 25.0  # seconds (typical pit stop time loss)
        self.tire_compounds = {
            'soft': {'initial_pace': 1.0, 'degradation': 0.05, 'life': 15},
            'medium': {'initial_pace': 0.98, 'degradation': 0.03, 'life': 25},
            'hard': {'initial_pace': 0.95, 'degradation': 0.02, 'life': 35}
        }

    def calculate_tire_life_remaining(
        self,
        current_lap: int,
        tire_compound: str,
        stint_start_lap: int = 1
    ) -> Dict:
        """
        Kalan lastik ömrü hesaplama

        Physics-based degradation model

        Args:
            current_lap: Current lap number
            tire_compound: Tire type
            stint_start_lap: Lap when tires were fitted

        Returns:
            Dict with tire life metrics
        """
        compound_data = self.tire_compounds.get(
            tire_compound.lower(),
            self.tire_compounds['medium']
        )

        laps_on_tire = current_lap - stint_start_lap + 1
        max_life = compound_data['life']
        degradation_rate = compound_data['degradation']

        # Remaining life percentage
        life_remaining = max(0, 100 - (laps_on_tire / max_life * 100))

        # Performance degradation (lap time delta)
        performance_loss = laps_on_tire * degradation_rate

        # Critical threshold
        if life_remaining < 20:
            status = "🔴 CRITICAL"
        elif life_remaining < 40:
            status = "🟡 WARNING"
        else:
            status = "🟢 GOOD"

        return {
            'laps_on_tire': laps_on_tire,
            'life_remaining_pct': round(life_remaining, 1),
            'estimated_laps_left': max(0, max_life - laps_on_tire),
            'performance_loss_sec': round(performance_loss, 3),
            'status': status,
            'compound': tire_compound
        }

    def calculate_undercut_advantage(
        self,
        current_lap: int,
        leader_tire_age: int,
        our_tire_age: int,
        tire_compound: str = "medium"
    ) -> Dict:
        """
        Undercut stratejisi analizi

        Undercut: Rakipten önce pit yaparak temiz lastiklerle avantaj

        Args:
            current_lap: Current lap
            leader_tire_age: Leader's tire age in laps
            our_tire_age: Our tire age
            tire_compound: Tire compound

        Returns:
            Dict with undercut analysis
        """
        compound_data = self.tire_compounds.get(
            tire_compound.lower(),
            self.tire_compounds['medium']
        )

        # Leader's tire degradation
        leader_degradation = leader_tire_age * compound_data['degradation']

        # Our fresh tire advantage (after pit)
        fresh_tire_advantage = leader_degradation

        # Pit stop time loss
        net_advantage = fresh_tire_advantage - (self.pit_loss_time / 90)  # Convert to lap time delta

        # Undercut viable?
        viable = net_advantage > 0

        return {
            'current_lap': current_lap,
            'leader_tire_age': leader_tire_age,
            'our_tire_age': our_tire_age,
            'fresh_tire_advantage_sec': round(fresh_tire_advantage, 2),
            'pit_loss_sec': self.pit_loss_time,
            'net_advantage_sec': round(net_advantage * 90, 2),  # Convert back to seconds
            'undercut_viable': viable,
            'recommendation': "✅ GO FOR UNDERCUT" if viable else "❌ STAY OUT"
        }

    def calculate_overcut_advantage(
        self,
        current_lap: int,
        rival_just_pitted: bool,
        our_tire_age: int,
        laps_until_rival_catches: int = 10
    ) -> Dict:
        """
        Overcut stratejisi

        Overcut: Rakip pit yaptıktan sonra biz dışarıda kalarak track position koruma

        Args:
            current_lap: Current lap
            rival_just_pitted: Did rival just pit?
            our_tire_age: Our current tire age
            laps_until_rival_catches: Estimated laps until rival catches up

        Returns:
            Dict with overcut analysis
        """
        if not rival_just_pitted:
            return {
                'viable': False,
                'recommendation': "⏸️ Wait for rival to pit first"
            }

        # Can we stay out long enough?
        tire_life = self.calculate_tire_life_remaining(
            current_lap,
            'medium',
            current_lap - our_tire_age
        )

        laps_available = tire_life['estimated_laps_left']

        # Overcut viable if we can stay out 5+ more laps
        viable = laps_available >= 5

        return {
            'current_lap': current_lap,
            'our_tire_age': our_tire_age,
            'laps_available': laps_available,
            'laps_needed': laps_until_rival_catches,
            'overcut_viable': viable,
            'recommendation': "✅ STAY OUT (Overcut)" if viable else "⚠️ PIT NEXT LAP"
        }

    def simulate_pit_stop_scenarios(
        self,
        current_lap: int,
        total_laps: int,
        current_tire_age: int,
        current_compound: str = "medium"
    ) -> List[Dict]:
        """
        Birden fazla pit senaryosu simüle et

        Scenarios:
        1. Pit now
        2. Pit in 3 laps
        3. Pit in 5 laps
        4. No more stops

        Args:
            current_lap: Current lap
            total_laps: Total race laps
            current_tire_age: Current tire age
            current_compound: Current tire compound

        Returns:
            List of scenario dicts
        """
        scenarios = []

        # Scenario 1: Pit now
        scenarios.append(self._simulate_scenario(
            pit_lap=current_lap,
            total_laps=total_laps,
            current_tire_age=current_tire_age,
            current_compound=current_compound,
            name="Pit NOW"
        ))

        # Scenario 2: Pit in 3 laps
        if current_lap + 3 <= total_laps:
            scenarios.append(self._simulate_scenario(
                pit_lap=current_lap + 3,
                total_laps=total_laps,
                current_tire_age=current_tire_age,
                current_compound=current_compound,
                name="Pit in +3 laps"
            ))

        # Scenario 3: Pit in 5 laps
        if current_lap + 5 <= total_laps:
            scenarios.append(self._simulate_scenario(
                pit_lap=current_lap + 5,
                total_laps=total_laps,
                current_tire_age=current_tire_age,
                current_compound=current_compound,
                name="Pit in +5 laps"
            ))

        # Scenario 4: No stop (if viable)
        if current_tire_age < 15:
            scenarios.append(self._simulate_scenario(
                pit_lap=None,
                total_laps=total_laps,
                current_tire_age=current_tire_age,
                current_compound=current_compound,
                name="No stop"
            ))

        # Sort by projected time
        scenarios.sort(key=lambda x: x['projected_total_time'])

        return scenarios

    def _simulate_scenario(
        self,
        pit_lap: Optional[int],
        total_laps: int,
        current_tire_age: int,
        current_compound: str,
        name: str
    ) -> Dict:
        """Single scenario simulation"""

        compound_data = self.tire_compounds.get(
            current_compound.lower(),
            self.tire_compounds['medium']
        )

        total_time = 0
        current_lap_sim = 1

        # Before pit (if applicable)
        if pit_lap:
            laps_before_pit = pit_lap - current_lap_sim
            for lap in range(laps_before_pit):
                tire_age = current_tire_age + lap
                degradation = tire_age * compound_data['degradation']
                lap_time = 90 + degradation  # Base lap time + degradation
                total_time += lap_time

            # Pit stop
            total_time += self.pit_loss_time

            # After pit (fresh tires)
            laps_after_pit = total_laps - pit_lap
            for lap in range(laps_after_pit):
                degradation = lap * compound_data['degradation']
                lap_time = 90 + degradation
                total_time += lap_time

        else:
            # No pit - all laps on current tires
            for lap in range(total_laps - current_lap_sim + 1):
                tire_age = current_tire_age + lap
                degradation = tire_age * compound_data['degradation']
                lap_time = 90 + degradation
                total_time += lap_time

        return {
            'scenario': name,
            'pit_lap': pit_lap if pit_lap else "No pit",
            'projected_total_time': round(total_time, 2),
            'time_vs_best': 0,  # Will be calculated after sorting
            'viable': True
        }

    def calculate_fuel_consumption(
        self,
        laps_remaining: int,
        avg_fuel_per_lap: float = 2.5,
        current_fuel: float = 100.0
    ) -> Dict:
        """
        Yakıt tüketimi ve strateji

        Args:
            laps_remaining: Remaining laps
            avg_fuel_per_lap: Fuel consumption per lap (kg)
            current_fuel: Current fuel level (kg)

        Returns:
            Dict with fuel strategy
        """
        fuel_needed = laps_remaining * avg_fuel_per_lap
        fuel_margin = current_fuel - fuel_needed

        if fuel_margin < 0:
            status = "🔴 FUEL CRITICAL"
            recommendation = f"SAVE FUEL: Lift and coast. {abs(fuel_margin):.1f} kg short."
        elif fuel_margin < 5:
            status = "🟡 FUEL TIGHT"
            recommendation = "Manage fuel: Reduce rich mix usage."
        else:
            status = "🟢 FUEL OK"
            recommendation = f"Fuel comfortable. {fuel_margin:.1f} kg margin available."

        return {
            'laps_remaining': laps_remaining,
            'fuel_needed_kg': round(fuel_needed, 1),
            'current_fuel_kg': round(current_fuel, 1),
            'fuel_margin_kg': round(fuel_margin, 1),
            'laps_of_fuel': round(current_fuel / avg_fuel_per_lap, 1) if avg_fuel_per_lap > 0 else 0,
            'status': status,
            'recommendation': recommendation
        }

    def caution_flag_strategy(
        self,
        current_lap: int,
        caution_lap: int,
        tire_age: int,
        pits_closed: bool = False
    ) -> Dict:
        """
        Caution flag (sarı bayrak) stratejisi

        NASCAR/IndyCar style caution periods

        Args:
            current_lap: Current lap
            caution_lap: Lap when caution started
            tire_age: Current tire age
            pits_closed: Are pits closed during caution?

        Returns:
            Dict with caution strategy
        """
        if pits_closed:
            return {
                'recommendation': "⏸️ PITS CLOSED - Wait for opening"
            }

        # Should we pit under caution?
        pit_now = tire_age > 10  # Pit if tires old

        if pit_now:
            recommendation = "✅ PIT NOW - Free stop under caution!"
            reason = "Old tires + no time loss under yellow"
        else:
            recommendation = "❌ STAY OUT - Tires still fresh"
            reason = "Save pit stop for later in race"

        return {
            'current_lap': current_lap,
            'caution_lap': caution_lap,
            'tire_age': tire_age,
            'pit_recommended': pit_now,
            'recommendation': recommendation,
            'reason': reason
        }


# Test
if __name__ == "__main__":
    sim = PitStrategySimulator()

    print("=== PIT STRATEGY SIMULATOR ===\n")

    # Test 1: Tire life
    print("1. TIRE LIFE:")
    tire_life = sim.calculate_tire_life_remaining(
        current_lap=15,
        tire_compound="soft",
        stint_start_lap=1
    )
    print(f"Laps on tire: {tire_life['laps_on_tire']}")
    print(f"Life remaining: {tire_life['life_remaining_pct']}%")
    print(f"Status: {tire_life['status']}\n")

    # Test 2: Undercut
    print("2. UNDERCUT ANALYSIS:")
    undercut = sim.calculate_undercut_advantage(
        current_lap=20,
        leader_tire_age=15,
        our_tire_age=12
    )
    print(f"Viable: {undercut['undercut_viable']}")
    print(f"Net advantage: {undercut['net_advantage_sec']:.2f}s")
    print(f"{undercut['recommendation']}\n")

    # Test 3: Scenarios
    print("3. PIT SCENARIOS:")
    scenarios = sim.simulate_pit_stop_scenarios(
        current_lap=10,
        total_laps=50,
        current_tire_age=8
    )
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['scenario']}: {scenario['projected_total_time']:.2f}s")

    # Test 4: Fuel
    print("\n4. FUEL STRATEGY:")
    fuel = sim.calculate_fuel_consumption(
        laps_remaining=30,
        current_fuel=85.0
    )
    print(f"Status: {fuel['status']}")
    print(f"Margin: {fuel['fuel_margin_kg']} kg")
    print(f"{fuel['recommendation']}")
