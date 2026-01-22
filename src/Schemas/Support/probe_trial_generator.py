import random
from itertools import combinations, permutations
from typing import List, Dict, Any, Set
import json


def create_probe_trial_sequence(rewarded_odor: str, rewarded_at_start: bool = False, used_signatures: Set[tuple] = None) -> Dict:
    """
    Create a single probe trial sequence matching the original YAML format exactly.
    
    Args:
        rewarded_odor: 'A' or 'B'
        rewarded_at_start: If True, put rewarded odor at sequence position 0, else at position 4
        used_signatures: Set of used sequence signatures to avoid duplicates
    
    Returns:
        Dictionary representing the probe trial sequence, or None if couldn't create unique sequence
    """
    if used_signatures is None:
        used_signatures = set()
    
    non_rewarded_odors = ['C', 'D', 'E', 'F', 'G']
    max_attempts = 100
    
    for attempt in range(max_attempts):
        # Select 4 different non-rewarded odors and create permutation
        selected_odors = random.sample(non_rewarded_odors, 4)
        random.shuffle(selected_odors)
        
        if rewarded_at_start:
            # Rewarded odor at sequence position 0 (start)
            sequence = [f'Odor{rewarded_odor}'] + [f'Odor{odor}' for odor in selected_odors]
        else:
            # Rewarded odor at sequence position 4 (end)
            sequence = [f'Odor{odor}' for odor in selected_odors] + [f'Odor{rewarded_odor}']
        
        # Create signature for uniqueness check
        signature = tuple(sequence)
        
        if signature not in used_signatures:
            used_signatures.add(signature)
            
            # Create definition array - this is the key insight from the original format
            definition = []
            for i, odor in enumerate(sequence):
                is_rewarded = (odor == f'Odor{rewarded_odor}')
                definition.append([{
                    'command': odor,
                    'rewarded': is_rewarded,
                    'minimumSamplingTime': 0.35,
                    'maximumSamplingTime': 1
                }])
            
            # Position is ALWAYS 0 for OdorA, 1 for OdorB (regardless of sequence position)
            position = 0 if rewarded_odor == 'A' else 1
            
            return {
                'name': f'QuintupleProbe{rewarded_odor}_Stage7',
                'defaultCommand': 'Default',
                'interCommand': 'Purge',
                'interCommandTime': 0.2,
                'maximumTime': 10,
                'responseTime': 99999,
                'interTrialIntervalSuccessfulTrial': 0,
                'completionRequiresEngagement': False,
                'rewardConditions': [{
                    'position': position,
                    'definition': definition
                }],
                'rewardAttempts': 0,
                'enableTrialEndIndicator': False,
                'enableRewardLocationIndicator': False,
                'resetOnReward': True,
                'skipSampling': False,
                'rewardAvailablePokeReset': False,
                'enableTrialStartIndicator': True,
                'interTrialIntervalUnsuccessfulTrial': 3
            }
    
    print(f"Warning: Could not create unique sequence after {max_attempts} attempts")
    return None


def generate_all_possible_combinations():
    """Generate all possible unique combinations for diversity analysis."""
    non_rewarded_odors = ['C', 'D', 'E', 'F', 'G']
    # All combinations of 4 from 5 odors
    all_combinations = list(combinations(non_rewarded_odors, 4))
    # All permutations of each combination to increase diversity
    all_permutations = []
    for combo in all_combinations:
        perms = list(permutations(combo))
        all_permutations.extend(perms)
    
    print(f"Total possible 4-odor combinations: {len(all_combinations)}")
    print(f"Total possible 4-odor permutations: {len(all_permutations)}")
    
    # With A or B at start or end, we have:
    # - 2 rewarded odors (A, B)
    # - 2 positions (start, end) 
    # - X permutations of 4 non-rewarded odors
    max_unique = len(all_permutations) * 2 * 2
    print(f"Theoretical maximum unique sequences: {max_unique}")
    return all_permutations


