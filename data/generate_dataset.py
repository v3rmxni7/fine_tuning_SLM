import json
import random
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.config import EXTRACTION_INSTRUCTION

random.seed(42)

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Daniel", "Lisa", "Matthew", "Nancy",
    "Anthony", "Betty", "Mark", "Margaret", "Andrew", "Sandra", "Steven", "Ashley",
    "Paul", "Emily", "Joshua", "Donna", "Kenneth", "Michelle", "Kevin", "Carol",
    "Brian", "Amanda", "George", "Melissa", "Timothy", "Deborah", "Ronald", "Stephanie",
    "Edward", "Rebecca", "Jason", "Sharon", "Jeffrey", "Laura", "Ryan", "Cynthia",
    "Aisha", "Raj", "Priya", "Wei", "Yuki", "Carlos", "Fatima", "Omar",
    "Sophia", "Liam", "Olivia", "Noah", "Emma", "Aiden", "Ava", "Lucas",
    "Mia", "Ethan", "Isabella", "Mason", "Zara", "Arjun", "Mei", "Hassan",
    "Elena", "Viktor", "Amara", "Kenji", "Leila", "Diego", "Nadia", "Sven",
    "Rina", "Pavel", "Ingrid", "Tao", "Aaliya", "Felix", "Clara", "Hugo",
    "Vera", "Oscar", "Nina", "Leo", "Iris", "Max", "Ada", "Sam",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen",
    "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera",
    "Campbell", "Mitchell", "Carter", "Roberts", "Patel", "Kumar", "Singh", "Chen",
    "Wang", "Zhang", "Tanaka", "Yamamoto", "Kim", "Park", "Ali", "Khan",
    "Ivanov", "Mueller", "Schmidt", "Fischer", "Weber", "Eriksson", "Johansson",
    "Dubois", "Bernard", "Silva", "Santos", "Costa", "Ferreira", "Rossi", "Russo",
]

TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust", "Ruby",
    "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL", "Redis", "Elasticsearch",
    "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "PyTorch", "TensorFlow",
    "Data Analysis", "Pandas", "NumPy", "Scikit-learn", "Apache Spark", "Airflow",
    "Git", "Linux", "REST APIs", "GraphQL", "Microservices", "System Design",
    "Agile", "Scrum", "JIRA",
]

ROLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Engineer",
    "Data Scientist", "Senior Data Scientist", "ML Engineer",
    "Frontend Developer", "Backend Developer", "Full Stack Developer",
    "DevOps Engineer", "Cloud Architect", "Site Reliability Engineer",
    "Product Manager", "Engineering Manager", "Tech Lead",
    "Data Analyst", "Business Analyst", "QA Engineer",
    "Mobile Developer", "iOS Developer", "Android Developer",
    "Data Engineer", "Senior Data Engineer", "Platform Engineer",
    "Security Engineer", "Solutions Architect", "AI Researcher",
    "UX Designer", "Technical Writer", "Scrum Master",
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Uber", "Airbnb",
    "Stripe", "Shopify", "Salesforce", "Adobe", "Intel", "Nvidia", "Tesla",
    "Twitter", "LinkedIn", "Spotify", "Snap", "Pinterest", "Dropbox", "Slack",
    "Palantir", "Databricks", "Snowflake", "MongoDB Inc", "Elastic", "Confluent",
    "TechCorp", "DataFlow Inc", "CloudBase", "InnovateTech", "NexGen Solutions",
    "Accenture", "Deloitte", "McKinsey", "BCG", "IBM", "Oracle", "SAP",
]

EDUCATION = [
    "Bachelor's in Computer Science", "Master's in Computer Science",
    "Bachelor's in Engineering", "Master's in Engineering",
    "Bachelor's in Mathematics", "Master's in Data Science",
    "Bachelor's in Information Technology", "Master's in AI",
    "PhD in Computer Science", "PhD in Machine Learning",
    "Bachelor's in Business Administration", "MBA",
    "Bachelor's in Electrical Engineering", "Master's in Software Engineering",
    "Bachelor's in Statistics", "Master's in Applied Mathematics",
]

UNIVERSITIES = [
    "MIT", "Stanford", "Carnegie Mellon", "UC Berkeley", "Harvard",
    "Georgia Tech", "Caltech", "University of Michigan", "Cornell",
    "University of Washington", "UT Austin", "UIUC", "Columbia",
    "UCLA", "Princeton", "University of Toronto", "Oxford", "Cambridge",
    "ETH Zurich", "IIT Delhi", "IIT Bombay", "NUS", "Tsinghua University",
]

EXPERIENCE_YEARS = [
    "1 year", "2 years", "3 years", "4 years", "5 years",
    "6 years", "7 years", "8 years", "10 years", "12 years", "15 years",
    "1+ years", "2+ years", "3+ years", "5+ years", "7+ years", "10+ years",
]

