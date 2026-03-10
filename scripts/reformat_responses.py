import sys
from pathlib import Path

# Ensure project src/ is importable regardless of cwd
BASE = Path(__file__).resolve().parent.parent
SRC = BASE / 'src'
sys.path.insert(0, str(SRC))

from prompt_runner import PromptRunner

if __name__ == '__main__':
    runner = PromptRunner(output_dir='results')
    input_file = 'results/wmdp_responses_20260210_162744.json'
    if not Path(input_file).exists():
        print(f"Input file not found: {input_file}")
        sys.exit(2)
    out = runner.export_grouped_responses(input_file=input_file)
    print(f"Exported grouped responses to: {out}")
