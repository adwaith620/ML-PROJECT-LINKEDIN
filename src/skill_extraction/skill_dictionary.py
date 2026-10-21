"""
skill_dictionary.py

Centralized taxonomy of canonical technical skills, frameworks, databases,
cloud platforms, developer tools, certifications, degrees, and aliases.
Also defines explicit related/transferable skill relationships with categories.
"""

from typing import Dict, List, Tuple

# 1. PROGRAMMING LANGUAGES
PROGRAMMING_LANGUAGES = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "C", 
    "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "R", "Scala", 
    "Dart", "SQL", "NoSQL", "Shell", "Bash", "HTML", "CSS"
]

# 2. FRAMEWORKS & LIBRARIES
FRAMEWORKS_AND_LIBRARIES = [
    "React", "Vue.js", "Angular", "Node.js", "Express.js", "Next.js", 
    "Django", "Flask", "FastAPI", "Spring Boot", "ASP.NET", ".NET", 
    "Ruby on Rails", "Flutter", "React Native", "PyTorch", "TensorFlow", 
    "Keras", "Scikit-Learn", "Pandas", "NumPy", "SciPy", "Tailwind CSS", 
    "Bootstrap"
]

# 3. DATABASES
DATABASES = [
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Oracle", 
    "Microsoft SQL Server", "Elasticsearch", "Cassandra", "DynamoDB", 
    "Firebase", "Neo4j", "Snowflake", "MariaDB"
]

# 4. CLOUD & DEVOPS
CLOUD_AND_DEVOPS = [
    "AWS", "Google Cloud Platform", "Microsoft Azure", "Docker", 
    "Kubernetes", "CI/CD", "Jenkins", "GitLab CI/CD", "GitHub Actions", 
    "Terraform", "Ansible", "Linux"
]

# 5. ARCHITECTURE & METHODOLOGIES
ARCHITECTURE_AND_CONCEPTS = [
    "Microservices", "REST APIs", "GraphQL", "Machine Learning", 
    "Deep Learning", "Natural Language Processing", "Computer Vision", 
    "Agile", "Scrum"
]

# 6. DEVELOPER TOOLS
DEVELOPER_TOOLS = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", 
    "Postman", "Webpack", "Vite", "npm", "Yarn", "Docker Compose"
]

# 7. CERTIFICATIONS
CERTIFICATIONS = [
    "AWS Certified Solutions Architect", "Certified Kubernetes Administrator", 
    "Cisco Certified Network Associate", "CCNA", "CompTIA Security+", 
    "Project Management Professional", "PMP", "Certified ScrumMaster", "CSM"
]

# 8. JOB ROLES
JOB_ROLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer", 
    "Full Stack Developer", "Data Scientist", "Machine Learning Engineer", 
    "DevOps Engineer", "Data Engineer", "Cloud Architect", "Product Manager", 
    "UI/UX Designer", "Database Administrator", "Systems Analyst"
]

# 9. EDUCATION DEGREES
EDUCATION_DEGREES = [
    "Bachelor of Science", "B.S.", "BS", "Bachelor of Engineering", "B.E.", "BE",
    "Bachelor of Technology", "B.Tech", "BTech", "Bachelor of Arts", "B.A.", "BA",
    "Master of Science", "M.S.", "MS", "Master of Technology", "M.Tech", "MTech",
    "Master of Business Administration", "MBA", "Doctor of Philosophy", "Ph.D.", "PhD"
]

# Canonical Skill Master List
def get_all_skills() -> List[str]:
    """Returns a flat list of all canonical technical skills."""
    return (
        PROGRAMMING_LANGUAGES +
        FRAMEWORKS_AND_LIBRARIES +
        DATABASES +
        CLOUD_AND_DEVOPS +
        ARCHITECTURE_AND_CONCEPTS +
        DEVELOPER_TOOLS
    )

CANONICAL_SKILLS: List[str] = get_all_skills()