PRODUCT_TYPES = [
    ("laptop", ["UltraBook", "ProBook", "AirBook", "ThinkPad", "EliteBook", "ZenBook", "SwiftBook"]),
    ("phone", ["Galaxy", "Pixel", "OnePlus", "Nova", "Redmi", "Xperia", "Moto"]),
    ("headphone", ["AirPods", "SoundMax", "BassPro", "QuietComfort", "FreeBuds", "WH-1000"]),
    ("monitor", ["UltraSharp", "ProDisplay", "ViewFine", "CrystalView", "PixelPerfect"]),
    ("keyboard", ["MechPro", "KeyCraft", "TypeMaster", "SilentKey", "RapidType"]),
    ("tablet", ["iPad", "Tab", "Surface", "MatePad", "Galaxy Tab", "Pixel Slate"]),
]

BRANDS = [
    "TechCorp", "NovaTech", "EliteTech", "PrimeTech", "CoreTech",
    "Samsung", "Sony", "LG", "Dell", "HP", "Lenovo", "Asus", "Acer",
    "Logitech", "Razer", "Bose", "JBL", "Anker", "Belkin",
]

PRODUCT_FEATURES_MAP = {
    "laptop": ["16GB RAM", "32GB RAM", "8GB RAM", "512GB SSD", "1TB SSD", "256GB SSD",
               "Intel i7", "Intel i9", "AMD Ryzen 7", "AMD Ryzen 9", "M2 chip", "M3 chip",
               "14-inch display", "15.6-inch display", "13-inch display", "OLED display",
               "backlit keyboard", "fingerprint reader", "Thunderbolt 4", "Wi-Fi 6E"],
    "phone": ["128GB storage", "256GB storage", "512GB storage", "6.5-inch AMOLED",
              "6.1-inch display", "5G connectivity", "48MP camera", "108MP camera",
              "50MP camera", "5000mAh battery", "4500mAh battery", "fast charging",
              "wireless charging", "water resistant", "Face ID", "under-display fingerprint"],
    "headphone": ["noise cancelling", "40-hour battery", "30-hour battery", "20-hour battery",
                  "Bluetooth 5.3", "Bluetooth 5.0", "Hi-Res Audio", "spatial audio",
                  "built-in microphone", "touch controls", "foldable design", "IPX4 water resistant"],
    "monitor": ["27-inch 4K", "32-inch 4K", "24-inch FHD", "34-inch ultrawide",
                "144Hz refresh rate", "165Hz refresh rate", "60Hz refresh rate",
                "IPS panel", "OLED panel", "VA panel", "HDR10", "USB-C hub",
                "adjustable stand", "built-in speakers", "blue light filter"],
    "keyboard": ["mechanical switches", "wireless", "Bluetooth", "RGB backlight",
                 "hot-swappable keys", "N-key rollover", "USB-C charging",
                 "compact 65%", "full-size", "TKL layout", "ergonomic design",
                 "programmable keys", "aluminum frame", "PBT keycaps"],
    "tablet": ["10.9-inch display", "11-inch display", "12.9-inch display",
               "128GB storage", "256GB storage", "M1 chip", "Snapdragon 8 Gen 2",
               "stylus support", "keyboard compatible", "5G optional",
               "Face ID", "fingerprint unlock", "quad speakers", "10-hour battery"],
}

COLORS = ["black", "silver", "white", "space gray", "midnight blue", "rose gold",
          "gold", "green", "red", "navy", "graphite", "starlight", "purple"]

PRICES = {
    "laptop": (599, 2499),
    "phone": (299, 1399),
    "headphone": (49, 449),
    "monitor": (199, 1299),
    "keyboard": (39, 249),
    "tablet": (329, 1599),
}

BIO_INTERESTS = [
    "growth hacking", "brand strategy", "digital marketing", "product innovation",
    "data-driven decisions", "team building", "startup culture", "open source",
    "AI ethics", "cloud architecture", "developer experience", "technical writing",
    "mentoring", "public speaking", "system design", "distributed systems",
    "fintech", "healthtech", "edtech", "sustainability", "blockchain",
]


def _gen_resume(omit_field=False):
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    role = random.choice(ROLES)
    exp = random.choice(EXPERIENCE_YEARS)
    skills = random.sample(TECH_SKILLS, random.randint(2, 5))
    edu_degree = random.choice(EDUCATION)
    edu_uni = random.choice(UNIVERSITIES)
    education = f"{edu_degree} from {edu_uni}"

    output = {
        "name": name,
        "role": role,
        "experience": exp,
        "skills": skills,
        "education": education,
    }

    omit_key = None
    if omit_field and random.random() < 0.1:
        omit_candidates = ["education", "experience"]
        omit_key = random.choice(omit_candidates)
        output[omit_key] = None

    templates = _resume_templates(name, role, exp, skills, education, omit_key)
    text = random.choice(templates)

    return text, output


