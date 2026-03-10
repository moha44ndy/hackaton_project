import sys
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / 'src'))

from elk_logger import get_elk_logger

if __name__ == '__main__':
    elk = get_elk_logger()
    print('ELK enabled:', elk.enabled)
    try:
        print('ELK health_check:', elk.health_check())
    except Exception as e:
        print('ELK health_check raised:', e)
