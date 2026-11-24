from app.prompts.sections.identity import IDENTITY
from app.prompts.sections.behavior import BEHAVIOR
from app.prompts.sections.volleyball import VOLLEYBALL
from app.prompts.sections.formatting import FORMATTING

SYSTEM_PROMPT = f"""

{IDENTITY}

{BEHAVIOR}

{VOLLEYBALL}

{FORMATTING}

"""