def _resume_templates(name, role, exp, skills, education, omit_key=None):
    skills_str = ", ".join(skills[:-1]) + f" and {skills[-1]}" if len(skills) > 1 else skills[0]
    skills_comma = ", ".join(skills)

    templates = []

    if omit_key == "education":
        templates.extend([
            f"{name} is a {role.lower()} with {exp} of experience. Skilled in {skills_str}.",
            f"{name} works as a {role}. With {exp} of professional experience, they specialize in {skills_str}.",
            f"Meet {name}, a {role.lower()} who has been in the industry for {exp}. Their expertise includes {skills_str}.",
        ])
    elif omit_key == "experience":
        templates.extend([
            f"{name} is a {role.lower()} specializing in {skills_str}. Graduated with a {education}.",
            f"{name}, {role} | Skills: {skills_comma} | Education: {education}",
        ])
    else:
        templates.extend([
            f"{name} is a {role.lower()} with {exp} of experience. Skilled in {skills_str}. Holds a {education}.",
            f"{name} works as a {role}. With {exp} of professional experience, they specialize in {skills_str}. Education: {education}.",
            f"Meet {name}, a {role.lower()} who has been in the industry for {exp}. Their expertise includes {skills_str}. They completed their {education}.",
            f"{name} | {role} | {exp} experience | Skills: {skills_comma} | {education}",
            f"Professional profile: {name} is an experienced {role.lower()} ({exp}) proficient in {skills_str}. Academic background: {education}.",
            f"With {exp} in the field, {name} serves as a {role}. Core competencies: {skills_str}. Educational qualification: {education}.",
            f"{name} has {exp} of experience as a {role.lower()}. Technical skills include {skills_str}. Graduated with a {education}.",
            f"As a {role.lower()}, {name} brings {exp} of hands-on experience in {skills_str}. Academic credentials: {education}.",
            f"{name} is currently working as a {role}. Over the past {exp}, they have developed expertise in {skills_str}. They hold a {education}.",
            f"Experienced {role.lower()} {name} has spent {exp} working with {skills_str}. Educational background includes a {education}.",
        ])

    random.shuffle(templates)
    return templates


def _gen_product():
    ptype, pnames = random.choice(PRODUCT_TYPES)
    model_suffix = random.choice(["X1", "Pro", "Max", "Ultra", "S", "Plus", "Lite", "SE", "Air", "Elite", "Z", "V2", "Neo"])
    product_name = f"{random.choice(pnames)} {model_suffix}"
    brand = random.choice(BRANDS)
    price_range = PRICES[ptype]
    price = f"${random.randint(price_range[0], price_range[1])}"
    features = random.sample(PRODUCT_FEATURES_MAP[ptype], random.randint(3, 5))
    colors = random.sample(COLORS, random.randint(2, 4))

    output = {
        "product_name": product_name,
        "brand": brand,
        "price": price,
        "features": features,
        "colors": colors,
    }

    templates = _product_templates(product_name, brand, price, features, colors, ptype)
    text = random.choice(templates)
    return text, output


def _product_templates(name, brand, price, features, colors, ptype):
    feat_str = ", ".join(features[:-1]) + f" and {features[-1]}" if len(features) > 1 else features[0]
    color_str = ", ".join(colors[:-1]) + f" and {colors[-1]}" if len(colors) > 1 else colors[0]
    feat_comma = ", ".join(features)

    templates = [
        f"The {name} is a {ptype} by {brand} priced at {price}. It features {feat_str}. Available in {color_str}.",
        f"Introducing the {name} from {brand}. This {ptype} comes with {feat_str} at just {price}. Color options: {color_str}.",
        f"{brand}'s {name} {ptype} ({price}) offers {feat_str}. Choose from {color_str}.",
        f"The {brand} {name} is a premium {ptype} available for {price}. Key specs: {feat_comma}. Colors: {color_str}.",
        f"Looking for a new {ptype}? The {name} by {brand} features {feat_str} and is available in {color_str}. Retail price: {price}.",
        f"Product: {name} | Brand: {brand} | Type: {ptype} | Price: {price} | Features: {feat_comma} | Colors: {color_str}",
        f"The {name} ({brand}) is a top-rated {ptype}. For {price}, you get {feat_str}. It comes in {color_str}.",
        f"{brand} releases the {name}, a {ptype} priced at {price} with {feat_str}. Available colors include {color_str}.",
    ]
    random.shuffle(templates)
    return templates


