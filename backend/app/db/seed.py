"""
Seed database with initial data:
- 10 personality traits
- 50 test questions (5 per trait)
- 20 sample idol profiles
"""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine, Base
from app.models import Trait, Question, Idol


def create_traits(db: Session):
    """Create initial personality traits."""
    traits_data = [
        {
            "name": "Strategic Thinking",
            "description": "Ability to plan ahead and think analytically",
            "high_behavior": "Plans multiple steps ahead, analytical, considers long-term consequences",
            "low_behavior": "Prefers spontaneity, focuses on present moment, intuitive decision-making"
        },
        {
            "name": "Execution & Discipline",
            "description": "Drive to complete tasks and maintain consistent effort",
            "high_behavior": "Highly organized, follows through on commitments, detail-oriented",
            "low_behavior": "Flexible approach, adapts plans as needed, comfortable with ambiguity"
        },
        {
            "name": "Creativity",
            "description": "Innovative thinking and artistic expression",
            "high_behavior": "Generates novel ideas, thinks outside the box, artistic inclination",
            "low_behavior": "Prefers proven methods, practical approach, values consistency"
        },
        {
            "name": "Emotional Sensitivity",
            "description": "Awareness and responsiveness to emotions",
            "high_behavior": "Deeply attuned to feelings, empathetic, emotionally expressive",
            "low_behavior": "Logical approach, maintains composure, objective perspective"
        },
        {
            "name": "Social Influence",
            "description": "Ability to persuade and inspire others",
            "high_behavior": "Charismatic, persuasive, enjoys leading groups",
            "low_behavior": "Prefers supporting roles, values independence, low-key presence"
        },
        {
            "name": "Adaptability",
            "description": "Comfort with change and uncertainty",
            "high_behavior": "Thrives in dynamic environments, embraces change, flexible mindset",
            "low_behavior": "Values stability, prefers routine, methodical approach"
        },
        {
            "name": "Persistence",
            "description": "Determination to overcome obstacles",
            "high_behavior": "Never gives up, resilient through setbacks, strong willpower",
            "low_behavior": "Knows when to pivot, realistic about limitations, conserves energy"
        },
        {
            "name": "Risk-Taking",
            "description": "Willingness to take chances",
            "high_behavior": "Bold decisions, comfortable with uncertainty, seeks adventure",
            "low_behavior": "Cautious approach, values security, calculated decisions"
        },
        {
            "name": "Empathy",
            "description": "Understanding and sharing others' feelings",
            "high_behavior": "Deeply caring, puts others first, strong emotional connection",
            "low_behavior": "Maintains boundaries, self-focused, logical relationships"
        },
        {
            "name": "Optimism",
            "description": "Positive outlook and hopefulness",
            "high_behavior": "Sees opportunities, maintains positive attitude, hopeful about future",
            "low_behavior": "Realistic expectations, prepares for challenges, pragmatic view"
        }
    ]

    traits = []
    for trait_data in traits_data:
        trait = Trait(**trait_data)
        db.add(trait)
        traits.append(trait)

    db.commit()
    print(f"✓ Created {len(traits)} traits")
    return traits