# -----------------------------------------------------------------------------
# ALIAS MAP: lowercase surface form -> Canonical Name
# -----------------------------------------------------------------------------
ALIAS_MAP: Dict[str, str] = {
    # Python & variations
    "python": "Python",
    "python3": "Python",
    "python 3": "Python",
    "python2": "Python",
    "py": "Python",
    
    # JavaScript & TypeScript
    "javascript": "JavaScript",
    "js": "JavaScript",
    "es6": "JavaScript",
    "ecmascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    
    # Java & C / C++ / C# / .NET
    "java": "Java",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "c-sharp": "C#",
    "c": "C",
    ".net": ".NET",
    "dotnet": ".NET",
    ".net core": ".NET",
    "asp.net": "ASP.NET",
    
    # Go / Golang / Rust / Ruby / PHP / Dart / Kotlin / Swift / Scala / R
    "golang": "Go",
    "go": "Go",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "dart": "Dart",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "scala": "Scala",
    "r": "R",
    
    # Frontend Frameworks
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "vue": "Vue.js",
    "vue.js": "Vue.js",
    "vuejs": "Vue.js",
    "angular": "Angular",
    "angular.js": "Angular",
    "angularjs": "Angular",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    
    # Backend Frameworks
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express.js",
    "express.js": "Express.js",
    "expressjs": "Express.js",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring boot": "Spring Boot",
    "springboot": "Spring Boot",
    "ruby on rails": "Ruby on Rails",
    "rails": "Ruby on Rails",
    
    # Mobile
    "flutter": "Flutter",
    "react native": "React Native",
    
    # AI / ML / DS
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "machine-learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "deep-learning": "Deep Learning",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "cv": "Computer Vision",
    "computer vision": "Computer Vision",
    
    # Databases
    "sql": "SQL",
    "nosql": "NoSQL",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "pgsql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "oracle": "Oracle",
    "sql server": "Microsoft SQL Server",
    "mssql": "Microsoft SQL Server",
    "microsoft sql server": "Microsoft SQL Server",
    "elasticsearch": "Elasticsearch",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "firebase": "Firebase",
    "snowflake": "Snowflake",
    "mariadb": "MariaDB",
    
    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "google cloud platform": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "microsoft azure": "Microsoft Azure",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "jenkins": "Jenkins",
    "gitlab ci/cd": "GitLab CI/CD",
    "gitlab ci": "GitLab CI/CD",
    "github actions": "GitHub Actions",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "linux": "Linux",
    "bash": "Bash",
    "shell": "Shell",
    
    # Architecture & APIs
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "restful": "REST APIs",
    "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "microservices": "Microservices",
    "agile": "Agile",
    "scrum": "Scrum",
    
    # Dev Tools
    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "postman": "Postman",
    "jira": "Jira",
    "webpack": "Webpack",
    "vite": "Vite",
    "docker compose": "Docker Compose",
    "docker-compose": "Docker Compose"
}

