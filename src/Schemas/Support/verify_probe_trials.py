import re
from collections import Counter


def analyze_sequence_uniqueness(filename: str = "probe_trials_stage7_240.yml"):
    """Analyze the uniqueness of odor sequences in the probe trials."""
    
    with open(filename, 'r') as f:
        content = f.read()
    
    print(f"=== Sequence Uniqueness Analysis ===")
    
    # Parse all sequences
    sequences = []
    
    # Find all rewardConditions blocks
    reward_blocks = re.findall(r'rewardConditions: \[\{position: (\d+), definition: \[(.*?)\]\}\]', content, re.DOTALL)
    
    print(f"Found {len(reward_blocks)} reward condition blocks")
    
    for i, (position_str, definition_str) in enumerate(reward_blocks):
        # Parse the definition array to extract odor sequence
        command_blocks = re.findall(r'\[{command: (Odor[A-G]), rewarded: (True|False), minimumSamplingTime: [\d.]+, maximumSamplingTime: \d+}\]', definition_str)
        
        if len(command_blocks) == 5:
            # Extract just the odor sequence (order matters)
            odor_sequence = tuple([cmd for cmd, _ in command_blocks])
            sequences.append({
                'index': i + 1,
                'sequence': odor_sequence,
                'position_field': int(position_str)
            })
    
    print(f"Parsed {len(sequences)} complete sequences")
    
    # Check for duplicate sequences
    sequence_signatures = [seq['sequence'] for seq in sequences]
    signature_counts = Counter(sequence_signatures)
    
    # Find duplicates
    duplicates = {sig: count for sig, count in signature_counts.items() if count > 1}
    unique_count = len(set(sequence_signatures))
    
    print(f"\nDuplicate Analysis:")
    print(f"- Total sequences: {len(sequences)}")
    print(f"- Unique sequences: {unique_count}")
    print(f"- Duplicate sequences: {len(sequences) - unique_count}")
    
    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate sequence patterns:")
        for sig, count in duplicates.items():
            print(f"  {sig} appears {count} times")
            
            # Find which sequence indices have this pattern
            matching_indices = [seq['index'] for seq in sequences if seq['sequence'] == sig]
            print(f"    Found in sequences: {matching_indices}")
    else:
        print(f"\n✓ All sequences are unique!")
    
    # Show some examples of sequences
    print(f"\nFirst 10 sequences:")
    for i, seq in enumerate(sequences[:10]):
        rewarded_odor = None
        for odor in seq['sequence']:
            if odor in ['OdorA', 'OdorB']:
                rewarded_odor = odor
                break
        
        print(f"  {i+1:2d}: {' -> '.join(seq['sequence'])} (rewarded: {rewarded_odor}, pos: {seq['position_field']})")
    
    # Check if any sequences with A/B at start are duplicated
    start_sequences = [seq for seq in sequences if seq['sequence'][0] in ['OdorA', 'OdorB']]
    end_sequences = [seq for seq in sequences if seq['sequence'][4] in ['OdorA', 'OdorB']]
    
    print(f"\nSequence Position Analysis:")
    print(f"- A/B at START (position 0): {len(start_sequences)} sequences")
    print(f"- A/B at END (position 4): {len(end_sequences)} sequences")
    
    if start_sequences:
        print(f"\nSequences with A/B at START:")
        for seq in start_sequences[:5]:  # Show first 5
            print(f"  {' -> '.join(seq['sequence'])}")
        if len(start_sequences) > 5:
            print(f"  ... and {len(start_sequences) - 5} more")
    
    return len(duplicates) == 0, duplicates


if __name__ == "__main__":
    is_unique, duplicates = analyze_sequence_uniqueness()
    
    if is_unique:
        print(f"\n✅ SUCCESS: All 240 sequences have unique odor orders!")
    else:
        print(f"\n❌ ISSUE: Found {len(duplicates)} duplicate sequence patterns that need to be fixed.")