def generate_probe_trials(num_trials: int = 240) -> List[Dict]:
    """
    Generate probe trials with 90% having A/B at end, 10% having A/B at start.
    
    Args:
        num_trials: Total number of probe trials to generate (default 240, same as original)
    
    Returns:
        List of probe trial dictionaries
    """
    if num_trials < 10:
        raise ValueError("Need at least 10 trials to have meaningful 10% distribution")
    
    # Check theoretical limits
    all_perms = generate_all_possible_combinations()
    theoretical_max = len(all_perms) * 2 * 2  # 2 odors, 2 positions
    
    if num_trials > theoretical_max:
        print(f"Warning: Requesting {num_trials} sequences but theoretical maximum is {theoretical_max}")
        print("Will generate unique sequences up to the maximum and then allow repetitions")
    
    # Calculate distribution
    trials_with_ab_at_start = max(1, num_trials // 10)  # 10% at start (24 trials)
    trials_with_ab_at_end = num_trials - trials_with_ab_at_start  # 90% at end (216 trials)
    
    print(f"Generating {num_trials} probe trials:")
    print(f"  - {trials_with_ab_at_start} trials with A/B at START (sequence position 0)")
    print(f"  - {trials_with_ab_at_end} trials with A/B at END (sequence position 4)")
    
    probe_trials = []
    used_signatures = set()
    
    # Generate sequences with A/B at start (10%)
    perm_index = 0
    for i in range(trials_with_ab_at_start):
        rewarded_odor = 'A' if i % 2 == 0 else 'B'
        
        trial = create_probe_trial_sequence(rewarded_odor, rewarded_at_start=True, used_signatures=used_signatures)
        if trial:
            probe_trials.append(trial)
    
    # Generate sequences with A/B at end (90%)
    for i in range(trials_with_ab_at_end):
        rewarded_odor = 'A' if i % 2 == 0 else 'B'
        
        trial = create_probe_trial_sequence(rewarded_odor, rewarded_at_start=False, used_signatures=used_signatures)
        if trial:
            probe_trials.append(trial)
    
    # Shuffle the final list
    random.shuffle(probe_trials)
    
    print(f"Generated {len(probe_trials)} probe trials")
    print(f"Unique sequences: {len(used_signatures)}")
    
    return probe_trials


def format_yaml_manually(yaml_content: dict) -> str:
    """Manually format YAML to match the original style exactly."""
    
    def format_sequence(seq, indent="    "):
        lines = []
        lines.append(f"{indent}{{")
        lines.append(f"{indent}  name: {seq['name']},")
        lines.append(f"{indent}  defaultCommand: {seq['defaultCommand']},")
        lines.append(f"{indent}  interCommand: {seq['interCommand']},")
        lines.append(f"{indent}  interCommandTime: {seq['interCommandTime']},")
        lines.append(f"{indent}  maximumTime: {seq['maximumTime']},")
        lines.append(f"{indent}  responseTime: {seq['responseTime']},")
        lines.append(f"{indent}  interTrialIntervalSuccessfulTrial: {seq['interTrialIntervalSuccessfulTrial']},")
        lines.append(f"{indent}  completionRequiresEngagement: {seq['completionRequiresEngagement']},")
        
        # Format rewardConditions
        reward_cond = seq['rewardConditions'][0]
        definition_items = []
        for def_item in reward_cond['definition']:
            cmd_dict = def_item[0]
            definition_items.append(f"[{{command: {cmd_dict['command']}, rewarded: {cmd_dict['rewarded']}, minimumSamplingTime: {cmd_dict['minimumSamplingTime']}, maximumSamplingTime: {cmd_dict['maximumSamplingTime']}}}]")
        
        definition_str = "[" + ", ".join(definition_items) + "]"
        lines.append(f"{indent}  rewardConditions: [{{position: {reward_cond['position']}, definition: {definition_str}}}],")
        
        lines.append(f"{indent}  rewardAttempts: {seq['rewardAttempts']},")
        lines.append(f"{indent}  enableTrialEndIndicator: {seq['enableTrialEndIndicator']},")
        lines.append(f"{indent}  enableRewardLocationIndicator: {seq['enableRewardLocationIndicator']},")
        lines.append(f"{indent}  resetOnReward: {seq['resetOnReward']},")
        lines.append(f"{indent}  skipSampling: {seq['skipSampling']},")
        lines.append(f"{indent}  rewardAvailablePokeReset: {seq['rewardAvailablePokeReset']},")
        lines.append(f"{indent}  enableTrialStartIndicator: {seq['enableTrialStartIndicator']},")
        lines.append(f"{indent}  interTrialIntervalUnsuccessfulTrial: {seq['interTrialIntervalUnsuccessfulTrial']}")
        lines.append(f"{indent}}}")
        
        return "\n".join(lines)
    
    # Start building the YAML
    lines = []
    lines.append("%YAML 1.1")
    lines.append("---")
    lines.append("# yaml-language-server: $schema=sequence-schema.json")
    lines.append("# Generated probe trials for quintuples-stage7")
    lines.append("# 240 unique sequences: 10% with A/B at start, 90% with A/B at end")
    lines.append("")
    lines.append(f"nextSequence: {yaml_content['nextSequence']}")
    lines.append(f"performaceCriterion: {yaml_content['performaceCriterion']}")
    lines.append("sequences: [")
    lines.append("  [")
    
    # Add all sequences
    sequences = yaml_content['sequences'][0]
    for i, seq in enumerate(sequences):
        if i > 0:
            lines.append("    ,")
        lines.append(format_sequence(seq))
    
    lines.append("  ]")
    lines.append("]")
    
    return "\n".join(lines)


def save_probe_trials_yaml(probe_sequences: List[Dict[str, Any]], filename: str = "probe_trials_stage7_240.yml"):
    """
    Save probe trial sequences to a YAML file matching the original format exactly.
    
    Args:
        probe_sequences: List of probe trial sequence dictionaries
        filename: Output filename (default: "probe_trials_stage7_240_corrected.yml")
    """
    
    # Create the complete YAML structure
    yaml_content = {
        "nextSequence": "Schemas/stage7-test.yml",
        "performaceCriterion": 1.1,
        "sequences": [probe_sequences]  # Note: sequences is a list containing one list of sequences
    }
    
    # Format and save manually to match original style
    formatted_yaml = format_yaml_manually(yaml_content)
    
    with open(filename, 'w') as f:
        f.write(formatted_yaml)
    
    print(f"Probe trials saved to {filename}")


if __name__ == "__main__":
    # Generate 240 probe trials
    probe_trials = generate_probe_trials(240)
    
    # Save to YAML file
    save_probe_trials_yaml(probe_trials)
    
    print(f"\nGeneration complete!")
    print(f"Total sequences: {len(probe_trials)}")
    
    # Count distribution
    start_count = 0
    end_count = 0
    a_count = 0
    b_count = 0
    
    for trial in probe_trials:
        # Check if rewarded odor is at start or end of sequence
        definition = trial['rewardConditions'][0]['definition']
        rewarded_odor_cmd = None
        for i, def_item in enumerate(definition):
            if def_item[0]['rewarded']:
                rewarded_odor_cmd = def_item[0]['command']
                if i == 0:
                    start_count += 1
                elif i == 4:
                    end_count += 1
                break
        
        if rewarded_odor_cmd == 'OdorA':
            a_count += 1
        elif rewarded_odor_cmd == 'OdorB':
            b_count += 1
    
    print(f"Sequences with A/B at START: {start_count} ({start_count/len(probe_trials)*100:.1f}%)")
    print(f"Sequences with A/B at END: {end_count} ({end_count/len(probe_trials)*100:.1f}%)")
    print(f"OdorA trials: {a_count}")
    print(f"OdorB trials: {b_count}")
    print(f"Position field - OdorA: always 0, OdorB: always 1 (as per original format)")
