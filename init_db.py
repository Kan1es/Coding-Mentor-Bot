"""Initialize database with sample data."""
import asyncio
import json
from database.db import Database


async def load_challenges():
    """Load challenges from JSON file into database."""
    db = Database()
    await db.init_db()
    
    with open('data/challenges.json', 'r', encoding='utf-8') as f:
        challenges = json.load(f)
    
    for challenge in challenges:
        await db.add_challenge(
            title=challenge['title'],
            description=challenge['description'],
            difficulty=challenge['difficulty'],
            language=challenge['language'],
            test_cases=challenge['test_cases'],
            solution=challenge['solution'],
            points=challenge['points']
        )
    
    print(f"✅ Loaded {len(challenges)} challenges")


async def load_interview_questions():
    """Load interview questions from JSON file into database."""
    db = Database()
    
    with open('data/interview_questions.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    for question in questions:
        await db.add_interview_question(
            category=question['category'],
            question=question['question'],
            answer=question['answer'],
            difficulty=question['difficulty']
        )
    
    print(f"✅ Loaded {len(questions)} interview questions")


async def main():
    """Main initialization function."""
    print("🚀 Initializing database with sample data...")
    
    await load_challenges()
    await load_interview_questions()
    
    print("✅ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())