def create_questions(db: Session, traits):
    """Create test questions for each trait."""
    questions_data = [
        # Strategic Thinking (trait 1)
        {"text": "I prefer to plan things well in advance rather than deciding at the last minute.", "reverse": False},
        {"text": "I often think about how my current actions will affect my future.", "reverse": False},
        {"text": "I make decisions based on careful analysis rather than gut feeling.", "reverse": False},
        {"text": "I enjoy solving complex problems that require strategic thinking.", "reverse": False},
        {"text": "I prefer to live in the moment without worrying about long-term plans.", "reverse": True},

        # Execution & Discipline (trait 2)
        {"text": "I always finish what I start, no matter how long it takes.", "reverse": False},
        {"text": "I maintain a consistent daily routine and stick to my schedule.", "reverse": False},
        {"text": "I pay close attention to small details in my work.", "reverse": False},
        {"text": "I find it easy to stay focused on tasks until they're complete.", "reverse": False},
        {"text": "I often leave projects unfinished when they become challenging.", "reverse": True},

        # Creativity (trait 3)
        {"text": "I frequently come up with new and original ideas.", "reverse": False},
        {"text": "I enjoy activities that allow me to express myself artistically.", "reverse": False},
        {"text": "I prefer unconventional solutions over traditional approaches.", "reverse": False},
        {"text": "I find it easy to think outside the box when solving problems.", "reverse": False},
        {"text": "I prefer to follow established methods rather than experiment.", "reverse": True},

        # Emotional Sensitivity (trait 4)
        {"text": "I am deeply affected by the emotions of people around me.", "reverse": False},
        {"text": "I find it easy to cry during emotional moments in movies or books.", "reverse": False},
        {"text": "I often notice subtle changes in other people's moods.", "reverse": False},
        {"text": "I express my emotions openly and freely.", "reverse": False},
        {"text": "I rarely let emotions influence my decisions.", "reverse": True},

        # Social Influence (trait 5)
        {"text": "I enjoy taking charge and leading group projects.", "reverse": False},
        {"text": "People often look to me for guidance and direction.", "reverse": False},
        {"text": "I find it easy to persuade others to see my point of view.", "reverse": False},
        {"text": "I am comfortable being the center of attention.", "reverse": False},
        {"text": "I prefer to work independently rather than lead a team.", "reverse": True},

        # Adaptability (trait 6)
        {"text": "I adjust easily when plans change unexpectedly.", "reverse": False},
        {"text": "I thrive in unpredictable and dynamic environments.", "reverse": False},
        {"text": "I am comfortable making decisions with incomplete information.", "reverse": False},
        {"text": "I embrace new experiences and changes enthusiastically.", "reverse": False},
        {"text": "I prefer familiar routines over trying new things.", "reverse": True},

        # Persistence (trait 7)
        {"text": "I never give up on my goals, even when faced with obstacles.", "reverse": False},
        {"text": "I view setbacks as temporary challenges to overcome.", "reverse": False},
        {"text": "I maintain my effort even when results are slow to appear.", "reverse": False},
        {"text": "I am known for my determination and resilience.", "reverse": False},
        {"text": "I tend to give up when things become too difficult.", "reverse": True},

        # Risk-Taking (trait 8)
        {"text": "I enjoy taking chances even when the outcome is uncertain.", "reverse": False},
        {"text": "I often make bold decisions that others might consider risky.", "reverse": False},
        {"text": "I prefer adventure and excitement over safety and security.", "reverse": False},
        {"text": "I am willing to take financial or personal risks for potential rewards.", "reverse": False},
        {"text": "I always choose the safe and predictable option.", "reverse": True},

        # Empathy (trait 9)
        {"text": "I deeply care about the wellbeing of others.", "reverse": False},
        {"text": "I often put other people's needs before my own.", "reverse": False},
        {"text": "I can easily understand how others are feeling.", "reverse": False},
        {"text": "I go out of my way to help people in need.", "reverse": False},
        {"text": "I prioritize my own needs over the feelings of others.", "reverse": True},

        # Optimism (trait 10)
        {"text": "I generally expect things to work out well in the end.", "reverse": False},
        {"text": "I focus on the positive aspects of any situation.", "reverse": False},
        {"text": "I believe that good things are always on the horizon.", "reverse": False},
        {"text": "I maintain a hopeful attitude even during difficult times.", "reverse": False},
        {"text": "I tend to expect the worst when facing uncertainty.", "reverse": True},
    ]

    questions = []
    for i, q_data in enumerate(questions_data):
        trait_index = i // 5  # 5 questions per trait
        question = Question(
            text=q_data["text"],
            trait_id=traits[trait_index].id,
            reverse_scored=q_data["reverse"],
            order_index=i + 1
        )
        db.add(question)
        questions.append(question)

    db.commit()
    print(f"✓ Created {len(questions)} questions")
    return questions