def _gen_bio(omit_field=False):
    name_given = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    role = random.choice(ROLES)
    company = random.choice(COMPANIES)
    prev_companies = random.sample([c for c in COMPANIES if c != company], random.randint(1, 2))
    exp = random.choice(EXPERIENCE_YEARS)
    skills = random.sample(BIO_INTERESTS + random.sample(TECH_SKILLS, 3), random.randint(2, 4))
    edu_degree = random.choice(["MBA", "MS", "BS", "PhD"])
    edu_uni = random.choice(UNIVERSITIES)
    education = f"{edu_degree} from {edu_uni}"

    # ~30% of bios omit the name (common on LinkedIn)
    include_name = random.random() > 0.3

    output = {
        "name": name_given if include_name else None,
        "role": role,
        "company": company,
        "previous_companies": prev_companies,
        "experience": exp,
        "skills": skills,
        "education": education,
    }

    templates = _bio_templates(name_given if include_name else None, role, company, prev_companies, exp, skills, education)
    text = random.choice(templates)
    return text, output


def _bio_templates(name, role, company, prev_companies, exp, skills, education):
    prev_str = ", ".join(prev_companies)
    ex_str = " | ".join([f"Ex-{c}" for c in prev_companies])
    skills_str = ", ".join(skills[:-1]) + f" and {skills[-1]}" if len(skills) > 1 else skills[0]
    skills_comma = ", ".join(skills)

    name_part = f"{name} | " if name else ""

    templates = [
        f"{name_part}{role} at {company} | {ex_str} | {education} | Passionate about {skills_str} | {exp} in the industry",
        f"{name_part}{role} @ {company}. Previously at {prev_str}. {exp} of experience in {skills_str}. {education}.",
        f"{name_part}Currently {role} at {company}. Former {prev_str}. Focused on {skills_str}. Education: {education}. {exp} experience.",
        f"{name_part}{role} | {company} | {exp} experience | Skills: {skills_comma} | Previously: {prev_str} | {education}",
        f"{name_part}Driving {skills_str} at {company} as {role}. {exp} track record. Prior: {prev_str}. {education}.",
        f"{name_part}{role} at {company} with {exp} of experience. Background in {skills_str}. Alumni of {education.split(' from ')[1] if ' from ' in education else education}. Previously worked at {prev_str}.",
    ]
    random.shuffle(templates)
    return templates


def generate_dataset(n_resume=500, n_product=300, n_bio=200):
    samples = []

    for _ in range(n_resume):
        text, output = _gen_resume(omit_field=True)
        samples.append({
            "instruction": EXTRACTION_INSTRUCTION,
            "input": text,
            "output": json.dumps(output),
            "category": "resume",
        })

    for _ in range(n_product):
        text, output = _gen_product()
        samples.append({
            "instruction": EXTRACTION_INSTRUCTION,
            "input": text,
            "output": json.dumps(output),
            "category": "product",
        })

    for _ in range(n_bio):
        text, output = _gen_bio(omit_field=True)
        samples.append({
            "instruction": EXTRACTION_INSTRUCTION,
            "input": text,
            "output": json.dumps(output),
            "category": "bio",
        })

    random.shuffle(samples)
    return samples


def split_dataset(samples, train_ratio=0.8, val_ratio=0.1):
    n = len(samples)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    return samples[:train_end], samples[train_end:val_end], samples[val_end:]


def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} samples to {path}")


def main():
    print("Generating synthetic dataset...")
    samples = generate_dataset()
    print(f"Total samples: {len(samples)}")

    # Validate all outputs are valid JSON
    invalid = 0
    for s in samples:
        try:
            json.loads(s["output"])
        except json.JSONDecodeError:
            invalid += 1
    print(f"JSON validation: {len(samples) - invalid}/{len(samples)} valid ({invalid} invalid)")

    # Split
    train, val, test = split_dataset(samples)
    print(f"Split: train={len(train)}, val={len(val)}, test={len(test)}")

    # Save
    save_json(samples, "data/raw/generated_1000.json")
    save_json(train, "data/processed/train.json")
    save_json(val, "data/processed/val.json")
    save_json(test, "data/processed/test.json")

    # Save sample (first 50)
    save_json(samples[:50], "data/sample_dataset.json")

    # Print stats
    categories = {}
    for s in samples:
        cat = s["category"]
        categories[cat] = categories.get(cat, 0) + 1
    print(f"Category distribution: {categories}")

    # Print 3 examples
    print("\n--- Sample Examples ---")
    for i, s in enumerate(samples[:3]):
        print(f"\n[{i+1}] Category: {s['category']}")
        print(f"Input: {s['input'][:120]}...")
        print(f"Output: {s['output'][:120]}...")


if __name__ == "__main__":
    main()