# -----------------------------------------------------------------------------
# RELATED / TRANSFERABLE SKILLS MAP
# Defines related technologies by domain with transferability credit (0.0 to 1.0).
# Example: If JD asks for MySQL, having PostgreSQL is related (credit = 0.5),
# but NOT an exact match.
# -----------------------------------------------------------------------------
RELATED_SKILLS_MAP: Dict[str, List[Tuple[str, str, float]]] = {
    # Relational Databases
    "MySQL": [
        ("PostgreSQL", "Relational Database", 0.5),
        ("SQLite", "Relational Database", 0.4),
        ("Oracle", "Relational Database", 0.5),
        ("Microsoft SQL Server", "Relational Database", 0.5),
        ("MariaDB", "Relational Database", 0.8),
    ],
    "PostgreSQL": [
        ("MySQL", "Relational Database", 0.5),
        ("SQLite", "Relational Database", 0.4),
        ("Oracle", "Relational Database", 0.5),
        ("Microsoft SQL Server", "Relational Database", 0.5),
        ("MariaDB", "Relational Database", 0.5),
    ],
    "SQLite": [
        ("PostgreSQL", "Relational Database", 0.4),
        ("MySQL", "Relational Database", 0.4),
    ],
    "Oracle": [
        ("PostgreSQL", "Relational Database", 0.5),
        ("MySQL", "Relational Database", 0.5),
        ("Microsoft SQL Server", "Relational Database", 0.5),
    ],
    "Microsoft SQL Server": [
        ("PostgreSQL", "Relational Database", 0.5),
        ("MySQL", "Relational Database", 0.5),
        ("Oracle", "Relational Database", 0.5),
    ],
    "MariaDB": [
        ("MySQL", "Relational Database", 0.8),
        ("PostgreSQL", "Relational Database", 0.5),
    ],

    # Cloud Providers
    "AWS": [
        ("Google Cloud Platform", "Public Cloud Provider", 0.5),
        ("Microsoft Azure", "Public Cloud Provider", 0.5),
    ],
    "Google Cloud Platform": [
        ("AWS", "Public Cloud Provider", 0.5),
        ("Microsoft Azure", "Public Cloud Provider", 0.5),
    ],
    "Microsoft Azure": [
        ("AWS", "Public Cloud Provider", 0.5),
        ("Google Cloud Platform", "Public Cloud Provider", 0.5),
    ],

    # Container & Orchestration
    "Kubernetes": [
        ("Docker", "Containerization & Orchestration", 0.4),
        ("Docker Compose", "Containerization & Orchestration", 0.3),
    ],
    "Docker": [
        ("Kubernetes", "Containerization & Orchestration", 0.4),
        ("Docker Compose", "Containerization & Orchestration", 0.6),
    ],

    # Frontend Frameworks
    "React": [
        ("Vue.js", "Frontend Component Framework", 0.5),
        ("Angular", "Frontend Component Framework", 0.4),
        ("Next.js", "React Framework", 0.8),
    ],
    "Vue.js": [
        ("React", "Frontend Component Framework", 0.5),
        ("Angular", "Frontend Component Framework", 0.4),
    ],
    "Angular": [
        ("React", "Frontend Component Framework", 0.4),
        ("Vue.js", "Frontend Component Framework", 0.4),
    ],

    # Python Backend Frameworks
    "FastAPI": [
        ("Flask", "Python Web Framework", 0.5),
        ("Django", "Python Web Framework", 0.5),
    ],
    "Flask": [
        ("FastAPI", "Python Web Framework", 0.5),
        ("Django", "Python Web Framework", 0.5),
    ],
    "Django": [
        ("FastAPI", "Python Web Framework", 0.5),
        ("Flask", "Python Web Framework", 0.5),
    ],

    # Deep Learning Frameworks
    "PyTorch": [
        ("TensorFlow", "Deep Learning Framework", 0.5),
        ("Keras", "Deep Learning Framework", 0.4),
    ],
    "TensorFlow": [
        ("PyTorch", "Deep Learning Framework", 0.5),
        ("Keras", "Deep Learning Framework", 0.6),
    ],

    # Languages
    "TypeScript": [
        ("JavaScript", "Typed JavaScript Superset", 0.7),
    ],
    "JavaScript": [
        ("TypeScript", "Typed JavaScript Superset", 0.6),
    ],
    "C++": [
        ("C", "Systems Programming Language", 0.6),
    ],
    "C": [
        ("C++", "Systems Programming Language", 0.6),
    ],
}

def normalize_skill(term: str) -> str:
    """Normalize a skill term or alias to its canonical name.
    If not found in ALIAS_MAP, returns cleaned original term.
    """
    if not term:
        return ""
    cleaned = term.strip().lower()
    if cleaned in ALIAS_MAP:
        return ALIAS_MAP[cleaned]
    return term.strip()

def get_related_skill_info(candidate_skill: str, target_skill: str):
    """Check if candidate_skill has a documented transferable relationship with target_skill.
    Returns (relationship_description, transferable_credit) if found, else None.
    """
    cand_norm = normalize_skill(candidate_skill)
    target_norm = normalize_skill(target_skill)
    if cand_norm.lower() == target_norm.lower():
        return ("Identical skill", 1.0)
    
    if cand_norm in RELATED_SKILLS_MAP:
        for rel_target, rel_desc, credit in RELATED_SKILLS_MAP[cand_norm]:
            if rel_target.lower() == target_norm.lower():
                return (rel_desc, credit)
    return None