def create_idols(db: Session, traits):
    """Create sample idol profiles with trait scores."""
    idols_data = [
        {
            "name": "Taylor Swift",
            "description": "Singer-songwriter known for storytelling and business acumen",
            "scores": [85, 90, 95, 80, 85, 70, 90, 65, 85, 75]
        },
        {
            "name": "Beyoncé",
            "description": "Performer known for perfectionism and stage presence",
            "scores": [90, 95, 85, 75, 95, 80, 95, 70, 80, 85]
        },
        {
            "name": "Elon Musk",
            "description": "Entrepreneur focused on innovation and ambitious goals",
            "scores": [95, 80, 90, 40, 90, 85, 100, 95, 50, 80]
        },
        {
            "name": "Oprah Winfrey",
            "description": "Media mogul known for empathy and influence",
            "scores": [85, 90, 75, 95, 95, 85, 90, 70, 100, 90]
        },
        {
            "name": "Stephen Curry",
            "description": "Basketball player known for work ethic and team play",
            "scores": [80, 95, 70, 70, 75, 75, 95, 65, 85, 85]
        },
        {
            "name": "BTS (RM)",
            "description": "K-pop leader known for wisdom and authenticity",
            "scores": [85, 85, 90, 85, 80, 80, 85, 60, 90, 80]
        },
        {
            "name": "Serena Williams",
            "description": "Tennis champion known for competitive drive",
            "scores": [85, 95, 70, 75, 85, 75, 100, 75, 75, 85]
        },
        {
            "name": "Keanu Reeves",
            "description": "Actor known for humility and kindness",
            "scores": [70, 80, 75, 80, 50, 85, 85, 40, 95, 75]
        },
        {
            "name": "Lady Gaga",
            "description": "Artist known for creativity and authenticity",
            "scores": [75, 85, 100, 90, 90, 85, 90, 85, 95, 75]
        },
        {
            "name": "LeBron James",
            "description": "Basketball player and businessman",
            "scores": [90, 90, 75, 70, 95, 80, 95, 70, 85, 85]
        },
        {
            "name": "Emma Watson",
            "description": "Actress and activist for social causes",
            "scores": [85, 85, 75, 85, 80, 75, 85, 60, 95, 80]
        },
        {
            "name": "Dwayne Johnson",
            "description": "Actor and entrepreneur known for work ethic",
            "scores": [80, 100, 70, 65, 90, 80, 100, 70, 85, 95]
        },
        {
            "name": "Zendaya",
            "description": "Actress and fashion icon",
            "scores": [75, 85, 85, 80, 80, 90, 85, 70, 90, 80]
        },
        {
            "name": "Steve Jobs (legacy)",
            "description": "Apple co-founder known for vision and perfectionism",
            "scores": [100, 85, 100, 60, 95, 70, 100, 95, 55, 85]
        },
        {
            "name": "Malala Yousafzai",
            "description": "Education activist and Nobel laureate",
            "scores": [85, 90, 75, 85, 85, 75, 100, 75, 100, 85]
        },
        {
            "name": "Ryan Reynolds",
            "description": "Actor known for humor and creativity",
            "scores": [75, 80, 95, 70, 85, 90, 80, 75, 80, 90]
        },
        {
            "name": "Simone Biles",
            "description": "Gymnast known for excellence and mental health advocacy",
            "scores": [85, 100, 80, 85, 75, 85, 95, 80, 90, 80]
        },
        {
            "name": "Chris Hemsworth",
            "description": "Actor known for dedication and family values",
            "scores": [70, 90, 70, 75, 75, 80, 85, 65, 85, 90]
        },
        {
            "name": "Rihanna",
            "description": "Singer and entrepreneur",
            "scores": [85, 85, 95, 75, 90, 95, 85, 85, 80, 85]
        },
        {
            "name": "Tom Hanks",
            "description": "Actor known for kindness and relatability",
            "scores": [75, 85, 75, 85, 70, 80, 85, 50, 100, 90]
        }
    ]

    idols = []
    for idol_data in idols_data:
        # Create trait_scores dict mapping trait_id to score
        trait_scores = {
            str(traits[i].id): score
            for i, score in enumerate(idol_data["scores"])
        }

        idol = Idol(
            name=idol_data["name"],
            description=idol_data["description"],
            image_url=f"https://via.placeholder.com/300x400?text={idol_data['name'].replace(' ', '+')}",
            trait_scores=trait_scores
        )
        db.add(idol)
        idols.append(idol)

    db.commit()
    print(f"✓ Created {len(idols)} idol profiles")
    return idols


def seed_database():
    """Main function to seed the database."""
    print("Starting database seed...")

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Created database tables")

    # Create session
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_traits = db.query(Trait).count()
        if existing_traits > 0:
            print("⚠ Database already contains data. Skipping seed.")
            return

        # Seed data
        traits = create_traits(db)
        questions = create_questions(db, traits)
        idols = create_idols(db, traits)

        print("\n✅ Database seeding completed successfully!")
        print(f"   - {len(traits)} traits")
        print(f"   - {len(questions)} questions")
        print(f"   - {len(idols)} idols")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
