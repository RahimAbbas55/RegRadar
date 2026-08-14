#Hand-verified question 
GOLDEN_DATASET = [
    {
        "id": "gd_001",
        "question": "Does a firm need to have systems and controls to counter financial crime?",
        "expected_provision_ids": ["SYSC 3.2.6"],
        "difficulty": "easy",
        "notes": "Direct lookup — a single, clearly binding Rule.",
    },
    {
        "id": "gd_002",
        "question": "Is staff training on money laundering required or just recommended?",
        "expected_provision_ids": ["SYSC 6.3.7", "SYSC 3.2.6G"],
        "difficulty": "easy",
        "notes": "Tests whether the system correctly identifies this as Guidance, not a binding Rule.",
    },
    {
        "id": "gd_003",
        "question": "Who must be appointed to oversee a firm's anti-money laundering compliance?",
        "expected_provision_ids": ["SYSC 6.3.9", "SYSC 3.2.6H"],
        "difficulty": "medium",
        "notes": "Requires connecting MLRO appointment (6.3.9) with senior management responsibility (3.2.6H).",
    },
    {
        "id": "gd_004",
        "question": "Can a firm avoid responsibility for compliance by outsourcing a function to another company?",
        "expected_provision_ids": ["SYSC 3.2.4"],
        "difficulty": "medium",
        "notes": "Tests whether the system correctly conveys 'a firm cannot contract out its regulatory obligations.'",
    },
    {
        "id": "gd_005",
        "question": "Which SYSC chapters apply to an insurer?",
        "expected_provision_ids": ["SYSC 1.1A.1"],
        "difficulty": "medium",
        "notes": "Tests table retrieval specifically — answer lives in a markdown table chunk, not prose.",
    },
    {
        "id": "gd_006",
        "question": "What must a firm's compliance function be responsible for?",
        "expected_provision_ids": ["SYSC 6.1.3", "SYSC 3.2.7"],
        "difficulty": "medium",
        "notes": "Multiple provisions describe compliance function responsibilities across different SYSC sections.",
    },
    {
        "id": "gd_007",
        "question": "What is the maximum penalty for insider trading under UK law?",
        "expected_provision_ids": [],
        "difficulty": "out_of_scope",
        "notes": "Deliberately not covered by our scraped SYSC sections — system should decline to answer, not hallucinate.",
    },
    {
        "id": "gd_008",
        "question": "What should a firm consider when delegating tasks to employees?",
        "expected_provision_ids": ["SYSC 3.2.3"],
        "difficulty": "easy",
        "notes": "Direct lookup on delegation safeguards.",
    },
]