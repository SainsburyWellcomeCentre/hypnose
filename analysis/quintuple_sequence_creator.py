from itertools import combinations, permutations

def generate_quintuple_sequences():
    non_rewarded_odors = ['C', 'D', 'E', 'F', 'G']
    
    # Generate all combinations of 4 odors from 5
    odor_combinations = list(combinations(non_rewarded_odors, 4))
    
    sequences_a = []  # For OdorA reward (position 0)
    sequences_b = []  # For OdorB reward (position 1)
    
    for combo in odor_combinations:
        # Generate all permutations of the 4 odors
        for perm in permutations(combo):
            # Create sequence for OdorA reward
            seq_a = {
                "name": "QuintupleA_Stage1",
                "defaultCommand": "Default",
                "interCommand": "Purge", 
                "interCommandTime": 0.2,
                "maximumTime": 10,
                "responseTime": 99999,
                "interTrialInterval": 0,
                "completionRequiresEngagement": True,
                "rewardConditions": [{
                    "position": 0,
                    "definition": [
                        [{"command": f"Odor{perm[0]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": f"Odor{perm[1]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": f"Odor{perm[2]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": f"Odor{perm[3]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": "OdorA", "rewarded": True, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}]
                    ]
                }],
                "rewardAttempts": 0,
                "enableTrialIndicator": True,
                "enableRewardLocationIndicator": False,
                "resetOnReward": True,
                "skipSampling": False,
                "rewardAvailablePokeReset": False
            }
            
            # Create sequence for OdorB reward  
            seq_b = {
                "name": "QuintupleB_Stage1",
                "defaultCommand": "Default",
                "interCommand": "Purge",
                "interCommandTime": 0.2, 
                "maximumTime": 10,
                "responseTime": 99999,
                "interTrialInterval": 0,
                "completionRequiresEngagement": True,
                "rewardConditions": [{
                    "position": 1,
                    "definition": [
                        [{"command": f"Odor{perm[0]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": f"Odor{perm[1]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": f"Odor{perm[2]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": f"Odor{perm[3]}", "rewarded": False, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}],
                        [{"command": "OdorB", "rewarded": True, "minimumSamplingTime": 0.35, "maximumSamplingTime": 1}]
                    ]
                }],
                "rewardAttempts": 0,
                "enableTrialIndicator": True,
                "enableRewardLocationIndicator": False,
                "resetOnReward": True,
                "skipSampling": False,
                "rewardAvailablePokeReset": False
            }
            
            sequences_a.append(seq_a)
            sequences_b.append(seq_b)
    
    return sequences_a + sequences_b

# Generate sequences
all_sequences = generate_quintuple_sequences()

# Save in exact YAML format as plain text matching the existing file structure
with open('/Users/Volkan/Repos/hypnose/analysis/quintuple_sequences.txt', 'w') as f:
    f.write("sequences: [\n")
    f.write("  [\n")
    
    for i, seq in enumerate(all_sequences):
        f.write("    {\n")
        f.write(f"      name: {seq['name']},\n")
        f.write(f"      defaultCommand: {seq['defaultCommand']},\n")
        f.write(f"      interCommand: {seq['interCommand']},\n")
        f.write(f"      interCommandTime: {seq['interCommandTime']},\n")
        f.write(f"      maximumTime: {seq['maximumTime']},\n")
        f.write(f"      responseTime: {seq['responseTime']},\n")
        f.write(f"      interTrialInterval: {seq['interTrialInterval']},\n")
        f.write(f"      completionRequiresEngagement: {str(seq['completionRequiresEngagement'])},\n")
        
        # Write reward conditions in exact format
        rc = seq['rewardConditions'][0]
        f.write(f"      rewardConditions: [{{position: {rc['position']}, definition: [")
        
        for j, step in enumerate(rc['definition']):
            cmd = step[0]
            f.write(f"[{{command: {cmd['command']}, rewarded: {str(cmd['rewarded'])}, minimumSamplingTime: {cmd['minimumSamplingTime']}, maximumSamplingTime: {cmd['maximumSamplingTime']}}}]")
            if j < len(rc['definition']) - 1:
                f.write(", ")
        
        f.write("]}],\n")
        f.write(f"      rewardAttempts: {seq['rewardAttempts']},\n")
        f.write(f"      enableTrialIndicator: {str(seq['enableTrialIndicator'])},\n")
        f.write(f"      enableRewardLocationIndicator: {str(seq['enableRewardLocationIndicator'])},\n")
        f.write(f"      resetOnReward: {str(seq['resetOnReward'])},\n")
        f.write(f"      skipSampling: {str(seq['skipSampling'])},\n")
        f.write(f"      rewardAvailablePokeReset: {str(seq['rewardAvailablePokeReset'])}\n")
        f.write("    }")
        
        if i < len(all_sequences) - 1:
            f.write(",")
        f.write("\n")
    
    f.write("  ]\n")
    f.write("]\n")

print(f"Generated {len(all_sequences)} quintuple sequences saved to quintuple_sequences.txt")
print(f"- {len(all_sequences)//2} QuintupleA_Stage1 sequences")
print(f"- {len(all_sequences)//2} QuintupleB_Stage1 sequences")