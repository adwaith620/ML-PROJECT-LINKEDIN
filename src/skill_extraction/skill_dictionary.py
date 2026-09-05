"""
skill_dictionary.py

Contains canonical lists of skills, technologies, and entities.
Also defines alias mappings for normalization.
"""

PROGRAMMING_LANGUAGES = [
    "Python", "JavaScript", "Java", "C++", "C#", "C", "Ruby", "Go", 
    "Swift", "Kotlin", "TypeScript", "PHP", "Rust", "Scala", "R", "Dart"
]

FRAMEWORKS_AND_LIBRARIES = [
    "React", "Angular", "Vue.js", "Django", "Flask", "Spring Boot", 
    "Ruby on Rails", "Express.js", "Node.js", "TensorFlow", "PyTorch", 
    "Keras", "Scikit-Learn", "Pandas", "NumPy", "FastAPI", ".NET", "Flutter"
]

DATABASES = [
    "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Microsoft SQL Server", 
    "Redis", "Cassandra", "Elasticsearch", "DynamoDB", "Firebase", "Neo4j"
]

CLOUD_AND_DEVOPS = [
    "AWS", "Amazon Web Services", "Microsoft Azure", "Google Cloud Platform", "GCP", 
    "Docker", "Kubernetes", "Jenkins", "GitLab CI/CD", "GitHub Actions", 
    "Terraform", "Ansible", "Linux"
]

DEVELOPER_TOOLS = [
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Postman", 
    "Webpack", "Babel", "npm", "Yarn"
]

CERTIFICATIONS = [
    "AWS Certified Solutions Architect", "Certified Kubernetes Administrator", 
    "Cisco Certified Network Associate", "CCNA", "CompTIA Security+", 
    "Project Management Professional", "PMP", "Certified ScrumMaster", "CSM"
]

JOB_ROLES = [
    "Software Engineer", "Backend Developer", "Frontend Developer", 
    "Full Stack Developer", "Data Scientist", "Machine Learning Engineer", 
    "DevOps Engineer", "Data Engineer", "Product Manager", "UI/UX Designer",
    "Systems Analyst", "Database Administrator", "Cloud Architect"
]

EDUCATION_DEGREES = [
    "Bachelor of Science", "B.S.", "BS", "Bachelor of Arts", "B.A.", "BA",
    "Master of Science", "M.S.", "MS", "Master of Business Administration", "MBA",
    "Doctor of Philosophy", "Ph.D.", "PhD"
]

# Alias mapping: lowercase surface form -> Canonical Name
ALIAS_MAP = {
    # Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "py": "Python",
    "python": "Python",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "c-sharp": "C#",
    "csharp": "C#",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "golang": "Go",
    "go": "Go",
    
    # Frameworks
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    
    # DBs
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "sql server": "Microsoft SQL Server",
    
    # Cloud
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes"
}

def get_all_skills():
    """Returns a flat list of all canonical technical skills."""
    return (PROGRAMMING_LANGUAGES + FRAMEWORKS_AND_LIBRARIES + 
            DATABASES + CLOUD_AND_DEVOPS + DEVELOPER_TOOLS)
