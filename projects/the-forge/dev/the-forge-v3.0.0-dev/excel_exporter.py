import pandas as pd
from typing import List

def export_paths_to_excel(paths: List[List[str]], output_path: str):
    df = pd.DataFrame(paths, columns=[f'Level{i+1}' for i in range(6)])  # type: ignore[arg-type]
    df.to_excel(output_path, index=False) 